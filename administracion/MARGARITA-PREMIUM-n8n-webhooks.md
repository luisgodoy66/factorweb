# Margarita — Plan Premium con Automatizaciones n8n
## Opciones omitidas, catálogo de webhooks y diseño comercial

**Documento técnico-comercial** · Sistema evaluado: **Margarita v2.11** (`factorweb`, Django 5.1.5 + PostgreSQL)
**Alcance:** 10 apps Django · 79 modelos · ~40 procedimientos almacenados · 19 integraciones · 6 dominios de negocio
**Plan base de referencia:** **USD 300 / mes**
**Fecha de análisis:** generado a partir de la inspección directa del código fuente en `E:\Django\margaritaenv\factorweb`

---

## 0. Resumen ejecutivo

Margarita es un sistema de factoring **funcionalmente profundo y comercialmente incompleto**. En cobertura de negocio está por encima del promedio del mercado ecuatoriano: maneja el ciclo completo (solicitud → aprobación por Slack → liquidación → desembolso → cobranza → protesto → contabilidad → facturación electrónica → estados financieros), con factoring con y sin recurso, cheques accesorios, pagarés por reestructuración, cuentas conjuntas, cortes históricos y revisiones de cartera. Ese núcleo es el activo.

El problema no es de funcionalidad transaccional, es de **automatización, integración y control**. Tres hallazgos estructurales lo resumen:

1. **No existe ningún planificador de tareas.** Cero coincidencias de `celery`, `crontab`, `apscheduler`, `django-cron` o `management/commands` en el código del proyecto. Todo lo que debería ocurrir solo —cierre de mes, generación de asientos, facturas al vencimiento, recordatorios de mora, cálculo de provisiones, cortes de cartera— es un **botón que un humano debe presionar**. El sistema no tiene reloj.
2. **No existe ninguna notificación saliente.** Hay `slack_sdk`, `twilio` y configuración SMTP en la base de datos, pero **cero `send_mail`** en todo el proyecto. El cliente nunca se entera de que su solicitud fue aprobada, de que se desembolsó, de que su factura venció o de que se le protestó un cheque. Peor: el campo `Clientes.ctcelular` está etiquetado **"WhatsApp"** en el formulario y existe `Twilio_whatsapp` como bitácora, pero el envío solo ocurre cuando un cobrador lo dispara a mano desde una gestión de cobro.
3. **No existe ningún concepto de plan, suscripción o facturación.** Solo hay tres campos huérfanos en `bases.Empresas`: `lgratis` (bool, default `True`), `nmaximooperaciones` (`SmallInteger`, default `10`) y `dfinpruebas` (fecha, se llena con `DIAS_PRUEBA_SISTEMA = 30`). **Ninguno de los tres se lee jamás para bloquear, cobrar o limitar nada.** El control comercial hoy es 100 % manual: alguien cambia `lbloqueada` a mano desde el admin.

**La conclusión estratégica:** el sistema no necesita que le agreguemos funciones de factoring —ya las tiene—. Necesita una **capa de automatización y de eventos** encima. Esa capa es exactamente lo que n8n provee, y es exactamente lo que justifica un plan premium.

La propuesta de este documento es vender esa capa como **Margarita Premium**, a **USD 690/mes** (2,3× el plan base), con un catálogo de **135 eventos de webhook** listos para conectar a workflows de n8n, y con la infraestructura de eventos (outbox, firma HMAC, reintentos, idempotencia) implementada en Django.

> **Estado de ejecución (26-jul-2026):** los **5 hallazgos críticos de seguridad** que este documento señalaba como condición previa no negociable **ya fueron corregidos y verificados** — ejecución de código arbitrario desde un formulario, tres endpoints `/api/*` anónimos, fuga multi-tenant de asientos contables, `DEBUG=True` en producción y webhooks entrantes sin verificación de firma. El detalle está en el anexo **8.6**. Con eso, el sistema ya está en condiciones de conectarse a un bus de eventos, y la Fase 0 del roadmap se reduce a construir la capa de webhooks salientes.

### Las 10 opciones omitidas de mayor impacto

| # | Omisión | Impacto de negocio | ¿Resoluble con n8n? |
|---|---|---|---|
| 1 | **Notificación de cesión al deudor sin envío ni acuse** | Riesgo legal: la cesión no oponible al deudor es una cesión débil. `Anexos.lcesionfacturas` solo genera un .docx que nadie envía. | Sí (P0) |
| 2 | **Sin notificaciones al cliente ni al deudor** | El 100 % del ciclo de vida es silencioso. Genera llamadas de "¿qué pasó con mi operación?" y desgasta la relación. | Sí (P0) |
| 3 | **Sin conciliación bancaria** | `lgeneradoarchivobanco` es un booleano. Nadie cruza el extracto contra lo registrado. | Parcial (P0) |
| 4 | **Sin KYC/AML ni listas de control** | `Datos_compradores` solo tiene `cxclase` y `cxestado`. No hay PEP, sanciones, ni verificación real de RUC. | Sí (P0) |
| 5 | **Sin validación efectiva de la factura en el SRI** | El chequeo en vivo está **comentado** en `solicitudes/forms.py:123-139` ("no hay acceso al servicio del SRI desde un hosting externo"). Solo se compara el prefijo de la clave de acceso. El XML/RIDE original no se guarda. | Sí — y ya hay un workflow n8n armado para esto |
| 6 | **Sin scoring de deudor** | La decisión se reduce a `Clases_cliente` + `cxestado`. `npromediodemoradepago` se carga pero solo se muestra. | Sí (P1) |
| 7 | **Sin promesas de pago** | `Gestion_cobro` no tiene fecha ni monto comprometido. El cobrador anota en un campo de texto libre. | Sí (P0) |
| 8 | **Sin escalamiento automático por mora** | La gestión de cobro se abre a mano, cliente por cliente. Si el cobrador no mira la lista, nadie cobra. | Sí (P0) |
| 9 | **Sin castigo de cartera ni NIIF 9** | `Documentos.lcastigada` y el estado `'C'` (cartera castigada) existen pero **ninguna vista los asigna**. `provision_cargos` es devengo de ingresos, no pérdida esperada. | No (requiere desarrollo) |
| 10 | **Sin retenciones automáticas** | `nretencioniva` / `nretencionrenta` se digitan a mano y no se contrastan con ningún comprobante del SRI. | Sí (P0) |

---

## 1. Inventario del sistema actual

### 1.1 Arquitectura

| Componente | Estado observado |
|---|---|
| Framework | Django 5.1.5, 10 apps propias + `django.contrib.*` |
| Base de datos | PostgreSQL en `69.62.68.116` (settings activo). `db.sqlite3` presente pero **no usado** |
| Lógica transaccional | ~40 **procedimientos almacenados** (`uspLiquidarAsignacion`, `uspAceptarCobranzaCartera`, `uspRegistroProtesto`, `uspAmpliacionDePlazo`, `uspBloquearMesContabilidad`, …) invocados vía `bases/views.py:62 enviarPost()` con SQL por concatenación `.format()` |
| Multi-tenant | Columna `empresa` en cada tabla vía `ClaseModelo` abstracto, **aislamiento solo por convención** en el queryset. Sin middleware, sin manager, sin RLS |
| Autenticación | `Usuario_empresa` (N:M usuario↔empresa). Mixin `SinPrivilegios` = `LoginRequiredMixin + PermissionRequiredMixin`. **Sin 2FA, sin grupos gestionados en código** |
| Configuración | `factorweb25/settings.py` es el módulo activo. **`DEBUG = True`** con `ALLOWED_HOSTS` de producción |
| Scheduler | **Ninguno.** Confirmado por grep: 0 coincidencias |
| Observabilidad | **Ninguna.** Sin `LOGGING`, sin Sentry, sin health-check; errores a `print()` |
| Reportes | 47 funciones `Impresion*` con **WeasyPrint** (PDF inline, **no se persiste ningún archivo**). Contratos con **docxtpl** (.docx generado y transmitido, tampoco se guarda) |

### 1.2 Módulos funcionales (lo que el sistema YA hace)

| Módulo | Cobertura observada |
|---|---|
| **Dashboard** | Cartera, protestos, pagarés, solicitudes pendientes, total negociado, ingreso acumulado del año. Vista "Ayer y hoy" |
| **Solicitudes / Negociación** | Facturas puras y con accesorios; carga manual, importación masiva JSON y carga automática por correo+XML vía webhook; ajuste de vencimientos por feriados (`pais.Feriados.llaborable`); niveles de aprobación por monto con votos requeridos; excesos temporales de línea |
| **Aprobaciones** | Integración **Slack** con botones interactivos: sube el PDF de liquidación, cuenta votos por nivel, aprueba al alcanzar `naprobadores`, y al rechazar ejecuta `uspreversaliquidacionasignacion` |
| **Clientes** | Solicitante → cliente; fichas natural y jurídica con representantes legales y vencimiento de cargos; socios y capital; líneas de factoring con histórico; cuentas bancarias con cuenta de transferencia por defecto; estados operativos (A/B/I/P/L/X/C) y clases |
| **Deudores** | Ficha del comprador, cupos por deudor con `lsenotifica`, cuentas bancarias de recaudo, reporte de últimas cobranzas |
| **Operaciones** | Cálculo de anticipo, GAO, descuento de cartera, otros cargos e IVA; condiciones operativas por tramos de plazo y clase; desembolso en efectivo/cheque/transferencia/movimiento contable; cheque garantía; anexos .docx con marca de cesión de facturas |
| **Cartera y riesgo** | Buckets de antigüedad (30/60/90/±90); `provision_cargos` con DC negociado, DC vencido, GAO adicional e IVA; revisión de cartera con clase/estado sugerido; cortes históricos con snapshots de 4 tablas |
| **Cobranzas** | Depósito de cheques; cobranza de cartera, cargos, cuotas y recuperaciones; confirmación y reversa; condonación de días; liquidación con GAO/GAOA/DC/DCV/retenciones/bajas/IVA/neto; liquidación en cero y en negativo |
| **Protestos** | Registro de protesto con motivo y responsabilidad del girador; recuperación total o parcial; reversa; reportes de protestos pendientes por corte y por deudor |
| **Cuentas conjuntas** | Cuenta del cliente en la empresa; confirmación de cobranzas depositadas; transferencias; débitos con y sin cobranza; movimientos |
| **Ampliaciones de plazo** | Prórroga con comisión, descuento de cartera e IVA; cálculo de cargos; reversa |
| **Pagarés** | Reestructuración de cartera por XML con cuotas; reprogramación de cuotas; reversa de aceptación |
| **Contabilidad** | Plan de cuentas con naturaleza por nivel; 12 cuentas especiales; cuentas por banco/tipo de factoring/tasa/cargo/reestructuración; asientos manuales; saldos y saldos P&G; cierre y desbloqueo de mes; libro mayor, balance general, estado de P&G |
| **Facturación de venta** | Facturas por liquidación, cobranza, al vencimiento, por comisión y cargos; XML de factura v1.1.0 con clave de acceso (módulo 11) y **descarga** |
| **Integraciones** | Slack, Twilio WhatsApp, Meta WhatsApp Cloud API, Google OAuth2 + Calendar, OpenAI (`gpt-4.1` vía Responses API), SRI (SOAP autorización + REST catastro de RUC), newsdata.io, AWS S3 (configurada pero **no activa**) |
| **IA** | `InvoiceAIAnalysis`: riesgo BAJO/MEDIO/ALTO + recomendación, persistido por documento |

### 1.3 La única automatización que ya existe

Vale la pena reconocerla porque es **la semilla del plan premium**. Hay un webhook entrante funcionando:

```
POST /solicitudes/webhook/cargar-solicitudes/   (solicitudes/webhooks.py:12)
  ↓  payload: { correo: { from, subject, attachments[{filename, content}] }, empresa_id, user_id }
  ↓  servicios.procesar_mensaje_del_agente → crear_asignacion_desde_xmls
  ↓  identifica al cliente por email (ctemail2 → ctemail), parsea factura o <autorizacion><comprobante>,
     valida XSD (factura_V2.1.0.xsd con lxml), reutiliza asignación abierta del cliente y crea los Documentos
  ↓  respuesta: { ok, empresa_id, procesados, creadas, correos[] }
```

Y en `administracion/comandos/` hay **un nodo Code de n8n ya escrito** (`nodo code.js`, 115 líneas) que decodifica adjuntos ZIP/GZIP/ZLIB/UTF-16 por *magic bytes* para extraer el XML de la factura, más un workflow n8n de prueba (`n8n-parche-http-request.json`) que consulta `AutorizacionComprobantesOffline` del SRI por SOAP.

**Esto significa que el equipo ya validó n8n como herramienta y ya resolvió el problema más difícil** (la decodificación de adjuntos del SRI). El plan premium no es una apuesta tecnológica: es **productizar lo que ya está probado**.

También existe un segundo webhook, de consulta:

```
POST /cobranzas/webhook/facturas_por_vencer/   (cobranzas/webhooks.py:13)
  entrada: { dias, empresa_id, usuario_id }
  salida:  { clientes: [ { nombre, celular, facturas:[{numero, fecha_vencimiento, saldo}] } ] }
```

Nótese que **ya devuelve el `celular` del cliente** — es decir, está diseñado exactamente para que n8n dispare recordatorios de WhatsApp. Está construido y sin conectar.

### 1.4 Deuda técnica que condiciona la implementación

Estos hallazgos son relevantes porque el plan premium **expone el sistema al mundo** (más webhooks salientes, más tráfico, más integraciones) y algunos bloqueaban directamente la implementación.

> **Los 5 puntos marcados como 🔴 CORREGIDO ya fueron resueltos y verificados** (26-jul-2026). El detalle de cada corrección está en el anexo **8.6**.

| Severidad | Estado | Hallazgo | Archivo |
|---|---|---|---|
| **Crítica** | 🔴 **CORREGIDO** | `eval(request.POST["Cheques"])` en el alta de accesorios → **ejecución de código arbitrario** desde un formulario | `solicitudes/views.py` |
| **Crítica** | 🔴 **CORREGIDO** | Endpoints `/api/*` sin autenticación: `permission_classes` comentado, `InvoiceAIAnalysisView` sin permisos y **`rest_framework` no estaba en `INSTALLED_APPS` ni existía `REST_FRAMEWORK`** → default DRF `AllowAny`. `estado_operativo_cliente_api` exponía línea, cartera y protestos de cualquier cliente con solo cambiar el ID | `api/views.py` |
| **Crítica** | 🔴 **CORREGIDO** | `asiento_contable_api` sin login **y sin filtro de empresa** → fuga multi-tenant de asientos contables | `contabilidad/views.py` |
| **Alta** | 🔴 **CORREGIDO** | `DEBUG = True` en el módulo de settings activo, con hosts de producción configurados | `factorweb25/settings.py` |
| **Alta** | 🔴 **CORREGIDO** | Webhooks entrantes sin verificación de firma: Twilio no validaba `X-Twilio-Signature`, Meta no validaba `X-Hub-Signature-256` y la carga de solicitudes no exigía credencial alguna | `api/twilio_service.py`, `api/whatsapp.py`, `solicitudes/webhooks.py` |
| **Crítica** | ⏳ Pendiente | `Configuracion_correos` tiene comas finales en 4 campos → `ctlogincorreo`, `ctpasswordcorreo`, `ctnombreremitente`, `ctasuntocorreo` quedaron como **tuplas**, no como campos, y **no existen en la base de datos**. La configuración SMTP es inutilizable y no hay `EMAIL_BACKEND` | `empresa/models.py:20-23` |
| **Crítica** | ⏳ Pendiente | El comando de correo IMAP **no es un management command** (vive en `administracion/comandos/`, no en `management/commands/`) → `manage.py procesar_correos` falla. Además tiene credenciales hardcodeadas | `administracion/comandos/procesar_correos.py:16-18` |
| **Alta** | ⏳ Pendiente | Secretos en texto plano en la base de datos: token y signing secret de Slack, auth token de Twilio. API key de newsdata.io **hardcodeada** | `api/models.py:5-24`, `api/noticias.py:68` |
| **Alta** | ⏳ Pendiente | Sin `LOGGING` ni manejo de errores centralizado; los fallos de SP se devuelven como texto `"Error:..."` y se imprimen | `bases/views.py:73-74` |
| **Alta** | ⏳ Pendiente | `api/noticias.py` ejecuta una llamada a la API **al importar el módulo** (líneas 68-82) | `api/noticias.py` |
| **Alta** | ⏳ Pendiente | `webhook_whatsapp_twilio` no aísla por empresa: toma la primera configuración activa de cualquier tenant | `api/twilio_service.py` |
| **Media** | ⏳ Pendiente | SQL por concatenación `.format()` hacia los stored procedures → superficie de inyección | `operaciones/views.py:764,1532,1748`, `cobranzas/views.py` |
| **Media** | ⏳ Pendiente | Varias `UpdateView` no re-verifican que el objeto pertenezca a la empresa del usuario | p. ej. `clientes/`, `pais/views.py:129-131` |
| **Media** | ⏳ Pendiente | `user_password` usa `make_password()` directo → **omite `AUTH_PASSWORD_VALIDATORS`** | `bases/views.py:288` |
| **Media** | ⏳ Pendiente | Sin `CACHES` configurado: la caché de RUC del SRI (`SRI_RUC_CACHE_SECONDS=43200`) cae en LocMemCache, que no se comparte entre workers de gunicorn | `settings.py` |
| **Media** | ⏳ Pendiente | `Pagares` no tiene FK a `Asignacion` → la reestructuración no queda trazada contra las facturas refinanciadas | `operaciones/models.py:2051` |
| **Media** | ⏳ Pendiente | Las migraciones no aplican sobre SQLite → la suite de tests no puede correr sin una base PostgreSQL de test | `contabilidad/migrations/0019` |
| **Baja** | ⏳ Pendiente | `Solicitud_aprobacion.asignacion` es un `BigInteger` suelto, no una FK | `solicitudes/models.py:55` |
| **Baja** | ⏳ Pendiente | `local_settings.py`, `aws_settings.py` y `cloud_settings.py` existen pero **no se usan**; solo `aws_settings.py` tiene `DEBUG=False` | — |
| **Baja** | ⏳ Pendiente | Migración de base de datos: la lógica de negocio fuerte vive en SPs **fuera del control de versiones de Django** | — |

