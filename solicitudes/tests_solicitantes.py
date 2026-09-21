"""Pruebas del mantenimiento (CRUD) de solicitantes de factoring.

Cubren el renombrado solicitudes.Clientes -> solicitudes.Solicitantes, los
permisos del modelo renombrado y las vistas de lista, alta, edicion y
eliminacion logica que se agregaron al menu Operaciones / Negociacion.

Ejecutar con:
    python manage.py test solicitudes.tests_solicitantes \
        --settings=factorweb25.test_settings_operaciones
"""
from django.contrib.auth.models import Permission, User
from django.test import TestCase, override_settings
from django.urls import reverse

from bases.models import Empresas, Usuario_empresa
from empresa.models import Tipos_factoring
from solicitudes.models import Asignacion, Solicitantes

PERMISOS = [
    'view_solicitantes',
    'add_solicitantes',
    'change_solicitantes',
    'delete_solicitantes',
]


@override_settings(ROOT_URLCONF='factorweb25.urls')
class BaseSolicitantesTests(TestCase):
    """Empresa, usuario con permisos y un solicitante de partida."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='solicitantes', password='x')
        self.empresa = Empresas.objects.create(
            ctnombre='FACTOR A', ctruccompania='0993220167001')
        self.otra_empresa = Empresas.objects.create(
            ctnombre='FACTOR B', ctruccompania='0993230707001')
        Usuario_empresa.objects.create(user=self.user, empresa=self.empresa)

        self.user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='solicitudes', codename__in=PERMISOS))

        self.client.force_login(self.user)

        # Tipos_factoring sobreescribe save() y exige las iniciales de
        # liquidacion de cobranza.
        self.tipo = Tipos_factoring(
            cttipofactoring='factoring', ctabreviacion='FAC', cxmoneda='USD',
            ctinicialesliquidacioncobranza='LC',
            cxusuariocrea=self.user, empresa=self.empresa)
        self.tipo.save()

        self.solicitante = Solicitantes.objects.create(
            cxcliente='1790012345001', ctnombre='SOLICITANTE UNO',
            ctemail='uno@example.com',
            cxusuariocrea=self.user, empresa=self.empresa)

    def datos_formulario(self, **cambios):
        datos = {
            'cxcliente': '1790012345555',
            'ctnombre': 'SOLICITANTE NUEVO',
            'ctdireccion': 'Av. Siempre Viva 123',
            'cttelefono1': '022345678',
            'cttelefono2': '',
            'ctemail': 'nuevo@example.com',
            'ctemail2': '',
            'ctcelular': '+593999999999',
            'ctgirocomercial': 'Comercio al por mayor',
            'dinicioactividades': '2020-01-15',
            'empresa': self.empresa.id,
        }
        datos.update(cambios)
        return datos


class PermisosSolicitantesTests(BaseSolicitantesTests):
    def test_permisos_del_modelo_renombrado(self):
        codenames = set(Permission.objects.filter(
            content_type__app_label='solicitudes'
        ).values_list('codename', flat=True))

        for codename in PERMISOS:
            self.assertIn(codename, codenames)
        for codename in ('view_clientes', 'add_clientes',
                         'change_clientes', 'delete_clientes'):
            self.assertNotIn(codename, codenames)


class ListaSolicitantesTests(BaseSolicitantesTests):
    def test_lista_muestra_solo_los_activos_de_la_empresa(self):
        Solicitantes.objects.create(
            cxcliente='1790012345002', ctnombre='SOLICITANTE DOS',
            cxusuariocrea=self.user, empresa=self.empresa)
        Solicitantes.objects.create(
            cxcliente='1790012345003', ctnombre='SOLICITANTE ELIMINADO',
            leliminado=True, cxusuariocrea=self.user, empresa=self.empresa)
        Solicitantes.objects.create(
            cxcliente='1790099999001', ctnombre='OTRA EMPRESA',
            cxusuariocrea=self.user, empresa=self.otra_empresa)

        respuesta = self.client.get(reverse('solicitudes:listasolicitantes'))

        self.assertEqual(respuesta.status_code, 200)
        nombres = [s.ctnombre for s in respuesta.context['consulta']]
        self.assertIn('SOLICITANTE UNO', nombres)
        self.assertIn('SOLICITANTE DOS', nombres)
        self.assertNotIn('SOLICITANTE ELIMINADO', nombres)
        self.assertNotIn('OTRA EMPRESA', nombres)

    def test_lista_requiere_permiso(self):
        sin_permisos = User.objects.create_user(
            username='sinpermisos', password='x')
        Usuario_empresa.objects.create(user=sin_permisos, empresa=self.empresa)
        self.client.force_login(sin_permisos)

        respuesta = self.client.get(reverse('solicitudes:listasolicitantes'))

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('bases:sin_permisos'), respuesta['Location'])


class CrearSolicitanteTests(BaseSolicitantesTests):
    def test_formulario_de_alta(self):
        respuesta = self.client.get(reverse('solicitudes:solicitante_nuevo'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Nuevo solicitante')

    def test_crear_asigna_empresa_y_usuario(self):
        respuesta = self.client.post(
            reverse('solicitudes:solicitante_nuevo'),
            self.datos_formulario())

        self.assertRedirects(
            respuesta, reverse('solicitudes:listasolicitantes'))
        nuevo = Solicitantes.objects.get(cxcliente='1790012345555')
        self.assertEqual(nuevo.ctnombre, 'SOLICITANTE NUEVO')
        self.assertEqual(nuevo.empresa, self.empresa)
        self.assertEqual(nuevo.cxusuariocrea, self.user)

    def test_no_admite_identificacion_duplicada(self):
        respuesta = self.client.post(
            reverse('solicitudes:solicitante_nuevo'),
            self.datos_formulario(cxcliente=self.solicitante.cxcliente))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            Solicitantes.objects.filter(
                cxcliente=self.solicitante.cxcliente).count(), 1)


class EditarSolicitanteTests(BaseSolicitantesTests):
    def test_formulario_de_edicion(self):
        respuesta = self.client.get(reverse(
            'solicitudes:solicitante_editar', args=[self.solicitante.id]))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'SOLICITANTE UNO')

    def test_editar_guarda_usuario_que_modifica(self):
        respuesta = self.client.post(
            reverse('solicitudes:solicitante_editar',
                    args=[self.solicitante.id]),
            self.datos_formulario(
                cxcliente=self.solicitante.cxcliente,
                ctnombre='SOLICITANTE UNO EDITADO'))

        self.assertRedirects(
            respuesta, reverse('solicitudes:listasolicitantes'))
        self.solicitante.refresh_from_db()
        self.assertEqual(self.solicitante.ctnombre, 'SOLICITANTE UNO EDITADO')
        self.assertEqual(self.solicitante.cxusuariomodifica, self.user.id)

    def test_no_edita_solicitante_de_otra_empresa(self):
        ajeno = Solicitantes.objects.create(
            cxcliente='1790099999002', ctnombre='AJENO',
            cxusuariocrea=self.user, empresa=self.otra_empresa)

        respuesta = self.client.get(
            reverse('solicitudes:solicitante_editar', args=[ajeno.id]))

        self.assertEqual(respuesta.status_code, 404)


class EliminarSolicitanteTests(BaseSolicitantesTests):
    def test_eliminacion_es_logica(self):
        respuesta = self.client.get(reverse(
            'solicitudes:eliminar_solicitante', args=[self.solicitante.id]))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.content.startswith(b'OK'))
        self.solicitante.refresh_from_db()
        self.assertTrue(self.solicitante.leliminado)
        self.assertEqual(self.solicitante.cxusuarioelimina, self.user.id)

    def test_no_elimina_con_solicitud_vigente(self):
        Asignacion.objects.create(
            cxcliente=self.solicitante, cxtipofactoring=self.tipo,
            cxtipo='F', cxasignacion='sol00001', nvalor=1000,
            cxusuariocrea=self.user, empresa=self.empresa)

        respuesta = self.client.get(reverse(
            'solicitudes:eliminar_solicitante', args=[self.solicitante.id]))

        self.assertTrue(respuesta.content.startswith(b'ERROR'))
        self.solicitante.refresh_from_db()
        self.assertFalse(self.solicitante.leliminado)

    def test_no_elimina_solicitante_de_otra_empresa(self):
        ajeno = Solicitantes.objects.create(
            cxcliente='1790099999003', ctnombre='AJENO',
            cxusuariocrea=self.user, empresa=self.otra_empresa)

        respuesta = self.client.get(reverse(
            'solicitudes:eliminar_solicitante', args=[ajeno.id]))

        self.assertTrue(respuesta.content.startswith(b'ERROR'))
        ajeno.refresh_from_db()
        self.assertFalse(ajeno.leliminado)