> **Nota de riesgo para la propuesta premium:** el endurecimiento de la superficie de integración era el requisito previo para conectar el sistema a workflows de automatización. Un webhook saliente que filtra datos entre empresas, o una ejecución de código arbitrario accesible desde el flujo de ingreso de facturas, se vuelve mucho más peligroso cuando además se automatiza. **Ese requisito previo está cumplido**; queda como siguiente lote cerrar la configuración de correo, la gestión de secretos y la observabilidad.

---

## 2. Opciones omitidas: lo que una compañía de factoring debería manejar

Las 10 omisiones del resumen ejecutivo son las de mayor impacto comercial. A continuación el inventario completo, organizado por área funcional, con la evidencia de la ausencia en el código. Se marca con ⚙️ lo que n8n puede resolver sin tocar el núcleo de Django, con 🔧 lo que requiere desarrollo, y con ⚖️ lo que es requisito regulatorio o legal.

### 2.1 Gestión del ciclo de crédito (el hueco más grande)

| # | Opción omitida | Evidencia de la ausencia | Vía |
|---|---|---|---|
| O-01 | ⚖️ **KYC / AML / listas de control** | `clientes.Datos_compradores` solo tiene `cxclase` (FK a `Clases_cliente`) y `cxestado` (A/X). No hay PEP, sanciones, beneficiario final, calificación de riesgo ni evidencia documental | ⚙️ n8n consulta listas + 🔧 campos |
| O-02 | ⚖️ **Validación de cédula/RUC** | `Clientes.cxcliente` es `CharField(13)` **sin validador**. `api/sri.py:112 consulta_contribuyente_sri` está implementado (con reintentos, proxy y caché de 12 h) pero **nunca se invoca** desde el alta de clientes | ⚙️ n8n puede llamarlo ya |
| O-03 | **Scoring y rating crediticio** | No existe campo de score, PD, capacidad de pago ni buró. `Datos_generales.npromediodemoradepago` y `Datos_compradores.reporte_ultimas_cobranzas()` están marcados en el código como "utilizado para el análisis de riesgo con IA" pero **ningún código los consume** | ⚙️ n8n + IA |
| O-04 | **Comité de crédito formal** | El cambio de clase solo se registra como *sugerencia* en `Revision_cartera_detalle.ctclaseactual/ctestadoactual`. No hay acta, quórum, votación ni trazabilidad de la decisión | ⚙️ n8n + 🔧 campos |
| O-05 | **Cupos y líneas: control preventivo** | Al crear una solicitud **no se valida** `Linea_Factoring.disponible()` ni `Cupos_compradores` disponible, ni se bloquea a un deudor con `cxestado='X'`. La única validación es `Exceso_temporal.estado()`, que se consulta a posteriori | ⚙️ n8n puede bloquear |
| O-06 | **Concentración de cartera por deudor/sector** | No hay cálculo de concentración ni límite por deudor, sector (`Actividades`), provincia o clase. El cupo por deudor (`Cupos_compradores`) es manual y no comparativo | ⚙️ n8n + reportes |
| O-07 | **Seguro de crédito / pólizas** | No existe ningún modelo de póliza, aseguradora, cobertura, prima ni reclamo | 🔧 desarrollo |
| O-08 | ⚖️ **Prevención de doble financiamiento** | La única defensa es `DocumentosForm.clean` (`solicitudes/forms.py:142-190`), que compara contra la propia base. No hay consulta a registros de otros factores ni a un registro compartido | ⚙️ n8n puede orquestar |

### 2.2 Formalización legal y cesión

| # | Opción omitida | Evidencia de la ausencia | Vía |
|---|---|---|---|
| O-09 | ⚖️ **Notificación de cesión al deudor con acuse** | `Anexos.lcesionfacturas` (bool) solo dispara `Documentos.lnotificaciongenerada = True` (`operaciones/views.py:2454-2457`) y un .docx descargable. **No hay envío, constancia, fecha de recepción, acuse ni registro de objeción.** Este es el mayor riesgo legal del sistema | ⚙️ n8n **P0** |
| O-10 | ⚖️ **Firma electrónica** | `pyHanko`, `cryptography` y `lxml` están en `requirements.txt` pero **no se usan para firmar nada**. No hay firma XAdES en el XML del SRI, ni firma de contratos, ni campos de firma/OTP | 🔧 + ⚙️ |
| O-11 | **Onboarding digital del cliente** | `Personas_juridicas` / `Personas_naturales` son captura manual sin checklist documental, sin portal de carga, sin validación de completitud. `Datos_generales.dcontrato` es solo una fecha | ⚙️ n8n |
| O-12 | **Expediente documental persistido** | Los 47 PDF (WeasyPrint) y los .docx (docxtpl) **se transmiten al navegador y no se guardan**. No hay repositorio documental, versionado ni evidencia. `cuentas_bancarias.ctrutaarchivobanco` es un campo huérfano | ⚙️ n8n puede archivarlos |
| O-13 | **Aceptación/objeción del deudor** | No existe entidad de aceptación de factura ni de objeción/disputa. El deudor no tiene ningún punto de contacto digital con el sistema | ⚙️ n8n + 🔧 |
| O-14 | **Gestión de garantías y colateral** | Solo 4 campos de texto/fecha para un cheque garantía en `Asignacion` (`ctbancochequegarantia`, `ctcuentachequegarantia`, `ctnumerochequegarantia`, `dchequegaratia`) y `Movimientos_maestro.lcolateral`. **Sin valuación, liberación, sustitución ni seguimiento de cobertura** | ⚙️ n8n + 🔧 |

### 2.3 Cobranza y recaudo

| # | Opción omitida | Evidencia de la ausencia | Vía |
|---|---|---|---|
| O-15 | **Notificación y recordatorio automático** | **Cero `send_mail`** en el proyecto. `ctcelular` etiquetado "WhatsApp" pero sin envío automático. `facturas_por_vencer` ya devuelve el celular y nadie lo consume | ⚙️ n8n **P0** |
| O-16 | **Escalamiento automático por mora** | `Registra_gestion_cobro` (`cobranzas/views.py:4490`) se ejecuta 100 % a mano, cliente por cliente. Sin cron, sin reglas de escalamiento, sin asignación por tramos de antigüedad | ⚙️ n8n **P0** |
| O-17 | **Promesas / acuerdos de pago** | `Gestion_cobro` solo tiene `cxtipoparticipante`, `cxestado` (A/C/P/R) y `ctnumerowhatsapp`. **No hay fecha compromiso, monto comprometido, cuotas del acuerdo ni medición de cumplimiento** | ⚙️ n8n **P0** |
| O-18 | **Conciliación bancaria automática** | `Desembolsos.lgeneradoarchivobanco` es un `BooleanField`. No hay importación de extractos, ni matching depósito↔cobranza, ni estado de conciliación. `ctrutaarchivobanco` sin uso | 🔧 + ⚙️ n8n |
| O-19 | **Domiciliación / débito automático / pasarela de pago** | `FORMAS_DE_PAGO` se limita a `EFE/CHE/MOV/TRA` (+`DEP` en protestos): `operaciones/models.py:2008`, `cobranzas/models.py:63,1364,1461,1547`. **Sin mandato, sin cobro recurrente, sin tarjeta, sin link de pago** | 🔧 + ⚙️ |
| O-20 | **Portal del deudor** | Todas las vistas heredan de `SinPrivilegios` (`login_required`). **No hay rutas públicas** de consulta de saldo, estado de factura o pago | 🔧 + ⚙️ |
| O-21 | **Tabla de mora escalonada** | Una sola tasa plana `Datos_operativos.ntasamora` (`operaciones/models.py:49`). Sin tramos por días, sin tope legal, sin control de anatocismo | ⚙️ n8n puede calcular |
| O-22 | **Trazabilidad de intentos de contacto** | `Twilio_whatsapp` registra mensajes, pero **no hay entidad de intento** con resultado (no contesta, número erróneo, promesa, disputa). El resultado se escribe en texto libre en `Revision_cartera_detalle.ctcomentario` | ⚙️ n8n + 🔧 |
| O-23 | **Cobranza judicial / legal** | Solo `Motivos_protesto_maestro` y `Documentos_protestados`. **Sin abogado, juzgado, etapa procesal, costas, ni seguimiento de juicio** | 🔧 + ⚙️ |
| O-24 | **Castigo de cartera** | `Documentos.lcastigada` y el estado `'C'` (Cartera castigada) **existen pero ninguna vista de `operaciones` los asigna**. Sin flujo, sin aprobación por comité, sin reversa de castigo, sin política de recuperación posterior | 🔧 |
| O-25 | **Retenciones electrónicas (SRI)** | `nretencioniva` / `nretencionrenta` se **digitan a mano** (`solicitudes/forms.py:50,61-62`). `solicitudes.models.Documentos.retenciones()` es una propiedad calculada, pero **no hay comprobante de retención ni validación contra el SRI** | ⚙️ n8n **P0** |

### 2.4 Riesgo financiero y contable

| # | Opción omitida | Evidencia de la ausencia | Vía |
|---|---|---|---|
| O-26 | ⚖️ **NIIF 9 / pérdida esperada (ECL)** | `provision_cargos` (`operaciones/models.py:604-687`, duplicado en 1272-1352 y 1636-1719) calcula `dc_vencido + gao_adicional + iva`, que es **devengo de ingresos, no deterioro**. Sin staging (1/2/3), sin PD/LGD, sin matriz de provisiones por calificación | 🔧 |
| O-27 | **Multipago / desembolso dividido** | `Desembolsos` y `DesembolsarForm` manejan **un** valor, **una** forma de pago y **un** destino (`operaciones/forms.py:139-207`). Sin pago a varios beneficiarios, sin retención en la fuente al desembolsar | 🔧 |
| O-28 | **Multi-moneda y tipo de cambio** | `Tipos_factoring.cxmoneda` existe (`empresa/models.py:112`) pero el XML del SRI fija `moneda='DOLAR'` (`contabilidad/sri.py:176`). **Sin tipos de cambio, sin revaluación** | 🔧 |
| O-29 | **Impuestos configurables por jurisdicción** | Solo `Empresas.nporcentajeiva` (default 12, columna con default 15) + mapas hardcodeados en `contabilidad/sri.py:118-132` | 🔧 |
| O-30 | **Anexos transaccionales (ATS) y reportería tributaria** | La carpeta `anexos/` está **fuera de `INSTALLED_APPS`**. Sin generación de ATS ni conciliación de IVA/retenciones | 🔧 + ⚙️ |
| O-31 | **Cierre contable automático** | `CierreDeMes` (`contabilidad/views.py:2291`), `GenerarAsientos*`, `GenerarFacturasAlVencimientoDiario` son **endpoints manuales**. Sin calendario de cierre ni tareas recurrentes | ⚙️ n8n **P0** |
| O-32 | **Confiabilidad de la cadena de facturación electrónica** | `GeneraXMLFactura` produce el XML con clave de acceso pero **no firma XAdES ni envía a Recepción del SRI**. `api/sri2.py` es código muerto que hace una llamada SOAP **a nivel de import** con una clave hardcodeada | ⚙️ n8n **P0** |
| O-33 | **Factoraje internacional / forfaiting** | `cxmoneda` existe sin flujo. Sin documentos de exportación, riesgo país ni tipo de cambio | 🔧 |
| O-34 | **Confirming / reverse factoring** | `Tipos_factoring.lfactoringproveedores` existe (`empresa/models.py:127`) **sin ningún flujo asociado**: sin proveedor, sin aprobación del deudor pagador, sin pago por cuenta del deudor | 🔧 |

### 2.5 Plataforma: seguridad, control y comercial

| # | Opción omitida | Evidencia de la ausencia | Vía |
|---|---|---|---|
| O-35 | **Auditoría de cambios y trazabilidad** | `ClaseModelo` solo guarda `cxusuariocrea` (FK), `cxusuariomodifica` (Int, **no FK**), `leliminado`, `cxusuarioelimina` (Int). **Sin tabla histórica, sin `django-simple-history`**, y varias `UpdateView` ni setean el campo de modificación | 🔧 |
| O-36 | ⚖️ **2FA / MFA y política de contraseñas** | Ausente. Y `user_password` usa `make_password()` directo, **eludiendo `AUTH_PASSWORD_VALIDATORS`** (`bases/views.py:288`) | 🔧 + ⚙️ |
| O-37 | **API pública con API keys / OAuth y scopes** | Sin `rest_framework.authtoken`, sin modelo de API key, sin cliente OAuth. `/api/*` es anónimo o por cookie de sesión | 🔧 |
| O-38 | **Webhooks salientes firmados, con reintentos e idempotencia** | **No existe ningún webhook saliente.** Solo Slack valida firma (`api/slack.py:205`); Twilio, Meta WhatsApp y el webhook de facturas **no**. Sin outbox, sin reintentos, sin idempotencia | 🔧 **base del premium** |
| O-39 | **Rate limiting / throttling** | Sin `DEFAULT_THROTTLE_*`, sin middleware de límites. Los endpoints `/api/*` anónimos son indefendibles ante scraping | 🔧 + ⚙️ |
| O-40 | **Observabilidad y alertas** | Sin `LOGGING`, sin Sentry/OTel, sin health-check, sin métricas. Los errores van a `print()` con `DEBUG=True` | ⚙️ n8n **P0** |
| O-41 | **SLA operativos medidos** | `Niveles_aprobacion.nhorasrespuestamaxima` existe pero **está excluido del formulario** (`solicitudes/forms.py:285`) y **no se usa en `slack.py`**. No hay medición de tiempo de aprobación, de desembolso ni de primer contacto de cobranza | ⚙️ n8n **P0** |
| O-42 | **Gestión de suscripciones, planes y facturación del propio SaaS** | **No existe.** `lgratis`, `nmaximooperaciones` y `dfinpruebas` no se leen en ningún punto del código para bloquear o cobrar. Sin modelo de plan, precio, factura de suscripción ni pasarela | 🔧 **base del premium** |
| O-43 | **Noticias/análisis de riesgo externo** | `api/noticias.py` consulta newsdata.io con una **API key hardcodeada** y ejecuta la llamada **al importar el módulo** | ⚙️ n8n |
| O-44 | **Backup y recuperación** | Sin scripts de respaldo ni `pg_dump` automatizado. `db.sqlite3` obsoleto versionado en el repositorio | ⚙️ n8n |
| O-45 | **Reportes distribuidos automáticamente** | Los cortes y revisiones existen pero **no se envían a nadie**. Todo reporte requiere que alguien entre al sistema, lo genere y lo descargue | ⚙️ n8n **P0** |
| O-46 | **Registro de actividad / bitácora de negocio** | Sin tabla de eventos. Sin `signals.py` en ninguna app. Es imposible responder "¿qué pasó con la operación 158?" sin reconstruirlo a mano entre 6 tablas | 🔧 **base del premium** |

### 2.6 Priorización: qué construir primero

```
                        ALTO IMPACTO
                             │
   ⚙️ n8n + IA              │            🔧 Requiere desarrollo
   O-01 KYC/AML             │            O-26 NIIF 9 / ECL
   O-03 Scoring deudor      │            O-29 Impuestos por país
   O-06 Concentración       │            O-37 API pública con keys
   O-17 Promesas de pago    │            O-42 Billing del SaaS
   O-45 Reportes autom.     │  ┌──────────────────────────────┐
                             │  │                              │
                             │  │   ZONA DE ORO DEL PREMIUM    │
                             │  │                              │
   ⚙️ O-09 Cesión con acuse  │  │  ⚙️ O-15 Notificaciones      │
   O-13 Aceptación deudor   │  │  ⚙️ O-16 Escalamiento mora    │
   O-18 Conciliación        │  │  ⚙️ O-25 Retenciones SRI      │
                             │  │  ⚙️ O-31 Cierre automático    │
                             │  │  ⚙️ O-32 Cadena SRI completa  │
                             │  │  ⚙️ O-38 Webhooks firmados 🔧 │
                             │  │  ⚙️ O-41 SLA operativos       │
                             │  │  O-12 Expediente documental   │
                             │  └──────────────────────────────┘
                             │
   ──────────────────────────┼──────────────────────────────  ESFUERZO →
        BAJO ESFUERZO        │        ALTO ESFUERZO
                             │
                        BAJO IMPACTO
```

**La "zona de oro"** —alto impacto y esfuerzo mayoritariamente de configuración en n8n— es exactamente el contenido del plan premium que se propone en la sección 5. Las omisiones que requieren desarrollo de fondo (NIIF 9, billing, API pública) se dejan fuera del alcance del premium o se venden como proyecto aparte.

---

## 3. Estado actual de webhooks e integración con n8n

### 3.1 Lo que existe hoy

| Tipo | Endpoint / artefacto | Autenticación | Estado |
|---|---|---|---|
| **Entrante** | `POST /solicitudes/webhook/cargar-solicitudes/` → `solicitudes/webhooks.py:12` | **Ninguna** (`@csrf_exempt`, sin firma, sin token) | 🟢 Funcionando |
| **Entrante** | `POST /cobranzas/webhook/facturas_por_vencer/` → `cobranzas/webhooks.py:13` | **Ninguna** (`@csrf_exempt`) | 🟡 Construido, sin consumidor |
| **Entrante** | `POST /api/twilio/webhook_whatsapp_twilio/` → `api/twilio_service.py:100` | **Ninguna** (Twilio firma `X-Twilio-Signature` y **no se valida**) | 🟢 Funcionando |
| **Entrante** | `GET|POST /api/whatsapp/webhook/` → `api/whatsapp.py:40` | Solo el `hub.verify_token` en GET; el POST **solo imprime, no persiste** | 🟡 Incompleto |
| **Entrante** | `POST /api/slack/interactive-endpoint/` → `api/slack.py:190` | 🟢 **Sí valida firma** (`SignatureVerifier`) — el único que lo hace | 🟢 Funcionando |
| **Saliente** | — | — | 🔴 **No existe ninguno** |
| **n8n** | `administracion/comandos/nodo code.js` (nodo Code que decodifica adjuntos SRI) + `n8n-parche-http-request.json` (consulta SOAP al SRI) | — | 🟢 Probado por el equipo |

**Diagnóstico:** hay entrada sin salida. El sistema sabe recibir instrucciones del mundo exterior pero **no sabe contarle nada a nadie**. Ese desequilibrio es precisamente el espacio comercial del plan premium.

### 3.2 Principios de diseño de la capa de eventos

| Principio | Decisión | Por qué |
|---|---|---|
| **No bloquear la transacción** | Patrón **outbox**: el evento se escribe en una tabla dentro de la misma transacción de negocio y un worker lo despacha después | El 90 % de la lógica crítica vive en stored procedures. Un webhook que falla **no puede** reversar una liquidación ya contabilizada |
| **At-least-once + idempotencia** | Cada evento lleva `event_id` (UUID v4) y `idempotency_key`; el consumidor deduplica | La red falla. Es preferible un evento duplicado que un desembolso no notificado |
| **Firma HMAC-SHA256** | Cabecera `X-Margarita-Signature: sha256=<hex>` sobre `timestamp + '.' + body`, con ventana de tolerancia de 5 min | Sin firma, cualquiera que descubra la URL de n8n puede inyectar eventos falsos de negocio |
| **Reintentos con backoff exponencial** | 8 intentos: 30 s, 2 m, 10 m, 30 m, 2 h, 6 h, 12 h, 24 h → luego *dead letter* | Cubre caídas de n8n, del VPS y de las APIs externas |
| **Aislamiento multi-tenant** | El evento **siempre** lleva `empresa_id`; el suscriptor se registra por empresa y no puede recibir eventos de otra | El sistema hoy aísla solo por convención en el queryset. Los webhooks no deben heredar esa debilidad |
| **Payload plano y estable** | JSON sin anidamiento profundo, con `schema_version` y `occurred_at` en ISO-8601 (`America/Guayaquil`) | Que un workflow en n8n no se rompa cuando cambie un modelo |
| **Solo datos de negocio, nunca secretos** | Prohibido incluir tokens, contraseñas, claves de acceso completas o datos de tarjeta | Los secretos hoy ya están en claro en la base de datos; no los propagamos por HTTP |
| **Opt-in por evento** | El suscriptor elige qué eventos recibe (wildcard `solicitud.*` soportado) | Evitar mandar 135 tipos de evento a un cliente que solo quiere notificaciones de cobranza |

### 3.3 Arquitectura propuesta

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DJANGO (factorweb)                                  │
│                                                                              │
│  Vista / SP wrapper          señal post_save / llamada explícita             │
│        │                                    │                                │
│        └──────────────┬─────────────────────┘                                │
│                       ▼                                                      │
│         ┌─────────────────────────────┐                                      │
│         │  eventos.emitir(...)        │  ← dentro de la MISMA transacción   │
│         │  crea WebhookEvent (outbox) │                                      │
│         └─────────────┬───────────────┘                                      │
│                       │  estado = PENDIENTE                                  │
│  ┌────────────────────┼──────────────────────────────────────────────────┐   │
│  │  BASE DE DATOS     ▼                                                  │   │
│  │  webhook_endpoint   (url, secret, eventos[], empresa, lactivo)        │   │
│  │  webhook_event      (event_id, tipo, payload JSON, empresa, estado)    │   │
│  │  webhook_delivery   (event→endpoint, intento, http_status, error)      │   │
│  └────────────────────┬──────────────────────────────────────────────────┘   │
│                       │                                                      │
│         ┌─────────────▼───────────────┐                                      │
│         │  despachador (worker)       │   management command + cron cada 30s │
│         │  - firma HMAC-SHA256        │   o disparado por n8n Schedule       │
│         │  - POST con timeout 15s      │                                      │
│         │  - backoff exponencial       │                                      │
│         │  - dead letter a los 8 fallos│                                      │
│         └─────────────┬───────────────┘                                      │
└───────────────────────┼──────────────────────────────────────────────────────┘
                        │  HTTPS + X-Margarita-Signature
                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              n8n                                             │
│                                                                              │
│   Webhook node ──► Crypto node (verifica HMAC) ──► Switch (por tipo)         │
│                        │                                                     │
│                        ├─► Postgres node  → consulta datos ampliados         │
│                        ├─► HTTP Request   → SRI / bancos / buró / OpenAI     │
│                        ├─► WhatsApp/Slack/Email → notificaciones             │
│                        ├─► Google Drive/Sheets → expediente y control        │
│                        └─► Wait node      → temporizadores de SLA            │
│                                                                              │
│   Schedule Trigger ──► HTTP Request → endpoints de Margarita (recordatorios, │
│                        cierre de mes, asientos, cortes, provisiones)         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Modelo de datos propuesto (3 tablas nuevas)

| Tabla | Campos | Propósito |
|---|---|---|
| `webhook_endpoint` | `empresa` (FK), `ctnombre`, `cturl`, `ctsecret` (HMAC), `jeventos` (lista/wildcards), `lactivo`, `nreintentosmaximos`, `ntimeoutsegundos`, `lverificaselifirma`, estadísticas de entrega | Registro de suscriptores. Reemplaza la configuración de Slack/Twilio que hoy vive en texto plano |
| `webhook_event` | `event_id` (UUID, unique), `cttipo`, `jsonspayload`, `empresa`, `docurrencia`, `nschemaversion`, `cxentidadorigen`, `nidorigen` | **Outbox**. Es también la **bitácora de negocio** que hoy no existe (omisión O-46) |
| `webhook_delivery` | `event` (FK), `endpoint` (FK), `nintento`, `nhttpstatus`, `ctrespuesta`, `dproximoIntento`, `lestado` (pendiente/entregado/fallido/dead_letter), `nduracionms` | Trazabilidad por entrega, base para reintentos y para el tablero de salud de integraciones |

> **Bonus:** `webhook_event` resuelve por sí sola la omisión O-46. Con ella, la pregunta *"¿qué pasó con la operación 158?"* se responde con un `SELECT` sobre una tabla, en lugar de reconstruirla a mano entre `solicitudes.Asignacion`, `operaciones.Asignacion`, `operaciones.Documentos`, `cobranzas.Documentos_cabecera`, `contabilidad.Diario_cabecera` y los logs de Slack.

### 3.5 Contrato del evento

**Cabeceras HTTP**

```http
POST /webhook/margarita HTTP/1.1
Content-Type: application/json; charset=utf-8
X-Margarita-Signature: sha256=8f3a...c1e
X-Margarita-Event: operacion.liquidada
X-Margarita-Delivery: 6d2f9a10-4b8e-4c77-9a21-0f5e3d8c7b41
X-Margarita-Attempt: 1
User-Agent: Margarita-Webhooks/1.0
```

**Cuerpo**

```json
{
  "event_id": "0f9c2b74-5a31-4e88-b0d2-7c1f4a9e6b35",
  "event": "operacion.liquidada",
  "schema_version": "1.0",
  "occurred_at": "2026-03-14T16:42:07-05:00",
  "empresa_id": 1,
  "empresa_ruc": "0992345678001",
  "actor": { "user_id": 14, "username": "lgodoy", "origen": "web" },
  "entity": { "tipo": "operaciones.Asignacion", "id": 158, "codigo": "OP-000158" },
  "data": {
    "asignacion_id": 158,
    "cliente_id": 42,
    "cliente_ruc": "1790012345001",
    "cliente_nombre": "ACME ECUADOR S.A.",
    "nvalor": "48500.00",
    "nanticipo": "38800.00",
    "neto": "37245.80",
    "ddesembolso": "2026-03-16",
    "documentos": [
      { "documento_id": 901, "numero": "001-002-000012345",
        "deudor_ruc": "0991234567001", "ntotal": "24250.00",
        "dvencimiento": "2026-06-12" }
    ]
  },
  "links": {
    "self": "https://margarita.codigobambuecuador.com/operaciones/consultaasignaciones/158/",
    "pdf": "https://margarita.codigobambuecuador.com/operaciones/imprimirasignacion/158/"
  }
}
```

**Reglas del contrato**

- Los montos viajan **como string decimal**, nunca como float, para no perder centavos en JavaScript.
- Las fechas son ISO-8601 con zona horaria de Ecuador (`USE_TZ = False` hoy → hay que fijar el offset explícitamente).
- `entity.id` es el ID interno del sistema. `entity.codigo` es el identificador legible para humanos (`OP-000158`, `sol00001`, `CXC00042`).
- El bloque `links` es opcional pero **muy rentable**: permite que el mensaje de WhatsApp o el correo incluya un enlace directo a la operación en Margarita.
- Todo evento es **inmutable**: si algo cambia, se emite un evento nuevo (`*.modificado` / `*.reversado`), nunca se reescribe el anterior.

**Verificación de firma en n8n (nodo Crypto)**

```javascript
// Nodo Code en n8n — validar que el evento viene de Margarita
const crypto = require('crypto');
const secret = $env.MARGARITA_WEBHOOK_SECRET;
const rawBody = $input.first().binary?.data
  ? Buffer.from($input.first().binary.data.data, 'base64').toString('utf8')
  : JSON.stringify($input.first().json.body);

const timestamp = $input.first().json.headers['x-margarita-timestamp'];
const firmaRecibida = $input.first().json.headers['x-margarita-signature'];

// Ventana de tolerancia de 5 minutos contra replay
const edadSegundos = Math.abs(Date.now() / 1000 - Number(timestamp));
if (edadSegundos > 300) throw new Error('Evento fuera de la ventana de tolerancia');

const esperada = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(`${timestamp}.${rawBody}`)
  .digest('hex');

if (!crypto.timingSafeEqual(Buffer.from(esperada), Buffer.from(firmaRecibida))) {
  throw new Error('Firma HMAC inválida: evento rechazado');
}

return $input.all();
```

---

## 4. Catálogo de eventos para workflows n8n

**135 eventos** organizados en 6 dominios. Cada uno indica el punto exacto del código donde debe emitirse, el payload realmente disponible en ese punto, y la automatización concreta que habilita.

**Leyenda de prioridad**

| Prioridad | Significado | Criterio |
|---|---|---|
| **P0** | Crítico | Sin este evento el workflow premium no funciona, o cubre riesgo legal/fraude/regulatorio |
| **P1** | Alto | Ahorro de tiempo evidente o mejora directa de cobranza/riesgo |
| **P2** | Medio | Valor operativo y de control, no urgente |
| **P3** | Bajo | Nice-to-have, útil para trazabilidad |

**Resumen por dominio**

| Dominio | Eventos | P0 | P1 | P2 | P3 | Fase |
|---|---|---|---|---|---|---|
| 1. Solicitudes / Negociación | 21 | 7 | 8 | 5 | 1 | Fase 1 |
| 2. Clientes y Deudores | 21 | 7 | 10 | 4 | 0 | Fase 2 |
| 3. Operaciones | 25 | 9 | 9 | 6 | 1 | Fase 1 |
| 4. Cobranzas y Protestos | 33 | 15 | 17 | 1 | 0 | Fase 1 |
| 5. Contabilidad y SRI | 16 | 6 | 6 | 3 | 1 | Fase 2 |
| 6. Plataforma y Premium | 19 | 7 | 6 | 6 | 0 | Fase 3 |
| **TOTAL** | **135** | **51** | **56** | **25** | **3** | 3 fases |

**Los 12 eventos que debe incluir la Fase 1 (MVP comercial, 30 días):**

`solicitud.creada` · `solicitud.documento_agregado` · `solicitud.aprobada` · `solicitud.rechazada` · `solicitud.exceso_temporal_generado` · `operacion.liquidada` · `operacion.desembolsada` · `operacion.cesion_facturas_notificada` · `cobranza.factura_por_vencer` · `cobranza.factura_vencida` · `cobranza.protesto_registrado` · `contabilidad.comprobante_recibido_sri`

### Dominio 1 — Solicitudes / Negociación (ingreso de facturas)

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `solicitud.creada` | **P0** | solicitudes/views.py:401,836,1127 · servicios.py:281 | Alta manual de facturas puras / con accesorios, importación masiva JSON o carga automática por correo-XML. | asignacion_id, cxasignacion (sol00001), cliente{id,ruc,nombre,email,celular}, cxcliente_id, tipo_factoring, cxtipo, nvalor, ncantidaddocumentos, usuario, empresa_id, origen(manual|masivo|correo|api) | POST a CRM (HubSpot/Odoo) creando la oportunidad; acuse de recibo automático al cliente por email+WhatsApp con checklist documental y número de solicitud. |
| 2 | `solicitud.documento_agregado` | **P0** | solicitudes/views.py:458,1238 | Se agrega una factura (Documentos) a la solicitud/negociación. | asignacion_id, documento_id, comprador{ruc,nombre}, ctserie1, ctserie2, ctdocumento, demision, dvencimiento, nvalorantesiva, niva, nretencioniva, nretencionrenta, ntotal, cxautorizacion_ec | Verificar en n8n la clave de acceso contra el SRI (SOAP AutorizacionComprobantesOffline) y marcar la factura como validada antes de liquidar. |
| 3 | `solicitud.documento_eliminado` | **P2** | solicitudes/views.py:530 EliminarDocumento | Eliminación lógica de un documento; en accesorios devuelve el valor a nvalornonegociado. | asignacion_id, documento_id, nvalornonegociado_restante, ncantidaddocumentos | Recalcular en hoja de control el monto solicitado y avisar a operaciones que la solicitud cambió de valor. |
| 4 | `solicitud.documento_recuperado` | **P2** | solicitudes/views.py:585 RecuperarDocumento | Reincorporación de un documento previamente eliminado de la solicitud. | asignacion_id, documento_id, cxautorizacion_ec | Revalidar duplicidad contra operaciones.Documentos y contra otros factores antes de aceptar. |
| 5 | `solicitud.eliminada` | **P2** | solicitudes/views.py:663 EliminarAsignacion | Reversa/eliminación de la negociación completa en estado Pendiente. | asignacion_id, cxasignacion, cliente_id, nvalor, motivo | Cerrar la oportunidad como perdida en el CRM y medir tasa de desistimiento por ejecutivo de ventas. |
| 6 | `solicitud.duplicado_detectado` | **P0** | solicitudes/views.py:1160-1164,1234 · forms.py:142-190 | La factura ya existe en operaciones o ya fue negociada en otro factor; se marca leliminado=True. | documento_id, ctdocumento, ruc_emisor, operacion_origen, motivo, origen_solicitud | ALERTA ANTIFRAUDE a Slack/email del comité: factura duplicada o negociada en otro factor, con bloqueo preventivo de la solicitud. |
| 7 | `solicitud.correo_procesado` | **P1** | solicitudes/webhooks.py:45 → servicios.py:365 | Resultado del webhook entrante que procesa un correo con adjuntos XML. | from, subject, procesados, creadas, asignaciones[], empresa_id | Responder automáticamente al correo del proveedor con el detalle de facturas cargadas y las que fallaron. |
| 8 | `solicitud.correo_sin_cliente` | **P1** | solicitudes/servicios.py:234-236 (ValueError) | Llegó un XML de un remitente que no corresponde a ningún cliente registrado. | sender_email, subject, n_adjuntos, empresa_id | Crear tarea de alta express del solicitante y responder una plantilla pidiendo completar el registro. |
| 9 | `solicitud.correo_xml_invalido` | **P1** | solicitudes/servicios.py:402-403 | El adjunto no es un XML de factura válido o falla la validación XSD. | sender_email, filename, error, empresa_id | Notificar a mesa de ayuda con el archivo adjunto para reproceso manual. |
| 10 | `solicitud.autorizacion_sri_formato_invalido` | **P1** | solicitudes/forms.py:117-120 | El número de autorización no respeta el prefijo ddmmyyyy+01+RUC+2+serie+documento. | documento_id, cxautorizacion_ec, ctdocumento, ruc_emisor | Solicitar en automático el XML/RIDE correcto al cliente y bloquear la liquidación hasta su regularización. |
| 11 | `solicitud.cheque_accesorio_agregado` | **P1** | solicitudes/views.py:942-955 | Alta de cheque o letra que respalda la factura (tipo 'A' con accesorios). | asignacion_id, banco, ctcuenta, ctcheque, ctgirador, propietario(C|D), ntotal, dvencimiento | Agendar recordatorio de depósito y validar fondos/estado del cheque antes del desembolso. |
| 12 | `solicitud.instruccion_pago_registrada` | **P1** | solicitudes/views.py:274 InstruccionDePagoView | El cliente registra la instrucción de pago del desembolso. | asignacion_id, ctinstrucciondepago, cliente_id | Enviar la instrucción al área de tesorería y precargar la orden de transferencia. |
| 13 | `solicitud.pdf_generado` | **P2** | solicitudes/views.py:1400 ImpresionSolicitud | Generación del PDF de la solicitud (facturas puras o con accesorios). | asignacion_id, tipo, url_documento, cliente_id | Archivar en gestor documental (Drive/S3) y enviar copia al cliente y al ejecutivo comercial. |
| 14 | `solicitud.exceso_temporal_generado` | **P0** | solicitudes/models.py:268 Exceso_temporal (creado por el flujo de operaciones) | El valor negociado supera el cupo disponible de la línea de factoring. | exceso_id, cxexceso, cliente_id, asignacion_id, nvalor, disponible_linea, porcentaje_disponible | Pedir aprobación extraordinaria de cupo al comité vía Slack con botones y plazo de respuesta. |
| 15 | `solicitud.exceso_temporal_aceptado` | **P1** | solicitudes/views.py:1355-1361 AceptarExcesoTemporal | Exceso temporal autorizado (estado 'A'). | exceso_id, cliente_id, asignacion_id, nvalor, usuario | Ampliar la línea temporalmente en el sistema, notificar al comité y agendar la revisión al vencimiento del exceso. |
| 16 | `solicitud.exceso_temporal_rechazado` | **P1** | solicitudes/views.py:1330-1338 RechazarExcesoTemporal | Exceso rechazado; ejecuta el SP uspreversaliquidacionasignacion (estado 'R'). | exceso_id, asignacion_id, cliente_id, usuario, resultado_sp | Reversar el desembolso en tesorería, liberar la línea y avisar al cliente el motivo del rechazo. |
| 17 | `solicitud.aprobacion_solicitada` | **P0** | api/slack.py:159-167 enviar_solicitud_aprobacion | Se crea Solicitud_aprobacion en estado 'P' y se publica el PDF en Slack con botones. | solicitud_id, asignacion_id, nivel_id, nmontominimo, naprobadores, canal_slack, monto_neto, url_pdf | Temporizador de SLA con Niveles_aprobacion.nhorasrespuestamaxima: escalar al jefe si no hay respuesta, reenviar a las 2 h y registrar el tiempo de decisión. |
| 18 | `solicitud.aprobada` | **P0** | api/slack.py:241-246 manejar_interactividad (naprobaciones>=naprobadores → cxestado='A') | Alcanzado el número de aprobadores requerido; la negociación queda Aceptada. | solicitud_id, asignacion_id, aprobadores[], monto_neto, usuario_slack, tiempo_respuesta_horas | Disparar la liquidación/desembolso, cerrar el hilo de Slack y avisar al cliente por WhatsApp que su operación fue aprobada. |
| 19 | `solicitud.rechazada` | **P0** | api/slack.py:255-262 (cxestado='R' + uspreversaliquidacionasignacion) | Rechazo de la solicitud con reversa de liquidación. | solicitud_id, asignacion_id, usuario_slack, motivo, resultado_sp | Notificar al cliente con el motivo, liberar línea de factoring y registrar el motivo de rechazo en el CRM. |
| 20 | `solicitud.aprobacion_reenviada` | **P2** | api/slack.py:171-187 reenviar_solicitud_aprobacion (anterior 'X') | Reenvío de una solicitud de aprobación vencida; la anterior se cancela. | solicitud_id, asignacion_id, intento, canal_slack | Medir cuántas veces se reenvía cada nivel y alertar a gerencia si un aprobador es cuello de botella. |
| 21 | `solicitud.pdf_exceso_aprobacion` | **P3** | api/slack.py:62-87 (ImpresionLiquidacion + files_upload_v2) | PDF de liquidación subido a Slack como soporte de la aprobación. | solicitud_id, url_pdf, canal_slack, ts_mensaje | Respaldar cada PDF de aprobación en el repositorio documental con trazabilidad de quién aprobó qué. |

### Dominio 2 — Participantes: Clientes y Deudores

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `cliente.solicitante_creado` | **P1** | solicitudes/views.py SolicitanteCrearView · views.py ImportarOperacion | Alta del solicitante (pre-cliente) que luego se formaliza como cliente. | solicitante_id, cxcliente(RUC/cédula), ctnombre, email, celular, cxlocalidad, origen | Onboarding automático: enviar welcome pack, formulario KYC y checklist de documentos por email y WhatsApp. |
| 2 | `cliente.promovido_desde_solicitante` | **P1** | clientes/views.py:709-747 DatosClientes | El solicitante pasa a cliente formal (Datos_participantes + Datos_generales) y se sincroniza el registro original. | cliente_id, solicitante_id, ctnombre, tipo_cliente(N|J), ejecutivo, dcontrato | Iniciar onboarding completo: contrato digital, definición de línea y alta de cuentas bancarias con tareas asignadas. |
| 3 | `cliente.actualizado` | **P2** | clientes/views.py:721-726 DatosClientes (POST) | Modificación de los datos maestros del cliente. | cliente_id, campos_modificados, usuario, empresa_id | Resincronizar el maestro de clientes con el ERP/CRM y versionar los cambios para auditoría. |
| 4 | `cliente.persona_juridica_registrada` | **P1** | clientes/views.py:618-644 | Alta de la ficha jurídica con representantes legales y vencimiento de sus cargos. | cliente_id, razon_social, ruc, tipoempresa, representantes[{nombre,cargo,dvencimientocargo}] | Agendar alertas de vencimiento de nombramiento del representante legal y pedir el nombramiento actualizado. |
| 5 | `cliente.persona_natural_registrada` | **P2** | clientes/views.py:648-674 | Alta de la ficha de persona natural. | cliente_id, nombres, cxtipoid, sexo, dnacimiento, estado_civil, ctnombrenegocio | Completar expediente digital y validar identidad (validación de cédula) antes de la primera operación. |
| 6 | `cliente.linea_factoring_otorgada` | **P0** | clientes/views.py:274-289 LineaNew | Otorgamiento de la línea de factoring (cupo del cliente). | cliente_id, nvalor, cxmoneda, lconrecurso, nreestructuracion | Notificar al cliente el cupo aprobado con condiciones y carta de línea; actualizar el límite en el CRM. |
| 7 | `cliente.linea_factoring_modificada` | **P0** | clientes/views.py:300-319 LineaEdit · Linea_factoring_hist | Cambio de la línea (incluye su histórico Linea_factoring_hist). | cliente_id, valor_anterior, valor_nuevo, utilizado, disponible, porcentaje_disponible, usuario | Si baja el cupo: alerta de riesgo al comité y comunicación formal al cliente. Si sube: oferta comercial automática. |
| 8 | `cliente.linea_por_agotar` | **P0** | clientes/models.py:302 Linea_Factoring.disponible/porcentaje_disponible | Umbral configurable (p. ej. 90 %) de consumo de la línea de factoring. | cliente_id, nvalor, utilizado, disponible, porcentaje_disponible, umbral | Avisar al ejecutivo comercial para ampliar cupo y al cliente por WhatsApp; generar propuesta de ampliación. |
| 9 | `deudor.registrado` | **P0** | solicitudes/views.py:492-498,903-909,1207-1213 · clientes/views.py:1160-1165 | Alta automática o manual del deudor (Datos_compradores) al cargar una factura de un comprador nuevo. | comprador_id, cxcomprador(RUC), ctnombre, cxclase, cxestado, cliente_relacionado | Consulta automática de buró de crédito + listas de control (PEP/sanciones) + validación de RUC en el SRI antes de aceptar sus facturas. |
| 10 | `deudor.estado_cambiado` | **P0** | clientes/views.py:459-491 EstadoCompradorEdit (A Activo / X Bloqueado) | Cambio de estado del deudor (bloqueo o reactivación). | comprador_id, estado_anterior, estado_nuevo, clase, usuario, motivo | Bloquear o habilitar en automático la negociación de facturas de ese deudor y avisar al comité de riesgo. |
| 11 | `deudor.cupo_otorgado` | **P1** | clientes/views.py:377-397 CuposCompradoresNew | Otorgamiento de cupo por deudor (concentración). | cupo_id, cliente_id, comprador_id, ncupocartera, cxtipocupo, cxmoneda, lsenotifica | Enviar carta de cupo/notificación al deudor y recalcular la concentración de cartera por deudor. |
| 12 | `deudor.cupo_modificado` | **P1** | clientes/views.py:405-429 CuposCompradoresEdit | Modificación del cupo por deudor. | cupo_id, cliente_id, comprador_id, cupo_anterior, cupo_nuevo, utilizadocartera | Recalcular concentración y alertar si un deudor supera el porcentaje máximo de la cartera. |
| 13 | `deudor.cupo_eliminado` | **P2** | clientes/views.py:1186 EliminarCupoComprador | Retiro del cupo de un deudor. | cupo_id, cliente_id, comprador_id | Bloquear nuevas facturas de ese deudor y notificar al área comercial. |
| 14 | `deudor.cupo_por_agotar` | **P1** | clientes/models.py:242 Cupos_compradores (ncupocartera vs nutilizadocartera) | Umbral configurable de consumo del cupo del deudor. | cupo_id, comprador_id, ncupocartera, nutilizadocartera, porcentaje | Alertar a riesgo y comercial; generar solicitud de ampliación de cupo al deudor. |
| 15 | `cliente.cuenta_bancaria_registrada` | **P1** | clientes/views.py:102-139 CuentasBancariasNew | Alta de cuenta bancaria del cliente. | cuenta_id, cliente_id, banco, cxcuenta, tipo_cuenta(A|C), lpropia, cxidpropietario, ctnombrepropietario | Validar titularidad y estado de la cuenta; alerta antifraude si el titular no coincide con el RUC del cliente. |
| 16 | `cliente.cuenta_bancaria_eliminada` | **P1** | clientes/views.py:1100-1113 EliminarCuentaBancaria | Baja de cuenta bancaria (arrastra Cuenta_transferencia). | cuenta_id, cliente_id, banco, cxcuenta, usuario | Auditoría de cambios bancarios: alerta al oficial de cumplimiento ante bajas inesperadas. |
| 17 | `cliente.cuenta_transferencia_actualizada` | **P0** | clientes/views.py:1147 ActualizarCuentaTransferencia | Cambio de la cuenta destino por defecto para desembolsos. | cliente_id, cuenta_id, banco, cxcuenta, cuenta_anterior | ALERTA ANTIFRAUDE obligatoria: cambio de cuenta de desembolso exige doble confirmación (OTP) antes de liberar pagos. |
| 18 | `deudor.cuenta_bancaria_registrada` | **P2** | clientes/views.py:216-245 CuentasBancariasDeudorNew | Alta de cuenta del deudor para recaudo. | cuenta_id, comprador_id, banco, cxcuenta, tipo_cuenta | Preparar domiciliación/recaudo y validar la cuenta contra el RUC del deudor. |
| 19 | `cliente.datos_operativos_actualizados` | **P1** | operaciones/views.py:799 DatosOperativos (+ Datos_operativos_hist) | Cambio de tasas, porcentaje de anticipo, clase o estado operativo del cliente. | cliente_id, nporcentajeanticipo, ntasacomision, ntasadescuentocartera, ntasagaoa, ntasamora, cxclase, cxestado | Versionar el tarifario por cliente y notificar al ejecutivo comercial y a riesgo de las nuevas condiciones. |
| 20 | `cliente.estado_operativo_cambiado` | **P0** | operaciones/models.py:47 Datos_operativos.cxestado (A/B/I/P/L/X/C) | Cambio de estado operativo: Activo, Baja, Inactivo, Pre legal, Legal, Bloqueado, Cartera castigada. | cliente_id, estado_anterior, estado_nuevo, clase, usuario, motivo | Bloquear o rehabilitar la operación; si pasa a Pre legal/Legal, abrir expediente con el abogado; si a Bloqueado, avisar a todo el equipo. |
| 21 | `cliente.tasas_actualizadas_masivamente` | **P1** | clientes/views.py:1521,1570 CambiarTasaGAOA_todos / CambiarTasaMora_todos | Actualización masiva de tasas GAO/GAOA o de mora para todos los clientes. | usuario, tasa_anterior, tasa_nueva, clientes_afectados, tipo_tasa | Registrar el cambio como evento de gobierno de precios, notificar a gerencia y generar comunicación a los clientes afectados. |

### Dominio 3 — Operaciones: Liquidación, Desembolso, Cartera y Pagarés

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `operacion.condiciones_calculadas` | **P1** | operaciones/views.py:1061 DetalleCargosAsignacion → 1177 CalcularCargosPorDocumento | Cálculo de anticipo, GAO, descuento de cartera e IVA por documento. | asignacion_id, documento_id, nplazo, nporcentajeanticipo, ntasacomision, ntasadescuento, nanticipo, ngao, ndescuentodecartera, condicion_operativa_id | Control de política: alertar si el anticipo supera el 80 % o si la tasa aplicada está fuera del rango autorizado para la clase del cliente. |
| 2 | `operacion.totales_calculados` | **P2** | operaciones/views.py:1358 SumaCargos | Totalización de la liquidación: negociado, anticipo, GAO, DC, bases de IVA, IVA y neto. | asignacion_id, nvalor, nanticipo, ngao, ndescuentodecartera, notroscargos, nbaseiva, nbasenoiva, niva, neto | Enviar resumen de liquidación a Slack/WhatsApp del comité para visto bueno antes de desembolsar. |
| 3 | `operacion.tasa_documento_editada` | **P0** | operaciones/views.py:1427 EditarTasasDocumentoSolicitud · cobranzas/views.py:3915 | Override manual de tasas sobre un documento (excepción a la política de precios). | documento_id, asignacion_id, tasas_anteriores, tasas_nuevas, usuario, motivo | Registrar la excepción, notificar a riesgo y exigir justificación documentada si supera un umbral de desvío. |
| 4 | `operacion.liquidada` | **P0** | operaciones/views.py:1510 AceptarDocumentos → uspLiquidarAsignacion · cxestado='L' | La negociación queda liquidada: se crean asignación, documentos definitivos, cargos, línea y contabilidad. | asignacion_id, cxasignacion, cliente_id, nvalor, nanticipo, neto, ddesembolso, documentos[], resultado_sp | Crear la tarjeta de operación en el CRM, agendar el desembolso y notificar a contabilidad para el registro del devengo. |
| 5 | `operacion.liquidacion_reversada` | **P0** | operaciones/views.py:1741 ReversaAceptacionAsignacion → uspreversaliquidacionasignacion | Reversa de la liquidación de una asignación. | asignacion_id, cliente_id, usuario, resultado_sp, excesos_eliminados | Alerta a tesorería y contabilidad, y registro de auditoría con el motivo de la reversa. |
| 6 | `operacion.desembolsada` | **P0** | operaciones/views.py:697 DesembolsarAsignacion → uspdesembolsarasignacion · cxestado='P' | Pago al cliente: crea Desembolsos y marca la asignación como Pagada. | asignacion_id, desembolso_id, cliente_id, nvalor(neto), cxformapago, beneficiario, cuenta_origen, cuenta_destino, ddesembolso | Avisar al cliente por WhatsApp y email con el comprobante y la fecha valor; actualizar el flujo de caja del día. |
| 7 | `operacion.desembolso_efectivo` | **P1** | operaciones/views.py:697 (cxformapago='EFE') | Desembolso en efectivo. | desembolso_id, cliente_id, nvalor, beneficiario, caja | Exigir aprobación adicional por monto y registrar la entrega con evidencia (foto/firma) en el expediente. |
| 8 | `operacion.desembolso_cheque_emitido` | **P1** | operaciones/views.py:752 (cxformapago='CHE') | Emisión de cheque para el desembolso. | desembolso_id, ctbeneficiario, cxbeneficiario, cuenta_origen, nvalor, n_cheque | Encolar la impresión del cheque, controlar la numeración y confirmar la entrega con acuse. |
| 9 | `operacion.desembolso_transferencia_ejecutada` | **P0** | operaciones/views.py:756 (cxformapago='TRA') | Transferencia al cliente (usa Cuenta_transferencia del cliente). | desembolso_id, cuenta_destino, banco, nvalor, cuenta_origen | Generar el archivo de transferencia para el banco y enviar el comprobante al cliente. |
| 10 | `operacion.desembolso_reversado` | **P0** | operaciones/views.py:2629 ReversoDesembolsoAsignacion | Reversa del desembolso de una asignación. | desembolso_id, asignacion_id, cliente_id, nvalor, usuario | Bloquear la conciliación bancaria, alertar a tesorería y verificar si el dinero ya salió de la cuenta. |
| 11 | `operacion.desembolso_archivo_banco_generado` | **P2** | operaciones/models.py:2025 Desembolsos.lgeneradoarchivobanco | Se marca que se generó el archivo bancario del desembolso (hoy es solo un booleano). | desembolso_id, nvalor, cxformapago, cuenta_origen, nombre_archivo | Subir el archivo al repositorio, enviarlo al banco por canal seguro y registrar el acuse de recibo. |
| 12 | `operacion.desembolso_contabilizado` | **P2** | operaciones/models.py:2026-2029 Desembolsos.lcontabilizado / cxasiento | El desembolso queda contabilizado (O2O con contabilidad.Diario_cabecera). | desembolso_id, asiento_id, cxtransaccion, dcontabilizado, nvalor | Cotejar con el ERP, verificar el cuadre del asiento y alertar si quedan desembolsos sin contabilizar al cierre del día. |
| 13 | `operacion.anexo_generado` | **P1** | operaciones/views.py:2351 GenerarAnexo (docxtpl) | Generación del anexo/contrato en Word desde la plantilla del tipo de cliente. | asignacion_id, anexo_id, cliente_id, deudor_id, total_deudor, url_documento | Enviar a firma electrónica, archivar el documento firmado y verificar que el expediente quede completo. |
| 14 | `operacion.cesion_facturas_notificada` | **P0** | operaciones/views.py:2454-2457 (Anexos.lcesionfacturas → Documentos.lnotificaciongenerada) | Se marca la cesión de facturas para notificar (hoy solo genera el .docx, sin envío ni acuse). | asignacion_id, cliente_id, deudor_id, documentos[], fecha_cesion | **Cerrar el ciclo legal**: enviar la notificación de cesión al deudor, exigir acuse de recibo, registrar la fecha y reintentar si no responde en 48 h. |
| 15 | `operacion.anexos_marcados_impresos` | **P3** | operaciones/views.py:2475 MarcarAnexoGenerado (lanexosimpresos) | Se marca el expediente de anexos como impreso/completo. | asignacion_id, usuario | Checklist de expediente completo por operación y semáforo de operaciones con documentación pendiente. |
| 16 | `operacion.pagare_importado` | **P1** | operaciones/views.py:2503 ImportarOperacion (secuencia PAGARE) | Reestructuración: alta del pagaré y sus cuotas a partir de XML. | pagare_id, cxpagare, cliente_id, ncapital, ninteres, ntasainteres, nplazo, ncantidadcuotas, dvencimiento, cuotas[] | Notificar al cliente el calendario de pagos y programar los recordatorios de cada cuota. |
| 17 | `operacion.pagare_aceptacion_reversada` | **P1** | operaciones/views.py:2615 ReversaAceptacionPagare | Reversa de la aceptación del pagaré. | pagare_id, asignacion_id, cliente_id, usuario | Restaurar el cupo consumido, avisar a contabilidad y anular los recordatorios de cuotas. |
| 18 | `operacion.linea_reestructuracion_consumida` | **P1** | operaciones/views.py:2568-2572 (Linea_Factoring.nreestructuracion += total) | Consumo de línea por reestructuración de cartera. | cliente_id, total_reestructurado, nreestructuracion, disponible | Alerta temprana de deterioro del cliente: si la reestructuración crece, escalar a riesgo y revisar la clase. |
| 19 | `operacion.cuota_pagare_reprogramada` | **P1** | operaciones/views.py:2683 ModificarCuota | Cambio de la fecha de pago de una cuota del pagaré. | cuota_id, ncuota, dfechapago_anterior, dfechapago_nueva, pagare_id, cliente_id | Reprogramar los recordatorios de cobro y registrar la reprogramación como señal de riesgo de pago. |
| 20 | `cartera.revision_generada` | **P0** | operaciones/views.py:2787 NuevaRevisionCarteraJSON (Revision_cartera + detalle) | Corrida de revisión de cartera con buckets de antigüedad y clase/estado sugeridos. | revision_id, cliente_id, nvencido30, nvencido60, nvencidomas60, nvencido90, nvencidomas90, nporvencer, nprotesto, nlineaactual, ctclaseactual, ctestadoactual, jdetalle | Generar el paquete de comité de riesgo (Excel + email) y proponer en automático el cambio de clase o de cupo. |
| 21 | `cartera.revision_comentada` | **P2** | operaciones/views.py:535 RevisionCarteraClienteEdit (ctcomentario) | El analista comenta un cliente dentro de la revisión de cartera. | revision_id, cliente_id, ctcomentario, usuario | Abrir una tarea de seguimiento asignada al analista y notificar al oficial de crédito. |
| 22 | `cartera.provision_calculada` | **P0** | operaciones/views.py:3234 GeneraListaCarteraVencidaJSON → Documentos_Manager.provision_cargos | Cálculo de la deuda provisionada: saldo anticipado, DC negociado, DC vencido, GAO adicional e IVA. | documento_id, cliente_id, saldo_anticipado, dc_negociado, dc_vencido, gao_adicional, iva, deuda, dias_vencidos | Generar la nota de débito y el aviso de mora al cliente por email/WhatsApp con el detalle de la deuda. |
| 23 | `cartera.corte_historico_generado` | **P1** | operaciones/views.py:2984 GuardarCorteHistorico → uspguardarcortehistorico | Snapshot histórico de cartera (facturas, protestos, pagarés). | corte_id, ctdescripcion, nvalorfacturas, nvalorprotestos, nvalorpagares, usuario, empresa_id | Publicar el reporte ejecutivo mensual de cartera a dirección y archivar el corte como evidencia. |
| 24 | `cartera.condicion_operativa_actualizada` | **P2** | operaciones/views.py:1560,1707,2318 | Alta, modificación, borrado lógico o inactivación de tramos de condiciones operativas. | condicion_id, ctdescripcion, tipo_factoring, tramos[{plazodesde,plazohasta,anticipo,tasadescuento,tasagao}], clases, lactiva | Recalcular el simulador de tarifas y publicar internamente la nueva tabla de precios por plazo y clase. |
| 25 | `cartera.documento_castigado` | **P2** | operaciones/models.py:762 Documentos.lcastigada · estado cliente 'C' | Castigo de cartera (flag existente pero sin flujo que lo asigne hoy). | documento_id, cliente_id, nsaldo, motivo, usuario, acta_id | Abrir expediente de castigo con acta de comité, registrar la provisión contable y separar la cartera en recuperación extrajudicial. |

### Dominio 4 — Cobranzas, Cheques y Protestos

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `cobranza.factura_por_vencer` | **P0** | cobranzas/webhooks.py:13 facturas_por_vencer · views.py:77 DocumentosPorVencerView | Facturas con vencimiento dentro del rango de días solicitado (vencimiento efectivo = dvencimiento + ndiasprorroga). | empresa_id, dias, clientes[{nombre, celular, facturas[{numero, fecha_vencimiento, saldo}]}] | Secuencia de recordatorios escalonada a 7/3/1 días al cliente y al deudor por WhatsApp con enlace de pago. |
| 2 | `cobranza.factura_vencida` | **P0** | cobranzas/views.py:50 DocumentosVencidosView · operaciones/models.py:793 vencimiento() | Factura que superó su fecha de vencimiento efectivo con saldo pendiente. | documento_id, ctdocumento, cliente_id, deudor_id, nsaldo, dvencimiento, dias_vencidos | Registrar la gestión de cobro, asignar al cobrador y disparar el primer contacto automático. |
| 3 | `cobranza.cheque_por_depositar` | **P0** | cobranzas/views.py:104,1218 ChequesADepositarView | Cheque accesorio próximo a vencer y pendiente de depósito. | accesorio_id, cliente_id, banco, ctcuenta, ctcheque, ctgirador, ntotal, dvencimiento | Avisar a tesorería y agendar el depósito; generar la papeleta y confirmar acreditación. |
| 4 | `cobranza.cheque_depositado` | **P1** | cobranzas/views.py:1262,1311 DepositoCheques → uspDepositarChequesAccesorios | Depósito de cheques accesorios en cuenta de la empresa o cuenta conjunta. | ids_cheques[], cuenta_destino(CE|CC), ddeposito, total, usuario | Conciliar con el extracto bancario y confirmar la acreditación por cada cheque depositado. |
| 5 | `cobranza.cheque_canjeado` | **P1** | cobranzas/views.py:3371 CanjeDeCheque | Canje de un cheque por otro (Cheques_canjeados + nuevo ChequesAccesorios). | accesorio_original, accesorio_nuevo, ctmotivocanje, banco, ntotal, dvencimiento | Llevar el historial de cheques rechazados o canjeados por deudor y ajustar su score de comportamiento. |
| 6 | `cobranza.accesorio_quitado` | **P1** | cobranzas/views.py:3471 QuitarAccesorio | Retiro de un cheque accesorio de la cartera (pasa a Cheques_quitados). | accesorio_id, cliente_id, ctmotivoquitado, nsaldo | Notificar el cambio de garantía al comité y reconvertir el saldo en factura pendiente de cobro. |
| 7 | `cobranza.documento_prorrogado` | **P1** | cobranzas/views.py:3864 Prorroga (ndiasprorroga / ncontadorprorrogas) | Prórroga del vencimiento de un documento. | documento_id, cliente_id, ndiasprorroga, dvencimiento_nuevo, ncontadorprorrogas, usuario | Reproyectar el flujo de caja de cobros y registrar la prórroga como señal de riesgo de pago. |
| 8 | `cobranza.ampliacion_plazo_registrada` | **P0** | cobranzas/views.py:3990 AceptarAmpliacionDePlazo → uspAmpliacionDePlazo | Ampliación formal de plazo con comisión, descuento de cartera e IVA, y nota de débito tipo 'A'. | ampliacion_id, cliente_id, dampliacionhasta, ncomision, ndescuentodecartera, niva, nvalor, documentos[], nota_debito_id | Emitir y enviar la nota de débito/factura de la comisión de prórroga y notificar al cliente las nuevas condiciones. |
| 9 | `cobranza.ampliacion_plazo_revertida` | **P1** | cobranzas/views.py:4362 ReversaAmpliacion → uspReversarAmpliacionDePlazo | Reversa de una ampliación de plazo. | ampliacion_id, cliente_id, usuario, resultado_sp | Revertir la nota de débito, restaurar el vencimiento anterior y avisar a contabilidad. |
| 10 | `cobranza.registrada` | **P0** | cobranzas/views.py:1157,1205 AceptarCobranza → uspAceptarCobranzaCartera | Registro de una cobranza de cartera con aplicación por documento. | cobranza_id, cxcobranza, cliente_id, cxformapago, nvalor, dcobranza, nsobrepago, documentos[{documento_id, nvalorcobranza, nretenciones, ndiasacondonar}], cxcheque, cuenta_deposito, cuenta_conjunta | Avisar a contabilidad y al canal de Slack de cobranzas; actualizar la cartera y el disponible de la línea en tiempo real. |
| 11 | `cobranza.confirmada` | **P1** | cobranzas/views.py:1641 ConfirmarCobranza (cxestado='C') | Confirmación de la cobranza registrada (requerida para TRA/CHE/DEP). | cobranza_id, cxcobranza, nvalor, ddeposito, cxcuentadeposito, usuario | Liberar la cobranza para liquidación y disparar la conciliación bancaria del depósito. |
| 12 | `cobranza.confirmacion_revertida` | **P0** | cobranzas/views.py:1777 ReversaConfirmacionCobranza | Reversa de la confirmación de una cobranza (también desactiva el movimiento de cuenta conjunta). | cobranza_id, cxcobranza, tenia_cuenta_conjunta, usuario, motivo | ALERTA de control interno: cobranza confirmada y luego revertida es un patrón típico de fraude; notificar a auditoría. |
| 13 | `cobranza.cobranza_cuenta_conjunta` | **P1** | cuentasconjuntas/views.py:115,343 AceptarConfirmacion → uspConfirmarCobranzaCuentaConjunta | Confirmación de cobranza depositada en cuenta conjunta, con transferencia y/o cargo. | tipo_operacion, cobranza_id, transferencia{nvalor, ndevolucion, cuenta_origen, cuenta_destino, dmovimiento}, cargo{nvalor, ctmotivo, dmovimiento} | Notificar al cliente el depósito en su cuenta compartida con el detalle de transferencia y cargos aplicados. |
| 14 | `cobranza.protesto_registrado` | **P0** | cobranzas/views.py:2064,2089 AceptarProtesto → uspRegistroProtesto | Protesto de cheque: crea Cheques_protestados, Documentos_protestados y la nota de débito; la cobranza pasa a 'P'. | protesto_id, cobranza_id, cheque_id, cliente_id, deudor_id, dprotesto, motivoprotesto, lresponsabilidadgirador, nvalor, nvalorcartera, documentos[] | Abrir caso legal en automático, notificar al deudor el protesto por WhatsApp/carta y alertar al comité de riesgo. |
| 15 | `cobranza.protesto_revertido` | **P1** | cobranzas/views.py:3345,3360 ReversaProtesto → uspReversaProtesto | Reversa de un protesto registrado. | protesto_id, cheque_id, usuario, resultado_sp | Cerrar el caso legal, revertir las alertas y auditar el motivo de la reversa. |
| 16 | `cobranza.recuperacion_protesto_registrada` | **P0** | cobranzas/views.py:2241,2290 AceptarRecuperacion → uspAceptarRecuperacionProtesto | Recuperación de cartera protestada (pago total o parcial). | recuperacion_id, cxrecuperacion, cliente_id, nvalor, nsobrepago, protestos[{protesto_id, nvalorrecuperacion, nsaldoaldia, ndiasacondonar}] | Actualizar la cartera protestada, avisar al deudor y al abogado, y evaluar el cierre del caso. |
| 17 | `cobranza.protesto_saldado` | **P2** | cobranzas/views.py:2420-2433 (Cheques_protestados.nsaldocartera → 0) | Cheque protestado completamente saldado. | protesto_id, cheque_id, cliente_id, nvalorcartera, dultimacobranza | Cerrar el caso y liberar la provisión; reconocer al deudor que regularizó su situación. |
| 18 | `cobranza.liquidacion_generada` | **P0** | cobranzas/views.py:1913,1944 Liquidacion → uspLiquidarCobranzas | Liquidación de cobranzas/recuperaciones con GAO, GAOA, DC, DC vencido, retenciones, bajas, IVA y neto. | liquidacion_id, cliente_id, cxtipooperacion(R|C), nvuelto, nsobrepago, ngao, ngaoa, ndescuentodecartera, ndescuentodecarteravencido, nretenciones, nbajas, notroscargos, nbaseiva, nbasenoiva, niva, nneto, jcobranzas, jotroscargos | Enviar el PDF de liquidación al cliente por email y WhatsApp, y registrar la rentabilidad por cliente en el tablero. |
| 19 | `cobranza.liquidacion_en_negativo` | **P0** | cobranzas/views.py:646 LiquidacionesEnNegativoPendientesView (Notas_debito nsaldo>0) | Liquidación en negativo: el cliente queda debiendo cargos (cobranza pendiente o nota de débito). | nota_debito_id, cxnotadebito, cliente_id, cxtipooperacion, nvalor, nsaldo, dnotadebito | Cobrar la diferencia con nota de débito o debitar la cuenta conjunta, con aviso previo al cliente. |
| 20 | `cobranza.liquidacion_desembolsada` | **P0** | cobranzas/views.py:1963-2038 DesembolsarCobranzas (ldesembolsada=True, cxestado='P') | Pago al cliente del neto de la liquidación de cobranzas, creando operaciones.Desembolsos tipo 'C'. | liquidacion_id, desembolso_id, cliente_id, neto, cxformapago, beneficiario, cuenta, ddesembolso | Avisar al cliente el pago del excedente y programar la transferencia bancaria. |
| 21 | `cobranza.desembolso_revertido` | **P1** | cobranzas/views.py:4323 ReversoDesembolsoLiquidacion | Reversa del desembolso de una liquidación (bloqueado si está contabilizada o facturada). | liquidacion_id, desembolso_id, cliente_id, nvalor, usuario | Alertar a tesorería y controlar que no exista un pago duplicado. |
| 22 | `cobranza.cobranza_revertida` | **P0** | cobranzas/views.py:2847 ReversaCobranza (enruta por prefijo CC/C/R/P) | Reversa de una cobranza según su tipo (cargos, cartera, recuperación o pagaré). | cobranza_id, cxcobranza, tipo_operacion, usuario, motivo, resultado_sp | Notificar la corrección al cliente, ajustar el asiento contable y registrar el evento de auditoría. |
| 23 | `cobranza.liquidacion_revertida` | **P1** | cobranzas/views.py:2827,2838 ReversaLiquidacion → uspReversaLiquidarCobranzas | Reversa de una liquidación de cobranzas. | liquidacion_id, cliente_id, usuario, resultado_sp | Reprocesar la liquidación, avisar a contabilidad y bloquear el desembolso asociado. |
| 24 | `cobranza.cargos_registrados` | **P1** | cobranzas/views.py:3079 AceptarCobranzaNotasDebito → uspAceptarCobranzaCargos | Cobranza de notas de débito / otros cargos. | cobranza_id, cxcobranza, cliente_id, nvalor, nsobrepago, cargos[{nota_debito_id, nvalor}], cuenta_deposito | Cerrar las notas de débito pendientes y conciliar contra el movimiento bancario. |
| 25 | `cobranza.cuota_pagare_cobrada` | **P1** | cobranzas/views.py:4273 AceptarCobranzaCuota → uspAceptarCobranzaCuota | Cobro de una cuota de pagaré. | pagare_cabecera_id, cuota_id, cliente_id, nvalorcobranza, nvaloraplicainteres, nsaldoaldia | Confirmar al cliente el pago recibido y reprogramar el recordatorio de la siguiente cuota. |
| 26 | `cobranza.dias_condonados` | **P0** | cobranzas/views.py:925,1735 CobranzaPorCondonar / DatosDiasACondonar | Condonación de días de mora con registro de usuario autorizante. | cobranza_id, liquidacion_id, ndiasacondonar, cxusuariocondona, valor_condonado, tipo_operacion | Control de excepciones: exigir aprobación de supervisor por encima de un monto y medir la condonación acumulada por cobrador. |
| 27 | `cuentaconjunta.debito_registrado` | **P1** | cuentasconjuntas/views.py:186,384 DebitoBancarioEdit / DebitoBancarioSinCobranza | Débito a la cuenta conjunta del cliente (con o sin cobranza asociada). | cuentabancaria_id, cliente_id, dmovimiento, nvalor, ctmotivo, nota_debito_id, cargos_detalle | Avisar al cliente el débito aplicado y su saldo pendiente, y conciliar contra la nota de débito. |
| 28 | `cuentaconjunta.nota_debito_eliminada` | **P1** | cuentasconjuntas/views.py:431 EliminarNotaDebito | Eliminación de una nota de débito en cuenta conjunta. | nota_debito_id, cliente_id, nvalor, usuario, motivo | Reversar el movimiento contable y auditar la eliminación con doble visto bueno. |
| 29 | `cuentaconjunta.transferencia_creada` | **P1** | cuentasconjuntas/views.py:497 DatosTransferencia | Transferencia de la cuenta conjunta hacia una cuenta de la empresa. | transferencia_id, cuentabancaria_id, cuenta_empresa, nvalor, ndevolucion, dmovimiento | Conciliar la transferencia con el extracto bancario y registrar la devolución al cliente. |
| 30 | `cuentaconjunta.transferencia_eliminada` | **P1** | cuentasconjuntas/views.py:459 EliminarTransferencia | Eliminación de una transferencia de cuenta conjunta. | transferencia_id, cliente_id, nvalor, usuario | Auditoría de movimientos eliminados y verificación bancaria de que el dinero no salió. |
| 31 | `cobranza.gestion_cobro_abierta` | **P0** | cobranzas/views.py:4490 Registra_gestion_cobro (cxestado='P') | Apertura de una gestión de cobro sobre la revisión de cartera de un cliente/deudor. | gestion_id, revision_cartera_detalle_id, cxtipoparticipante(C|D), cliente_id, ctnumerowhatsapp, buckets_vencido, nporvencer, nprotesto, nlineaactual, ctclaseactual, ctestadoactual | Asignar la tarea al cobrador en el turno, notificar por Slack y calcular el SLA de primer contacto. |
| 32 | `cobranza.gestion_cobro_contactada` | **P1** | api/twilio_service.py:51-74 (Gestion_cobro 'P'→'A') | Primer contacto efectivo por WhatsApp sobre la gestión de cobro. | gestion_id, whatsapp_destino, ctsid, ctstatus, ctbody, tiempo_hasta_contacto_horas | Medir tiempo de respuesta del cobrador y programar el siguiente contacto si no hay respuesta del deudor. |
| 33 | `cobranza.whatsapp_recibido` | **P0** | api/twilio_service.py:100-133 webhook_whatsapp_twilio | Mensaje entrante del deudor o cliente en el hilo de cobranza. | ctfrom, ctto, ctbody, ctsid, ctstatus, ctdirection, gestion_cobro_id, jcontexto | Clasificar la intención con IA (promesa de pago, disputa, consulta, número equivocado) y crear la tarea o respuesta correspondiente. |

### Dominio 5 — Contabilidad, Facturación Electrónica y Cierre

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `contabilidad.factura_venta_generada` | **P0** | contabilidad/views.py:1458 GenerarFactura → uspGenerarFacturaContabilidad | Generación de factura de venta al cliente por comisiones, cargos y otros conceptos. | factura_id, cxnumerofactura, cxtipooperacion(LA|LC|AP|VF|CP), cliente_id, demision, nbasenoiva, nbaseiva, niva, nvalor, operacion, asiento_id | Emitir PDF/RIDE, enviar por email al cliente y encolar la generación del XML electrónico. |
| 2 | `contabilidad.factura_al_vencimiento_generada` | **P1** | contabilidad/views.py:2340 GenerarFacturasAlVencimientoDiario → uspGenerarFacturasAlVencimiento | Emisión de la factura al vencimiento de la operación. | factura_id, documento_id, cliente_id, nvalor, niva, cxtipooperacion | Avisar al deudor y programar el cobro de esa factura; adjuntar el XML autorizado en el mismo correo. |
| 3 | `contabilidad.xml_electronico_generado` | **P0** | contabilidad/sri.py:15 GeneraXMLFactura (ldocumentoelectronicogenerado) | Generación del XML de factura con clave de acceso (módulo 11). Hoy no se firma ni se envía al SRI. | factura_id, clave_acceso, ambiente, punto_emision, cxtipodocumento, nvalor | **Completar la cadena**: firmar XAdES, enviar a Recepción del SRI y hacer seguimiento hasta la autorización. |
| 4 | `contabilidad.comprobante_recibido_sri` | **P0** | api/sri.py:180 consulta_estado_comprobante_sri (estado AUTORIZADO / rechazado) | Resultado de la consulta del comprobante en el SRI (AutorizacionComprobantesOffline). | clave_acceso, estado, numero_autorizacion, fecha_autorizacion, ambiente, mensajes[], comprobante_xml | Si AUTORIZADO: enviar PDF+XML al deudor y archivar en el repositorio. Si RECHAZADO: alerta a contabilidad y reintento. |
| 5 | `contabilidad.comprobante_retencion_recibido` | **P0** | Retenciones hoy se digitan a mano (solicitudes/forms.py:50,61-62) | Evento propuesto: detección/recepción de comprobante de retención del deudor desde el correo. | cliente_id, deudor_id, numero_retencion, fecha, nretencioniva, nretencionrenta, clave_acceso, documento_relacionado | Leer el comprobante, aplicarlo automáticamente contra la factura y generar el asiento de retención. |
| 6 | `contabilidad.asiento_generado` | **P2** | contabilidad/views.py:1809 AsientoDiario | Registro de un asiento contable manual (Diario_cabecera + Transaccion). | diario_id, cxtransaccion, dcontabilizado, ctconcepto, nvalor, n_lineas, empresa_id, usuario | Sincronizar con el ERP y validar el cuadre debe/haber con alerta si el asiento queda descuadrado. |
| 7 | `contabilidad.asiento_reversado` | **P1** | contabilidad/views.py:2151 ReversarAsiento | Reversa de un asiento contable. | diario_id, cxtransaccion, usuario, concepto, motivo | Notificar a auditoría y registrar el evento en un log inmutable con el asiento original. |
| 8 | `contabilidad.asientos_cobranzas_generados` | **P1** | contabilidad/views.py:2271 → uspGenerarAsientosCobranzas | Generación masiva de asientos de cobranzas y cuotas de pagaré. | ids[], usuario, n_asientos, total, empresa_id | Conciliar contra bancos y alertar descuadres entre lo cobrado y lo contabilizado. |
| 9 | `contabilidad.asientos_protestos_generados` | **P1** | contabilidad/views.py:2486 | Generación masiva de asientos de cheques protestados. | ids[], n_asientos, total_protestado, usuario | Activar el flujo legal/judicial y actualizar el score del deudor moroso. |
| 10 | `contabilidad.asientos_recuperaciones_generados` | **P2** | contabilidad/views.py:2610 | Generación masiva de asientos de recuperaciones. | ids[], n_asientos, total_recuperado, usuario | Cerrar los casos de protesto recuperados y liberar provisiones. |
| 11 | `contabilidad.asientos_transferencias_generados` | **P2** | contabilidad/views.py:2545 | Generación masiva de asientos de transferencias de cuentas conjuntas. | ids[], n_asientos, total, cuenta_destino, usuario | Verificar la acreditación bancaria real y conciliar la devolución al cliente. |
| 12 | `contabilidad.comprobante_egreso_generado` | **P1** | contabilidad/views.py:1616 GenerarEgreso → GenerarEgresoDiario:1757 | Emisión de comprobante de egreso (caja/banco) con forma de pago. | egreso_id, cxformapago(EFE|CHE|TRA|TRN|DEB), cxbeneficiario, ctbeneficiario, nvalor, ctcheque, cuenta_bancaria, asiento_id | Enviar la orden de pago al banco, imprimir/enviar el cheque y registrar el acuse del beneficiario. |
| 13 | `contabilidad.mes_cerrado` | **P1** | contabilidad/views.py:2291 CierreDeMes → uspBloqueoMesContabilidad · Control_meses.lbloqueado | Cierre del mes contable (bloqueo del período). | año, mes, usuario, empresa_id, n_asientos, total_debe, total_haber | Congelar el período, generar el paquete de estados financieros (balance, P&G, libro mayor) y enviarlo a gerencia y al contador externo. |
| 14 | `contabilidad.mes_desbloqueado` | **P0** | contabilidad/views.py:2629 DesbloqueoDeMes | Desbloqueo de un mes contable previamente cerrado. | año, mes, usuario, empresa_id, motivo | Alerta de control interno a auditoría: reapertura de período cerrado siempre debe justificarse. |
| 15 | `contabilidad.saldos_actualizados` | **P3** | contabilidad/views.py:2290,2628 (Saldos / Saldos_gyp) | Actualización de saldos por cuenta y año / saldos de pérdidas y ganancias. | año, cuenta_id, ndebe, nhaber, usuario | Publicar el tablero financiero diario y alertar variaciones anómalas por cuenta. |
| 16 | `contabilidad.analisis_ia_factura_completado` | **P0** | api/views.py:329 InvoiceAIAnalysis.objects.create (OpenAI gpt-4.1) | Análisis de riesgo de una factura/documento con IA: nivel BAJO/MEDIO/ALTO y recomendación. | invoice_id, risk_level, analysis_text, recommendation, cliente_id, raw_response | Si risk_level=ALTO: Slack a riesgo, bloquear la asignación y exigir doble aprobación; si BAJO, auto-avanzar. |

### Dominio 6 — Plataforma, Configuración, Seguridad y Comercial (Premium)

| # | Evento (`entidad.accion`) | Prioridad | Disparador en el código | Qué informa | Payload (campos disponibles) | Automatización n8n objetivo |
|---|---|---|---|---|---|---|
| 1 | `plataforma.empresa_datos_actualizados` | **P1** | empresa/views.py:501 DatosEmpresaEdit | Cambio de datos de la empresa: RUC, razón social, ambiente SRI, IVA, logos. | empresa_id, campos_modificados, ambientesri, nporcentajeiva, ctruccompania, usuario | Versionar el cambio y alertar si se modifica el RUC o el ambiente SRI (impacta facturación electrónica). |
| 2 | `plataforma.tipo_factoring_configurado` | **P2** | empresa/views.py:44-95 (ltipofactoringconfigurado=True) | Alta/edición de tipos de factoring con sus políticas y cuentas. | tipo_factoring_id, cttipofactoring, ctabreviacion, cxmoneda, ndiasgracia, nporcentajeretencionenfactura, politicas{}, usuario | Validar que existan las cuentas contables asociadas y avisar a contabilidad antes de permitir operar con ese tipo. |
| 3 | `plataforma.tasa_factoring_configurada` | **P2** | empresa/views.py:131-195 (ltasasfactoringconfiguradas=True) | Alta/edición de tasas de factoring (flat, periodicidad, IVA, sobre anticipo). | tasa_id, cxtasa, lflat, ndiasperiocidad, lcargaiva, lsobreanticipo, usuario | Recalcular los simuladores de precio y publicar la tabla vigente al equipo comercial. |
| 4 | `plataforma.otro_cargo_configurado` | **P2** | empresa/views.py:557-630 OtroCargoNew/Edit | Alta/edición de otros cargos (con IVA, en liquidación de asignación o de cobranza). | cargo_id, ctabreviacion, nvalor, lcargaiva, lcargaenliquidacionasignacion, lcargaenliquidacioncobranza, lactivo | Avisar a contabilidad y comercial del cambio de cargos y actualizar las cotizaciones del CRM. |
| 5 | `plataforma.cuenta_bancaria_empresa_actualizada` | **P1** | empresa/views.py:291-352 CuentaBancariaNew/Edit | Alta/edición de cuenta bancaria de la empresa (incluye ruta de archivo bancario). | cuenta_id, banco, cxcuenta, ctrutaarchivobanco, limprimecheque, lactiva, usuario | Alerta de cumplimiento y actualización de la configuración de pagos masivos. |
| 6 | `plataforma.funcionario_creado` | **P2** | empresa/views.py:723-768 FuncionariosNew/Edit | Alta/edición de funcionario con esquema de comisión (%, flat, periodicidad, base). | funcionario_id, cxfuncionario, ctfuncionario, nporcentajecomision, lcomisionflat, nperiocidadcomision, lcomisionsobregao, lcomisionsobredescuentocartera | Alta en el cálculo de comisiones, notificación al funcionario y publicación del tarifario comercial. |
| 7 | `plataforma.punto_emision_creado` | **P2** | empresa/views.py:448-499 PuntoEmisionNew/Edit | Alta/edición de punto de emisión (establecimiento, secuencias, generación XML). | puntoemision_id, cxestablecimiento, cxpuntoemision, nultimasecuencia, lgeneracionxmldocumentoelectronico, lactiva | Verificar la disponibilidad de secuenciales en el SRI y alertar cuando se agoten. |
| 8 | `plataforma.usuario_creado` | **P2** | bases/views.py:215-292 user_editar / user_password | Creación o edición de usuario del sistema y cambio de contraseña. | user_id, username, email, grupos[], es_nuevo, empresa_id, usuario_ejecutor | Onboarding del usuario (invitación, guía de permisos) y alerta de seguridad al administrador. |
| 9 | `plataforma.permiso_denegado` | **P1** | bases/views.py:47-56 SinPrivilegios.handle_no_permission | Intento de acceso a una vista sin permiso o sin sesión válida. | user_id, username, ruta, metodo, ip, user_agent, empresa_id | Detección de accesos indebidos: 3+ denegaciones en 10 min dispara alerta de seguridad y bloqueo temporal. |
| 10 | `plataforma.cierre_automatico_sin_actividad` | **P0** | Propuesto — hoy no existe scheduler ni cierre de período automático | Evento de plataforma: cierre diario/mensual de procesos que hoy son botones manuales. | empresa_id, proceso(cierre_mes|facturas_vencimiento|asientos|provisiones|recordatorios), resultado, duracion_seg | Orquestar desde n8n el disparo de los procesos manuales (CierreDeMes, GenerarAsientos*, GenerarFacturasAlVencimiento, recordatorios) y reportar el resultado. |
| 11 | `plataforma.tarea_programada_fallida` | **P0** | Propuesto — orquestación n8n sobre endpoints hoy manuales | Fallo de una tarea automatizada de negocio (conciliación, recordatorios, cierre). | proceso, error, timestamp, empresa_id, intento, url_endpoint | Reintento con backoff, escalamiento a soporte y registro del incidente. |
| 12 | `plataforma.disponibilidad_servicio` | **P1** | Propuesto — health check (hoy no existe LOGGING ni health-check) | Monitoreo de disponibilidad del sistema y de las integraciones (SRI, OpenAI, Slack, WhatsApp). | servicio, estado, latencia_ms, codigo_http, timestamp | Aviso de caída a soporte, apertura de incidente y comunicación al cliente si supera el SLA. |
| 13 | `premium.onboarding_cliente_iniciado` | **P0** | Propuesto — paquete premium | Inicio del onboarding automatizado de un nuevo cliente de factoring. | cliente_id, plan, ejecutivo, checklist[{documento, estado, fecha_limite}], canal | Secuencia de bienvenida multicanal, recolección de documentos KYC, firma electrónica y activación de línea. |
| 14 | `premium.kyc_cliente_completado` | **P0** | Propuesto — paquete premium (hoy no hay KYC/AML) | Resultado de la verificación KYC/AML: identidad, RUC en el SRI, listas de control, PEP y beneficiario final. | cliente_id, ruc, resultado, listas_consultadas[], coincidencias[], nivel_riesgo, evidencia_url | Aprobación o rechazo automático del alta, apertura de caso de cumplimiento y archivado de la evidencia. |
| 15 | `premium.score_deudor_calculado` | **P1** | Propuesto — hoy no existe scoring de deudor | Cálculo periódico del score de comportamiento de pago de cada deudor. | comprador_id, score, categoria(A|B|C|D), dias_promedio_pago, protestos_historicos, cheques_rechazados, monto_anual, recomendacion | Actualizar el cupo sugerido por deudor y alertar a riesgo cuando el score cruza un umbral. |
| 16 | `premium.conciliacion_bancaria_completada` | **P0** | Propuesto — hoy no existe conciliación bancaria | Resultado de la conciliación automática entre extracto bancario y movimientos del sistema. | cuenta_bancaria_id, periodo, movimientos_banco, movimientos_sistema, conciliados, diferencias[{fecha, valor, referencia, sugerencia}], archivo_url | Notificar diferencias a tesorería con el detalle y el archivo sugerido de ajuste. |
| 17 | `premium.promesas_pago_seguimiento` | **P0** | Propuesto — hoy Gestion_cobro no tiene fecha/monto comprometido | Registro y seguimiento de la promesa de pago acordada con el deudor. | comprador_id, gestion_id, monto_comprometido, fecha_compromiso, estado(cumplida|incumplida|pendiente), cobrador | Recordatorio al deudor 1 día antes del compromiso y escalamiento automático si incumple. |
| 18 | `premium.sla_operativo_incumplido` | **P0** | Propuesto — usa campos existentes: Niveles_aprobacion.nhorasrespuestamaxima | Incumplimiento de un SLA operativo (aprobación, primer contacto de cobranza, desembolso). | proceso, referencia_id, sla_horas, horas_transcurridas, responsable, nivel_escalamiento | Escalar al jefe del responsable por Slack/WhatsApp y registrar el incumplimiento en el tablero de productividad. |
| 19 | `premium.reporte_ejecutivo_enviado` | **P1** | Propuesto — cortes y revisiones ya existen pero no se distribuyen | Distribución programada de reportes ejecutivos (cartera, mora, producción, rentabilidad). | reporte(cartera|mora|produccion|rentabilidad), periodo, destinatarios[], url_pdf, url_excel, kpis{} | Envío automático semanal/mensual a gerencia y accionistas con KPIs y comparativo contra el período anterior. |

---

**Totales del catálogo:** 135 eventos — P0 (crítico): 51 · P1 (alto): 56 · P2 (medio): 25 · P3 (bajo): 3

---

## 5. Catálogo de workflows n8n del plan premium

Los 22 workflows se agrupan en 5 paquetes funcionales. Cada paquete corresponde a un beneficio que el cliente percibe de inmediato y que hoy **no tiene de ninguna forma**.

### 5.1 Paquete A — Notificaciones y experiencia del cliente (7 workflows)

| # | Workflow | Disparador | Lógica | Beneficio medible |
|---|---|---|---|---|
| A1 | **Acuse de recibo de solicitud** | `solicitud.creada` | WhatsApp + email al cliente con número de solicitud, monto, n.º de facturas y checklist de lo que falta. Adjunta el PDF de la solicitud | Elimina ~80 % de las llamadas "¿recibieron mis facturas?" |
| A2 | **Resolución de aprobación** | `solicitud.aprobada` / `solicitud.rechazada` | Notifica al cliente el resultado con monto neto y fecha estimada de desembolso; si es rechazo, incluye el motivo y qué regularizar | Cierra el ciclo de incertidumbre; reduce desgaste del ejecutivo comercial |
| A3 | **Comprobante de desembolso** | `operacion.desembolsada` | Envía comprobante con valor neto, forma de pago, cuenta destino y fecha valor; registra el acuse en Google Sheets | Evita el "no me llegó la transferencia" |
| A4 | **Recordatorio de vencimiento escalonado** | `cobranza.factura_por_vencer` (cron diario) | Secuencia a 7/3/1 días: WhatsApp al deudor + copia al cliente, con enlace a la factura. Tono escalonado según los días restantes | **El ahorro más grande del paquete**: reduce días de mora |
| A5 | **Aviso de mora con detalle de deuda** | `cartera.provision_calculada` | Envía al cliente y al deudor el desglose: saldo anticipado, DC negociado, DC vencido, GAO adicional e IVA | Reduce disputas por cobros "sin explicación" |
| A6 | **Notificación de cesión al deudor con acuse** ⚖️ | `operacion.cesion_facturas_notificada` | Envía la carta de cesión al deudor, exige acuse de recibo, reintenta a las 48 h, escala al ejecutivo a las 72 h y archiva el acuse | **Cierra el hueco legal más grave del sistema (O-09)** |
| A7 | **Liquidación al cliente** | `cobranza.liquidacion_generada` | Adjunta el PDF de liquidación (GAO/GAOA/DC/retenciones/IVA/neto) y lo archiva en Drive con nombre normalizado | Transparencia del cobro; sustituye el envío manual |

### 5.2 Paquete B — Cobranza inteligente (5 workflows)

| # | Workflow | Disparador | Lógica | Beneficio medible |
|---|---|---|---|---|
| B1 | **Escalamiento automático por tramos de mora** | `contabilidad.cierre_automatico_sin_actividad` (cron diario) + consulta a `facturas_por_vencer` | 1-30 días: WhatsApp al deudor. 31-60: llamada + email formal. 61-90: carta notarial. +90: pre-jurídico. Cada tramo crea la `Gestion_cobro` correspondiente vía API | **Sustituye el botón manual de `Registra_gestion_cobro`** |
| B2 | **Clasificación de respuestas por IA** | `cobranza.whatsapp_recibido` | OpenAI clasifica la intención: promesa de pago, disputa, consulta, número erróneo, pago ya realizado. Enruta al cobrador y crea la tarea | El cobrador deja de leer y triagear mensajes a mano |
| B3 | **Seguimiento de promesas de pago** | `premium.promesas_pago_seguimiento` | Registra monto y fecha comprometidos; recuerda al deudor 1 día antes; si incumple, escala al tramo siguiente | **Cubre la omisión O-17**, hoy inexistente |
| B4 | **Bloqueo preventivo del deudor moroso** | `cobranza.protesto_registrado` + umbral de mora | Cambia `Datos_compradores.cxestado` a `'X'` (Bloqueado) y avisa a riesgo y comercial | Evita seguir financiando a quien no paga |
| B5 | **Tablero diario de cobranza** | cron 07:00 | Arma el Excel del día por cobrador (aging, compromisos de hoy, promesas incumplidas) y lo envía por Slack/email | El equipo arranca el día con la lista lista |

### 5.3 Paquete C — Riesgo, cumplimiento y antifraude (5 workflows)

| # | Workflow | Disparador | Lógica | Beneficio medible |
|---|---|---|---|---|
| C1 | **KYC / AML del cliente y deudor** ⚖️ | `cliente.promovido_desde_solicitante`, `deudor.registrado` | Valida RUC/cédula contra el SRI (`api/sri.py:112`, ya implementado y sin usar), consulta listas de control y PEP, calcula nivel de riesgo y archiva la evidencia | **Cubre O-01 y O-02**: hoy el alta no valida nada |
| C2 | **Validación SRI de la factura** | `solicitud.documento_agregado` | Consulta `AutorizacionComprobantesOffline` por clave de acceso, verifica emisor/receptor/monto/estado y marca la factura como validada | **Cubre O-08 y O-25**: el chequeo en vivo está comentado en el código, y el workflow n8n ya está probado |
| C3 | **Alerta antifraude multicanal** | `solicitud.duplicado_detectado`, `cliente.cuenta_transferencia_actualizada`, `cobranza.confirmacion_revertida`, `operacion.tasa_documento_editada` | Agrupa los 4 patrones de fraude clásico en factoring y alerta a Slack/WhatsApp del comité con doble confirmación por OTP | Detecta los 4 vectores reales de fraude interno y externo |
| C4 | **Scoring de comportamiento del deudor** | cron mensual | Calcula score con días promedio de pago, protestos históricos, cheques canjeados, monto anual y propone cupo sugerido | **Cubre O-03 y O-06**: hoy la decisión es solo `cxclase` + `cxestado` |
| C5 | **Análisis de riesgo con IA** | `contabilidad.analisis_ia_factura_completado` | Si `risk_level = ALTO`, bloquea la asignación, escala a riesgo y exige doble aprobación. Si BAJO, auto-avanza | Aprovecha la integración OpenAI `gpt-4.1` que **ya existe** |

### 5.4 Paquete D — Automatización operativa y contable (3 workflows)

| # | Workflow | Disparador | Lógica | Beneficio medible |
|---|---|---|---|---|
| D1 | **Orquestador de procesos manuales** | cron | Dispara en secuencia lo que hoy son botones: cierre de mes (`CierreDeMes`), generación de asientos (`GenerarAsientos*`), facturas al vencimiento, cortes, provisiones, revisiones de cartera | **Cubre O-31 y resuelve la ausencia total de scheduler** |
| D2 | **Cadena completa de facturación electrónica** ⚖️ | `contabilidad.xml_electronico_generado` | Firma XAdES, envía a Recepción del SRI, hace polling hasta la autorización, archiva XML+RIDE y envía al deudor. Alerta si RECHAZADO | **Cubre O-32**: hoy el XML se genera pero nunca se firma ni se envía |
| D3 | **Conciliación bancaria asistida** | `premium.conciliacion_bancaria_completada` (cron diario) | Descarga el extracto, lo cruza contra `Documentos_cabecera`, `Desembolsos` y `Transferencias`, y entrega solo las diferencias | **Cubre O-18**: hoy `lgeneradoarchivobanco` es solo un booleano |

### 5.5 Paquete E — Visibilidad, SLA y soporte (2 workflows)

| # | Workflow | Disparador | Lógica | Beneficio medible |
|---|---|---|---|---|
| E1 | **Vigilancia de SLA operativos** | `solicitud.aprobacion_solicitada` + cron | Mide tiempos de aprobación, desembolso y primer contacto de cobranza; escala al jefe si supera `nhorasrespuestamaxima` | **Cubre O-41**: el campo existe y hoy no se usa |
| E2 | **Reporte ejecutivo y salud del sistema** | cron semanal/mensual | Cartera, mora por tramos, producción, rentabilidad por cliente, comparativo contra el período anterior; más monitoreo de integraciones (SRI, OpenAI, Slack, WhatsApp) | **Cubre O-40 y O-45**: hoy no hay observabilidad ni reportes distribuidos |

### 5.6 Matriz de trazabilidad: workflow → omisión que resuelve

| Workflow | Omisiones cubiertas |
|---|---|
| A1, A2, A3, A7 | O-15 (notificaciones) |
| A4, A5 | O-15, O-16 (escalamiento) |
| A6 | **O-09 (cesión sin acuse)**, O-12 (expediente) |
| B1 | **O-16 (escalamiento automático)** |
| B2, B3 | **O-17 (promesas de pago)**, O-22 (trazabilidad de contacto) |
| B4 | O-05 (control de cupos), O-06 (concentración) |
| B5, E2 | O-45 (reportes automáticos) |
| C1 | **O-01 (KYC/AML)**, **O-02 (validación RUC)** |
| C2 | **O-08 (doble financiamiento)**, **O-25 (retenciones SRI)** |
| C3 | Fraude: duplicados, cambio de cuentas, reversas, excepciones de tasa |
| C4 | O-03 (scoring), O-06 (concentración) |
| C5 | O-03 (riesgo con IA — la integración ya existe) |
| D1 | **O-31 (cierre automático)**, ausencia de scheduler |
| D2 | **O-32 (cadena SRI completa)** |
| D3 | **O-18 (conciliación bancaria)** |
| E1 | O-41 (SLA medidos) |
| E2 | O-40 (observabilidad), O-44 (backup) |

**18 de las 46 omisiones quedan cubiertas por los workflows.** Las 28 restantes requieren desarrollo de núcleo (NIIF 9, multi-moneda, billing, API pública, multipago, factoring internacional, portal del deudor, firma electrónica de contratos) y se posicionan como **servicios profesionales**, no como parte de la suscripción.

---

## 6. Diseño del plan premium

### 6.1 Modelo de tres niveles

| | **Base** | **Premium** ⭐ | **Corporate** |
|---|---|---|---|
| **Precio mensual** | **USD 300** | **USD 690** | **USD 1.290** |
| Sistema completo de factoring (los 10 módulos) | ✅ | ✅ | ✅ |
| Usuarios incluidos | 5 | 15 | Ilimitados |
| Operaciones / mes | 150 | 1.000 | Ilimitadas |
| Reportes PDF y contabilidad completa | ✅ | ✅ | ✅ |
| Integración Slack / WhatsApp / Google | Manual | ✅ Automatizada | ✅ Automatizada |
| **Webhooks salientes** | ❌ | ✅ 135 eventos | ✅ 135 eventos + personalizados |
| **Workflows n8n incluidos** | ❌ | **22** | **22 + 10 a medida** |
| Notificaciones a cliente y deudor | ❌ | ✅ | ✅ |
| Escalamiento automático de cobranza | ❌ | ✅ | ✅ |
| KYC/AML + validación SRI + scoring | ❌ | ✅ | ✅ |
| Cadena SRI completa (firma + envío + autorización) | ❌ | ✅ | ✅ |
| Conciliación bancaria asistida | ❌ | ✅ | ✅ |
| Orquestación de procesos (cierre, asientos, cortes) | ❌ | ✅ | ✅ |
| Alertas antifraude | ❌ | ✅ | ✅ |
| Tablero de salud de integraciones | ❌ | ✅ | ✅ |
| SLA de soporte | 48 h hábiles | **8 h hábiles** | **4 h + canal directo** |
| SLA de disponibilidad | 99,0 % | 99,5 % | 99,9 % |
| Entornos (producción + staging) | Solo producción | ✅ Staging | ✅ Ambos + réplica |
| Onboarding | Autogestionado | **Acompañado** | **Acompañado + capacitación** |
| **Implementación (una vez)** | — | **USD 900** | **USD 2.500** |

### 6.2 Justificación del precio

**¿Por qué 2,3× y no 2×?** Porque el premium no es "el mismo sistema con más límites": es **una capacidad nueva** (automatización e integración) cuyo costo de reemplazo para el cliente es sustancialmente mayor que USD 390/mes.

| Componente del precio premium | Valor mensual justificado |
|---|---|
| Alojamiento, mantenimiento y monitoreo del n8n dedicado | USD 30 |
| Webhooks firmados con reintentos, outbox e idempotencia (infraestructura) | USD 60 |
| Biblioteca de 22 workflows mantenidos y actualizados | USD 520 |
| Reportería ejecutiva automática y tablero de integraciones | USD 80 |
| SLA 8 h + entorno de staging + onboarding acompañado | USD 120 |
| **Sustitución de trabajo manual** (ver 6.3) | **USD 2.280** |
| **Valor entregado total** | **≈ USD 3.090** |
| **Precio cobrado** | **USD 690** |
| **Valor entregado / precio** | **4,5×** |

**Costo de construir esto internamente.** Si una factoring quiere armar los 22 workflows con un integrador externo, la referencia de mercado ecuatoriana es de **USD 400-700 por workflow complejo**, más la infraestructura de webhooks (unos USD 2.500-4.000 de desarrollo Django). Total: entre **USD 11.300 y USD 19.400** de inversión inicial más **USD 600-1.200/mes** de mantenimiento. El premium se paga solo **desde el primer mes** frente a esa alternativa.

### 6.3 Cálculo de ROI para una factoring típica

**Supuestos** (factoring mediano ecuatoriano):

| Variable | Valor |
|---|---|
| Cartera promedio | USD 800.000 |
| Facturas gestionadas por mes | 220 |
| Deudores activos | 90 |
| Cobradores / analistas | 2 cobradores + 1 analista de riesgo |
| Costo cargado por hora | USD 12 |
| Horas de cobranza manual por factura | 0,75 h |
| Horas mensuales de reportería e integración manual | 24 h |

**Ahorro mensual**

| Concepto | Cálculo | Ahorro |
|---|---|---|
| Gestión de cobranza manual | 220 × 0,75 h × USD 12 | USD 1.980 |
| Recordatorios preventivos (los hace el sistema) | 220 × 0,25 h × USD 12 | USD 660 |
| Reportería ejecutiva y armado de tableros | 24 h × USD 12 | USD 288 |
| Conciliación bancaria manual | 16 h × USD 12 | USD 192 |
| Validación manual de facturas y listas de control | 20 h × USD 12 | USD 240 |
| **Subtotal trabajo manual** | | **USD 3.360** |
| Reducción de 3 días de mora promedio sobre USD 800.000 a 12 % anual | 800.000 × 12 % × 3/365 | USD 789 |
| **Ahorro total estimado** | | **USD 4.149 / mes** |

**Resultado**

| | |
|---|---|
| Costo adicional del premium | USD 390 / mes (690 − 300) |
| Implementación (una vez) | USD 900 |
| Ahorro mensual estimado | USD 4.149 |
| **ROI mensual** | **10,6×** |
| **Punto de equilibrio de la implementación** | **≈ 8 días** |

**Encuadre comercial recomendado para la conversación de venta:** *"El premium cuesta USD 390 más al mes. Si le evita que un solo cobrador dedique menos de 33 horas al mes a tareas que el sistema puede hacer solo, ya se pagó."* A USD 12/hora, ese umbral es de **33 horas mensuales** — un cobrador dedica más que eso solo a mandar recordatorios.

### 6.4 Add-ons y servicios profesionales

Más allá de la suscripción, hay ingreso por servicios que el premium habilita naturalmente:

| Servicio | Precio sugerido | Descripción |
|---|---|---|
| Workflow n8n a medida | USD 450 / workflow | Integración con un sistema específico del cliente (ERP, buró, banco) |
| Conector a sistema externo | USD 1.200 - 2.500 | SAP, Odoo, Siigo, sistema bancario local |
| Migración e importación de cartera | USD 800 | Carga histórica de cartera con validación |
| Capacitación presencial (2 días) | USD 900 | Equipo comercial, operativo y de cobranza |
| Soporte extendido 24/7 | USD 250 / mes | Fuera del horario hábil |
| Entorno dedicado (VPS propio) | USD 180 / mes | Aislamiento total de infraestructura |
| Reporte regulatorio NIIF 9 / ECL | USD 4.500 | Proyecto: desarrollo no incluido en el premium |
| Módulo de billing y suscripciones | USD 3.500 | Proyecto: alta de planes, control de límites y cobro automático |
| API pública con API keys y OAuth | USD 3.800 | Proyecto: hoy `/api/*` es anónimo |

### 6.5 Mecánica de conversión de Base a Premium

```
   Cliente en plan Base (USD 300/mes)
              │
              ├── Día 0: onboarding. Trial premium GRATIS 30 días
              │          (reutiliza DIAS_PRUEBA_SISTEMA = 30, que ya existe
              │           y hoy no hace nada — campo dfinpruebas)
              │
              ├── Día 1-7:   activar Paquete A (notificaciones).
              │              El cliente ve a sus clientes recibiendo acuses.
              │
              ├── Día 8-20:  activar Paquete B (cobranza) + C2 (validación SRI).
              │              Métrica de impacto: días de mora, contactos realizados.
              │
              ├── Día 21-29: mostrar el reporte E2 con el ahorro medido
              │              contra el mes anterior con datos reales del cliente.
              │
              └── Día 30:    conversión. Se cobra desde el mes 2.
                             Si no convierte → degrada a Base sin perder datos.
```

**Por qué este orden funciona:** el Paquete A es visible para los **clientes del cliente**, no solo para él. El acuse automático genera una percepción de mejora externa, lo que crea presión interna para no dar marcha atrás.

**Los tres números que hay que medir durante el trial** (y que hoy el sistema no puede dar, de ahí que la Fase 0 del roadmap sea la bitácora de eventos):

1. **Días promedio de mora** antes vs. después → el argumento financiero.
2. **Horas de cobranza por factura** → el argumento de eficiencia.
3. **Tiempo de aprobación de solicitudes** → el argumento de servicio al cliente.

---

## 7. Plan de implementación

### 7.1 Fases

| Fase | Duración | Alcance | Entregable verificable |
|---|---|---|---|
| **Fase 0 — Cimientos** | ~~3 semanas~~ **1,5 semanas** | ~~Resolver los 5 hallazgos críticos de seguridad~~ **(hecho, 26-jul-2026)**; crear las 3 tablas de webhooks y el despachador con HMAC; crear la bitácora de eventos; registrar los 12 eventos P0 de Fase 1; staging y monitoreo básico | Un evento de prueba firmado llega a n8n y se verifica la firma |
| **Fase 1 — MVP comercial** | 4 semanas | Paquete A completo (7), B1, B2, C2, C3, D1, E1. Alta de clientes premium en el sistema | Un cliente real recibe notificaciones automáticas y su cobranza escala sola por 2 semanas |
| **Fase 2 — Cobertura completa** | 4 semanas | Resto de dominios 2 y 5 (clientes/deudores y contabilidad/SRI); paquetes C1, C4, D2; catálogo completo de 135 eventos | 135 eventos emitidos y trazables; cadena SRI completa de punta a punta |
| **Fase 3 — Diferenciación** | 4 semanas | Paquetes B3, B4, B5, C5, D3, E2; workflows a medida por cliente; tablero de salud de integraciones | Reporte ejecutivo automático y conciliación bancaria entregando diferencias |
| **Fase 4 — Comercialización** | continuo | Onboarding autoservicio, trial de 30 días automatizado, materiales de venta, capacitación | Proceso de conversión Base→Premium operando sin intervención manual |

**Total: 13,5 semanas** (≈ 3 meses) hasta el final de la Fase 3. La Fase 0 se acortó a la mitad porque el endurecimiento de seguridad previo ya se ejecutó.

### 7.2 Recursos requeridos

| Rol | Dedicación Fase 0-1 | Dedicación Fase 2-3 |
|---|---|---|
| Desarrollador Django (backend, webhooks, seguridad) | 1,0 FTE | 0,5 FTE |
| Especialista n8n / integraciones | 0,5 FTE | 1,0 FTE |
| Analista funcional de factoring (validación de reglas) | 0,3 FTE | 0,3 FTE |
| QA (pruebas de contrato de webhooks y de workflows) | 0,2 FTE | 0,3 FTE |

### 7.3 Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Los hallazgos críticos de seguridad retrasan la Fase 0 | Alta | Alto | **No negociable.** Sin resolverlos, no se abren webhooks salientes. Se ejecuta en paralelo con el diseño de workflows |
| La lógica en SPs dificulta emitir eventos con contexto | Alta | Medio | Emitir desde la vista Django que invoca el SP (no desde el SP), usando `enviarPost()` como punto de retorno. El outbox se escribe antes de la llamada |
| Los SPs son PostgreSQL, pese a que el código tiene rastros de SQL Server | Media | Medio | Verificar el motor real en staging **antes** de escribir cualquier SQL nativo del outbox |
| n8n se cae y se pierden eventos | Media | Alto | Outbox + reintentos con backoff + dead letter. Un evento nunca se pierde por una caída del consumidor |
| El cliente no adopta los workflows | Media | Alto | Trial de 30 días con métricas reales. Sin conversión, degrada a Base sin perder datos |
| Dependencia de la API del SRI (bloqueo geográfico) | Media | Medio | Ya está resuelto: `SRI_PROXY_URL` y los endpoints de contribuyente están configurados en `settings.py:237-252` |
| Openness: el cliente quiere sus propios workflows | Baja | Bajo | n8n es estándar; se vende la infraestructura y el catálogo, no el lock-in |
| `DEBUG=True` en producción expone trazas en los errores de webhook | Alta | Alto | Parte de la Fase 0 |

### 7.4 KPIs del plan premium

| KPI | Línea base actual | Objetivo a 6 meses |
|---|---|---|
| Días promedio de mora | Medir en Fase 0 | −20 % |
| Tiempo de aprobación de solicitudes | Medir en Fase 0 (campo `nhorasrespuestamaxima` existe sin usar) | < 4 h en el 90 % de los casos |
| Contactos de cobranza ejecutados | Hoy solo lo que el cobrador alcanza a hacer | 100 % de facturas vencidas contactadas en 72 h |
| Facturas validadas en el SRI antes de liquidar | 0 % (chequeo comentado) | 100 % |
| Cesiones con acuse de recibo archivado | 0 % | 95 % |
| Conciliaciones bancarias del mes cerradas | Solo las manuales | 100 % automáticas con diferencias reportadas |
| Horas mensuales de trabajo manual evitado | 0 | > 250 h |
| Clientes Base convertidos a Premium | 0 % | 25 % |

---

## 8. Anexos

### 8.1 Convención de nombres

| Elemento | Convención | Ejemplo |
|---|---|---|
| Evento | `entidad.accion_en_pasado` en minúsculas, sin tildes | `operacion.liquidada` |
| Dominio (wildcard) | `entidad.*` | `cobranza.*` |
| Workflow n8n | `MGT-<paquete><n> · <descripción>` | `MGT-A4 · Recordatorio de vencimiento` |
| Credencial n8n | `margarita_<entorno>_<servicio>` | `margarita_prod_sri` |
| Fila en `webhook_event` | `event_id` UUID v4 | `0f9c2b74-5a31-4e88-b0d2-7c1f4a9e6b35` |

### 8.2 Anexo de seguridad: checklist antes de conectar n8n

> **Estado: los 5 hallazgos críticos fueron corregidos y verificados.** Ver el anexo 8.6 para el detalle de la corrección y las variables de entorno que hay que definir.

**Corregido y verificado**

- [x] `DEBUG = False` por defecto (variable de entorno), con `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` configurables
- [x] Llamada a `eval()` sobre `request.POST["Cheques"]` eliminada (`solicitudes/views.py`)
- [x] `REST_FRAMEWORK` con `IsAuthenticated` por defecto y `rest_framework` en `INSTALLED_APPS`
- [x] `permission_classes` activado en los 3 endpoints de `api/views.py`
- [x] Filtro de empresa agregado en `asiento_contable_api` (`contabilidad/views.py`)
- [x] Firma validada en el webhook de Twilio (`X-Twilio-Signature`)
- [x] Firma validada en el webhook de Meta WhatsApp (`X-Hub-Signature-256`)
- [x] Clave compartida exigida en el webhook de carga de solicitudes (`X-Margarita-Key`)

**Pendiente (segundo lote)**

- [ ] `SECRET_KEY` rotado y fuera del repositorio
- [ ] Secretos de Slack, Twilio y newsdata.io movidos a variables de entorno; rotados
- [ ] `LOGGING` configurado con rotación y alerta a n8n ante errores 5xx
- [ ] `CACHES` con backend compartido (Redis) para la caché de RUC del SRI
- [ ] Re-verificación de propiedad por empresa en las `UpdateView` que hoy no la hacen
- [ ] Aislamiento por empresa en `webhook_whatsapp_twilio` (hoy toma la primera configuración activa de cualquier empresa)
- [ ] Firma HMAC verificada en **todos** los webhooks salientes del premium
- [ ] Ventana de tolerancia de 5 minutos contra ataques de replay
- [ ] Lista blanca de IP de n8n si el cliente lo permite
- [ ] `webhook_event` con retención definida (recomendado: 24 meses) y respaldo
- [ ] Suite de tests corriendo en CI contra una base PostgreSQL de test (las migraciones no aplican en SQLite)

### 8.3 Anexo: errores técnicos detectados que conviene corregir

| # | Error | Archivo | Efecto |
|---|---|---|---|
| 1 | Comas finales convierten 4 campos en tuplas → no existen en la BD | `empresa/models.py:20-23` | La configuración SMTP es inutilizable |
| 2 | El comando IMAP no está en `management/commands/` | `administracion/comandos/procesar_correos.py` | `manage.py procesar_correos` no funciona |
| 3 | `api/noticias.py` llama a la API al importar el módulo | `api/noticias.py:68-82` | Latencia y fallo en el arranque; API key hardcodeada |
| 4 | `api/sri2.py` hace una llamada SOAP a nivel de import con clave hardcodeada | `api/sri2.py:163-187` | Código muerto peligroso |
| 5 | `Solicitud_aprobacion.asignacion` es `BigInteger`, no FK | `solicitudes/models.py:55` | Sin integridad referencial |
| 6 | `Pagares` sin FK a `Asignacion` | `operaciones/models.py:2051` | La reestructuración no queda trazada |
| 7 | `ESTADOS_DE_COMPRADORES` define A/X pero las vistas renderizan B/I/P/L | `clientes/models.py:11-14` vs `clientes/views.py:1446-1463` | Estados no seleccionables |
| 8 | `dvencimiento = hoy + 30` hardcodeado al cargar desde XML | `solicitudes/servicios.py:207` | Se pierde el plazo real de la factura y con él el cálculo de GAO y descuento |
| 9 | `UnboundLocalError` si el participante existe sin `Datos_generales` | `clientes/views.py:1387` | Error 500 latente |
| 10 | `nmaximooperaciones`, `lbloqueada` y `dfinpruebas` nunca se leen para bloquear | `bases/models.py:12-14` | No hay control comercial automatizado |
| 11 | `nporcentajeiva` default 12 en `operaciones.Asignacion` vs 15 en `bases.Empresas` | modelos respectivos | Inconsistencia de IVA según el camino de alta |
| 12 | `USE_L10N = True` en Django 5.1 | `settings.py:169` | Sin efecto; la localización cambió de mecanismo |

### 8.4 Anexo: primer workflow de referencia (Paquete A4)

Esbozo de importación directa en n8n, para validar la arquitectura de punta a punta:

```json
{
  "name": "MGT-A4 · Recordatorio de vencimiento escalonado",
  "nodes": [
    { "name": "Schedule 07:00", "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": { "rule": { "interval": [{ "field": "cronExpression",
        "expression": "0 7 * * 1-5" }] } } },
    { "name": "Margarita · facturas por vencer", "type": "n8n-nodes-base.httpRequest",
      "parameters": { "method": "POST",
        "url": "https://margarita.codigobambuecuador.com/cobranzas/webhook/facturas_por_vencer/",
        "sendHeaders": true,
        "headerParameters": { "parameters": [
          { "name": "X-Margarita-API-Key", "value": "={{ $env.MARGARITA_API_KEY }}" },
          { "name": "Content-Type", "value": "application/json" } ] },
        "sendBody": true, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ dias: 7, empresa_id: 1, usuario_id: 1 }) }}",
        "options": { "timeout": 30000 } } },
    { "name": "Separar por factura", "type": "n8n-nodes-base.splitOut",
      "parameters": { "fieldToSplitOut": "clientes" } },
    { "name": "Separar facturas", "type": "n8n-nodes-base.splitOut",
      "parameters": { "fieldToSplitOut": "facturas" } },
    { "name": "Calcular tono", "type": "n8n-nodes-base.code",
      "parameters": { "jsCode":
        "const f = $json; const hoy = new Date();\nconst v = new Date(f.fecha_vencimiento);\nconst dias = Math.ceil((v - hoy) / 86400000);\nreturn [{ json: { ...f, dias_restantes: dias, tono: dias <= 1 ? 'urgente' : dias <= 3 ? 'firme' : 'cortes' } }];" } },
    { "name": "Enviar WhatsApp", "type": "n8n-nodes-base.httpRequest",
      "parameters": { "method": "POST",
        "url": "https://graph.facebook.com/v22.0/={{ $env.PHONE_NUMBER_ID }}/messages",
        "sendHeaders": true,
        "headerParameters": { "parameters": [
          { "name": "Authorization", "value": "=Bearer {{ $env.WHATSAPP_TOKEN }}" } ] },
        "sendBody": true, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ messaging_product: 'whatsapp', to: $json.celular, type: 'text', text: { body: `Estimado cliente, le recordamos que la factura ${$json.numero} por USD ${$json.saldo} vence en ${$json.dias_restantes} día(s).` } }) }}" } },
    { "name": "Registrar envío", "type": "n8n-nodes-base.googleSheets",
      "parameters": { "operation": "append",
        "documentId": "={{ $env.SHEET_LOG_COBRANZA }}",
        "sheetName": "Recordatorios" } }
  ],
  "settings": { "executionOrder": "v1" }
}
```

Obsérvese que este workflow **solo usa endpoints que ya existen** (`cobranzas/webhook/facturas_por_vencer/`, que ya devuelve `celular`, `numero`, `fecha_vencimiento` y `saldo`) más la API de WhatsApp cuya configuración ya está en `settings.py`. **Es desplegable hoy mismo**, sin tocar el núcleo de Django. Ese es el argumento comercial más fuerte del plan premium: **hay valor facturable disponible antes de escribir la primera línea de código nuevo.**

> **Nota:** `cobranzas/webhook/facturas_por_vencer/` sigue **sin autenticación** (devuelve datos de cartera por cliente). Al desplegar este workflow, conviene protegerlo con el mismo esquema `INTERNAL_API_KEY` que se definió en `settings.py`, o restringirlo por IP de n8n. El webhook de carga de solicitudes **ya exige** `X-Margarita-Key`.

### 8.5 Glosario

| Término | Significado en Margarita |
|---|---|
| **Asignación** | La operación de factoring. En `solicitudes` es la negociación en curso; en `operaciones` es la ya liquidada |
| **GAO** | Gastos administrativos y operativos: la comisión del factor cobrada al cliente |
| **GAOA** | GAO adicional, aplicado sobre cartera vencida |
| **DC / DCV** | Descuento de cartera / descuento de cartera vencido |
| **Accesorio** | Cheque o letra que respalda la factura negociada |
| **Protesto** | Rechazo formal del cheque por falta de fondos |
| **Cesión** | Transferencia del crédito del cliente (cedente) al factor (cesionario). Requiere notificación al deudor |
| **Exceso temporal** | Autorización puntual para negociar por encima de la línea de factoring |
| **Corte histórico** | Snapshot mensual de cartera, protestos y pagarés |
| **Outbox** | Patrón de persistir el evento en la misma transacción de negocio y despacharlo después |
| **Dead letter** | Cola de eventos que agotaron los reintentos y requieren intervención manual |

### 8.6 Anexo: corrección de los 5 hallazgos críticos (ejecutada)

Los 5 hallazgos marcados como no negociables fueron corregidos el **26 de julio de 2026**. Verificación: `python manage.py check` sin incidencias, 31 comprobaciones funcionales y 7 comprobaciones HTTP, todas en verde.

| # | Hallazgo | Corrección aplicada | Archivos |
|---|---|---|---|
| **H1** | Ejecución de código arbitrario desde el formulario de accesorios | La llamada a `eval()` sobre `request.POST["Cheques"]` se reemplazó por `json.loads()` con respaldo en `ast.literal_eval()`, y se descarta todo elemento que no sea diccionario. Un test verifica por AST que no quede ninguna llamada a `eval()`/`exec()` en el módulo | `solicitudes/views.py` |
| **H2** | Endpoints `/api/*` accesibles sin autenticación | `@permission_classes([IsAuthenticated])` en los 3 endpoints; `permission_classes = [IsAuthenticated]` en `InvoiceAIAnalysisView`; `REST_FRAMEWORK` con `IsAuthenticated` por defecto y `rest_framework` registrado en `INSTALLED_APPS` (no estaba). Además, cada endpoint acota por empresa: `Datos_generales`, `Documentos` y `InvoiceAIAnalysis` | `api/views.py`, `factorweb25/settings.py` |
| **H3** | Fuga multi-tenant de asientos contables | `IsAuthenticated` + filtro `empresa=id_empresa.empresa` sobre `Diario_cabecera`; devuelve 403 si el usuario no tiene empresa asignada | `contabilidad/views.py` |
| **H4** | `DEBUG = True` en producción | `DEBUG = os.getenv("DEBUG", "False")` → seguro por defecto. `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` pasan a variables de entorno con los valores de producción como respaldo. En local, `DEBUG=True` vive en `.env`, que está en `.gitignore` | `factorweb25/settings.py`, `.env` |
| **H5** | Webhooks entrantes sin verificación de firma | Twilio: `RequestValidator.validate()` sobre `X-Twilio-Signature`. Meta: HMAC-SHA256 sobre el cuerpo crudo con `X-Hub-Signature-256`. Carga de solicitudes: clave compartida `X-Margarita-Key` con comparación en tiempo constante. Todos registran el rechazo en el logger | `api/twilio_service.py`, `api/whatsapp.py`, `solicitudes/webhooks.py` |

**Variables de entorno nuevas (obligatorias en producción)**

| Variable | Obligatoria | Efecto si falta |
|---|---|---|
| `MARGARITA_API_KEY` | **Sí** | El webhook de carga de solicitudes responde 403 a todo (fail-closed) |
| `WHATSAPP_APP_SECRET` | **Sí** | El webhook de Meta rechaza todo (fail-closed). Si ya existe `CLAVE_SECRETA_WHATSAPP_META`, se reutiliza automáticamente |
| `WHATSAPP_VERIFY_TOKEN` | Recomendada | Cae en `WHATSAPP_TOKEN` (comportamiento anterior) |
| `DEBUG` | Sí en local | `False` por defecto; en local debe estar en `True` |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | No | Usan los hosts de producción actuales |
| `TWILIO_VALIDATE_SIGNATURE` | No | `True`. Ponerlo en `False` solo para depuración local |

**Cambio operativo requerido en n8n.** El workflow que hoy llama al webhook de carga de solicitudes **debe** empezar a enviar la cabecera `X-Margarita-Key`. Sin ella el endpoint responde 403. En el nodo HTTP Request de n8n:

```
Header:  X-Margarita-Key
Value:   ={{ $env.MARGARITA_API_KEY }}
```

El resto del contrato del payload (`correo`, `empresa_id`, `user_id`) no cambió.

**Pruebas permanentes agregadas**

| Archivo | Casos | Cubre |
|---|---|---|
| `api/tests_seguridad.py` | 11 | Permisos de los 3 endpoints, default de DRF, firma de Twilio (válida, ausente, manipulada), firma de Meta (válida, ausente, manipulada), 403 anónimo |
| `solicitudes/tests_seguridad.py` | 12 | Ausencia de `eval()` por AST, parseo seguro del payload de cheques (JSON, literales, código malicioso, `None`, escalares), clave del webhook |
| `contabilidad/tests_seguridad.py` | 4 | Permiso, 403 anónimo y filtro por empresa del asiento contable |

**Limitación conocida de la suite.** Las migraciones del proyecto no aplican sobre SQLite (falla un `alter_field` en `contabilidad.0019` al resolver una referencia a modelo declarada como string). Por eso las pruebas se ejecutan con `factorweb25.test_settings`, que apunta a SQLite en memoria para **no crear ni destruir bases en el servidor de producción**. Para correrlas hace falta una base PostgreSQL de test aparte:

```bash
python manage.py test api.tests_seguridad solicitudes.tests_seguridad \
    contabilidad.tests_seguridad --settings=factorweb25.test_settings
```

La corrección se validó además con comprobaciones funcionales directas sobre los helpers (31 casos) y con peticiones HTTP reales anónimas a los 7 endpoints (7 casos, todos 403), sin tocar la base de datos.


---

## 9. Recomendación final

**Vender el premium a USD 690/mes y ejecutarlo en el orden propuesto.**

Tres razones para actuar ahora:

1. **El valor es inmediato y no depende del desarrollo de núcleo.** El workflow A4 (recordatorios de vencimiento) y el A6 (cesión con acuse) se pueden entregar usando **únicamente endpoints que ya existen en producción**. El equipo incluso ya tiene un nodo Code de n8n probado para decodificar los adjuntos del SRI. La Fase 0 es de 3 semanas y produce valor desde la primera semana.

2. **El precio está anclado en un ahorro verificable, no en una percepción.** A USD 12/hora, el premium se paga con **33 horas mensuales** de trabajo manual evitado. Una sola cobranza automatizada por día ya cubre eso.

3. **El activo estratégico es el catálogo, no el software.** Los 135 eventos y 22 workflows son propiedad intelectual reutilizable: cada cliente nuevo se activa sin reescribir nada. El costo marginal de un cliente premium adicional es de aproximadamente **USD 30-45/mes** en infraestructura (n8n + monitoreo) contra **USD 690 de ingreso**. Ese es el negocio.

**La condición no negociable ya está cumplida.** Los 5 hallazgos críticos de seguridad fueron corregidos y verificados el 26-jul-2026 (anexo 8.6): la ejecución de código arbitrario desde el formulario de accesorios, los tres endpoints `/api/*` anónimos, la fuga multi-tenant de asientos contables, el `DEBUG=True` en producción y la ausencia de verificación de firma en los webhooks entrantes. El sistema **ya puede** conectarse a un bus de eventos sin exponer al cliente ni al negocio.

Queda un segundo lote de endurecimiento que **no bloquea** el arranque del premium, pero que conviene cerrar antes de escalar a muchos clientes: configuración de correo (el bug de las comas finales en `Configuracion_correos` impide enviar emails), gestión de secretos fuera de la base de datos, `LOGGING` con alertas, aislamiento por empresa en `webhook_whatsapp_twilio` y una base PostgreSQL de test en CI para que la suite de 27 pruebas corra de forma continua. La Fase 0 del roadmap se reduce así a construir la capa de webhooks salientes; el endurecimiento previo ya está hecho.
