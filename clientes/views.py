from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.db import transaction

from .models import Cuenta_transferencia, Datos_generales, Personas_juridicas, Personas_naturales, Linea_Factoring \
    , Datos_compradores, Cupos_compradores, Cuentas_bancarias

from empresa.models import Datos_participantes
from empresa.forms import ParticipanteForm

from .forms import  ClienteForm, PersonaNaturalForm, PersonaJuridicaForm\
    ,LineaFactoringForm, CuposCompradoresForm, CuentasBancariasForm\
    , CompradorForm

from datetime import date

class ClientesView(LoginRequiredMixin, generic.ListView):
    model = Datos_generales
    template_name = "clientes/listaclientes.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    
class LineasView(LoginRequiredMixin, generic.ListView):
    model = Datos_generales
    template_name = "clientes/listalineasfactoring.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class CuentasBancariasView(LoginRequiredMixin, generic.ListView):
    model = Datos_generales
    template_name = "clientes/listacuentasbancarias.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    
class CuentasBancariasNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_bancarias
    template_name = "clientes/datoscuentabancaria_modal.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    form_class=CuentasBancariasForm
    # success_url=reverse_lazy("clientes:listacuentasbancariascliente")
    success_message="Línea creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        cliente_ruc = self.kwargs.get('cliente_ruc')
        # Call the base implementation first to get a context
        context = super(CuentasBancariasNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["cliente_id"] = cliente_ruc
        return context

    def get_success_url(self):
        cliente_ruc = self.kwargs.get('cliente_ruc')
        return reverse_lazy("clientes:listacuentasbancariascliente"
            , kwargs={'cliente_ruc': cliente_ruc})

class CuentasBancariasDeudoresView(LoginRequiredMixin, generic.ListView):
    model = Cuentas_bancarias
    template_name = "clientes/listacuentasbancariasdeudores.html"
    context_object_name='consulta'
    login_url = 'bases:login'

    # solo cuentas de deudores
    def get_queryset(self):
        participantes = Datos_participantes.objects.values_list('cxparticipante')
        dedudores = Datos_compradores.objects.values_list('cxcomprador')

        return Cuentas_bancarias.objects\
            .filter(cxparticipante__in = participantes.intersection(dedudores))

class CuentasBancariasDeudorNew(LoginRequiredMixin, generic.CreateView):
    model = Cuentas_bancarias
    template_name = "clientes/datoscuentabancariadeudor.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    form_class=CuentasBancariasForm
    success_url=reverse_lazy("clientes:listacuentasbancarias_deudores")
    success_message="Línea creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class CuentasBancariasDeudorEdit(LoginRequiredMixin, generic.UpdateView):
    model = Cuentas_bancarias
    template_name = "clientes/datoscuentabancariadeudor.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    form_class=CuentasBancariasForm
    # success_url=reverse_lazy("clientes:listacuentasbancariascliente")
    success_message="Línea creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class LineaNew(LoginRequiredMixin, generic.CreateView):
    model=Linea_Factoring
    template_name="clientes/datoslinea_modal.html"
    context_object_name = "consulta"
    form_class=LineaFactoringForm
    success_url=reverse_lazy("clientes:listalineas")
    success_message="Línea creada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        cliente_ruc = self.kwargs.get('cliente_ruc')
        nombre_cliente = self.kwargs.get('cliente')

        # Call the base implementation first to get a context
        context = super(LineaNew, self).get_context_data(**kwargs)
        context["nueva"]=True
        context["nombre_cliente"] = nombre_cliente
        context["cliente_id"] = cliente_ruc
        return context

class LineaEdit(LoginRequiredMixin, generic.UpdateView):
    model=Linea_Factoring
    template_name="clientes/datoslinea_modal.html"
    context_object_name = "consulta"
    form_class=LineaFactoringForm
    success_url=reverse_lazy("clientes:listalineas")
    success_message="Línea actualizada satisfactoriamente"

    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        nombre_cliente = self.kwargs.get('cliente')
        cliente_ruc = self.kwargs.get('cliente_ruc')

        context = super(LineaEdit, self).get_context_data(**kwargs)
        context["consulta"] = Linea_Factoring.objects.filter(pk=id).first()
        context["nueva"]=False
        context["nombre_cliente"] = nombre_cliente
        context["cliente_id"] = cliente_ruc
        context["pk"] = id
        return context

class CompradoresView(LoginRequiredMixin, generic.ListView):
    model = Datos_compradores
    template_name = "clientes/listacompradores.html"
    context_object_name='consulta'
    login_url = 'bases:login'
    
class CuposCompradoresView(LoginRequiredMixin, generic.ListView):
    model = Cupos_compradores
    template_name = "clientes/listacuposcompradores.html"
    context_object_name='consulta'
    login_url = 'bases:login'

class CuposCompradoresNew(LoginRequiredMixin, generic.CreateView):
    model=Cupos_compradores
    template_name="clientes/datoscupo_modal.html"
    context_object_name = "consulta"
    form_class=CuposCompradoresForm
    success_url=reverse_lazy("clientes:listacupos")
    success_message="Cupo actualizado satisfactoriamente"
    
    def form_valid(self, form):
        form.instance.cxusuariocrea = self.request.user
        return super().form_valid(form)

class CuposCompradoresEdit(LoginRequiredMixin, generic.UpdateView):
    model=Cupos_compradores
    template_name="clientes/datoscupo_modal.html"
    context_object_name = "consulta"
    form_class=CuposCompradoresForm
    success_url=reverse_lazy("clientes:listacupos")
    success_message="Cupo actualizado satisfactoriamente"
    def form_valid(self, form):
        form.instance.cxusuariomodifica = self.request.user.id
        return super().form_valid(form)


@login_required(login_url='/login/')
@permission_required('clientes.view_datos_generales', login_url='bases:sin_permisos')
def DatosClientes(request, cliente_id=None):
    template_name="clientes/datoscliente_form.html"
    contexto={}
    idcliente={}
    datosparticipante={}
    formulario={}
    form_cliente={}
    datoscliente={}
    
    if request.method=='GET':
        datosparticipante = Datos_participantes.objects\
            .filter(cxparticipante=cliente_id).first()
            
        if datosparticipante:
            e={ 
                'cxtipoid':datosparticipante.cxtipoid,
                'cxparticipante':datosparticipante.cxparticipante,
                'ctnombre':datosparticipante.ctnombre,
                # 'cxzona': datosparticipante.cxzona,
                'cxlocalidad':datosparticipante.cxlocalidad,
                # 'cxestado':datosparticipante.cxestado,
                'ctdireccion':datosparticipante.ctdireccion,
                'ctemail':datosparticipante.ctemail,
                'ctemail2':datosparticipante.ctemail2,
                'cttelefono1':datosparticipante.cttelefono1,
                'cttelefono2':datosparticipante.cttelefono2,
                'ctcelular':datosparticipante.ctcelular,
                'ctgirocomercial':datosparticipante.ctgirocomercial,
            }
            idcliente=datosparticipante.cxparticipante
            formulario=ParticipanteForm(e)
            # si encuentra registro de datos participantes buscar en datos de cliente

            datoscliente = Datos_generales.objects\
                .filter(cxcliente=idcliente).first()
            
            if datoscliente:
                e={
                    'cxtipocliente':datoscliente.cxtipocliente,
                    'cxactividad':datoscliente.cxactividad,
                    'dinicioactividades':date.isoformat(datoscliente.dinicioactividades),
                    'cxcliente':datosparticipante.cxparticipante
                }
                form_cliente=ClienteForm(e)
        else:
            formulario=ParticipanteForm()
            form_cliente=ClienteForm()

            datoscliente=Datos_generales.objects.filter(pk=0)
            
    contexto={'datosparticipante':datosparticipante
            , 'form_participante':formulario
            , 'form_cliente':form_cliente
            }

    if request.method=='POST':
        # cxtipoid=request.POST.get("cxtipoid")
        cxtipoid="R"
        idcliente=request.POST.get("cxparticipante")
        ctnombre=request.POST.get("ctnombre")
        # cxzona=request.POST.get("cxzona")
        cxlocalidad=request.POST.get("cxlocalidad")
        # cxestado=request.POST.get("cxestado")
        ctdireccion=request.POST.get("ctdireccion")
        cttelefono1=request.POST.get("cttelefono1")
        cttelefono2=request.POST.get("cttelefono2")
        ctcelular=request.POST.get("ctcelular")
        ctemail=request.POST.get("ctemail")
        ctemail2=request.POST.get("ctemail2")
        ctgirocomercial=request.POST.get("ctgirocomercial")

        if not cliente_id:
            datosparticipante = Datos_participantes(
                cxtipoid=cxtipoid,
                cxparticipante=idcliente,
                ctnombre=ctnombre,
                # 'cxzona': datosparticipante.cxzona,
                cxlocalidad=cxlocalidad,
                # 'cxestado':datosparticipante.cxestado,
                ctdireccion=ctdireccion,
                ctemail=ctemail,
                ctemail2=ctemail2,
                cttelefono1=cttelefono1,
                cttelefono2=cttelefono2,
                ctcelular=ctcelular,
                ctgirocomercial=ctgirocomercial,
                cxusuariocrea= request.user
            )
            if datosparticipante:
                datosparticipante.save()
        else:
            datosparticipante = Datos_participantes.objects\
                .filter(cxparticipante=cliente_id).first()

            if datosparticipante:
                datosparticipante.cxtipoid = cxtipoid
                datosparticipante.cxparticipante=idcliente
                datosparticipante.ctnombre=ctnombre
                # datosparticipante.cxzona=cxzona
                datosparticipante.cxlocalidad=cxlocalidad
                # datosparticipante.cxestado=cxestado
                datosparticipante.ctdireccion=ctdireccion
                datosparticipante.ctemail=ctemail
                datosparticipante.ctemail2=ctemail2
                datosparticipante.cttelefono1=cttelefono1
                datosparticipante.cttelefono2=cttelefono2
                datosparticipante.ctcelular=ctcelular
                datosparticipante.ctgirocomercial=ctgirocomercial
                datosparticipante.cxusuariomodifica = request.user.id

                datosparticipante.save()
            
        # datos en tabla clientes

        datoscliente = Datos_generales.objects.filter(cxcliente=idcliente).first()

        cxtipocliente = request.POST.get("cxtipocliente")
        cxactividad = request.POST.get("cxactividad")
        dinicioactividades = request.POST.get("dinicioactividades")

        if not datoscliente:
            datoscliente= Datos_generales(
                cxcliente = datosparticipante,
                cxactividad = cxactividad,
                dinicioactividades=dinicioactividades,
                cxtipocliente=cxtipocliente,
                cxusuariocrea = request.user
            )
            if datoscliente:
                datoscliente.save()
        else:
            datoscliente.cxactividad=cxactividad
            datoscliente.dinicioactividades = dinicioactividades
            datoscliente.cxtipocliente=cxtipocliente
            datoscliente.cxusuariomodifica = request.user.id

            datoscliente.save()

        # bifurcar dependiendo del tipo de cliente: natural o juridico
        if cxtipocliente=="N":
            return redirect("clientes:clientenatural_editar",cliente_ruc=idcliente)
        else:
            return redirect("clientes:clientejuridico_editar",cliente_ruc=idcliente)

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('clientes.update_datos_generales', login_url='bases:sin_permisos')
def DatosClienteNatural(request, cliente_ruc=None):
    template_name="clientes/datosclientenatural_form.html"
    contexto={}
    formulario={}
    datoscliente={}
    
    cliente = Datos_generales.objects\
        .filter(cxcliente=cliente_ruc).first()

    if request.method=='GET':
        datoscliente = Personas_naturales.objects\
            .filter(cxcliente=cliente_ruc).first()

        if datoscliente:
            nacimiento= date.isoformat(datoscliente.dnacimiento)
            e={ 
                'cxcliente':datoscliente.cxcliente,
                'dnacimiento':nacimiento,
                'cxsexo':datoscliente.cxsexo,
                'cxestadocivil':datoscliente.cxestadocivil,
                'cxconyuge':datoscliente.cxconyuge,
                'ctnombrenegocio':datoscliente.ctnombrenegocio,
                'ctnombreconyuge':datoscliente.ctnombreconyuge,
                'ctprofesion':datoscliente.ctprofesion,
            }
            formulario=PersonaNaturalForm(e)
        else:
            formulario=PersonaNaturalForm()

    contexto={'nombrecliente':cliente
            , 'form_cliente':formulario
            }

    if request.method=='POST':

        dnacimiento = request.POST.get("dnacimiento")
        cxsexo = request.POST.get("cxsexo")
        cxestadocivil = request.POST.get("cxestadocivil")
        cxconyuge = request.POST.get("cxconyuge")
        ctnombrenegocio = request.POST.get("ctnombrenegocio")
        ctnombreconyuge = request.POST.get("ctnombreconyuge")
        ctprofesion = request.POST.get("ctprofesion")

        datoscliente = Personas_naturales.objects.filter(cxcliente=cliente.cxcliente).first()

        if not datoscliente:
            datoscliente= Personas_naturales(
                dnacimiento = dnacimiento,
                cxsexo=cxsexo,
                cxestadocivil=cxestadocivil,
                cxcliente = cliente.cxcliente,
                cxconyuge = cxconyuge,
                ctnombrenegocio = ctnombrenegocio,
                ctprofesion = ctprofesion,
                ctnombreconyuge=ctnombreconyuge,
                cxusuariocrea = request.user
            )
            if datoscliente:
                datoscliente.save()
        else:
            datoscliente.dnacimiento=dnacimiento
            datoscliente.cxsexo = cxsexo
            datoscliente.cxestadocivil=cxestadocivil
            datoscliente.cxconyuge=cxconyuge
            datoscliente.ctnombreconyuge=ctnombreconyuge
            datoscliente.ctnombrenegocio=ctnombrenegocio
            datoscliente.ctprofesion=ctprofesion

            datoscliente.cxusuariomodifica = request.user.id

            datoscliente.save()

            return redirect("clientes:listaclientes")

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('clientes.update_datos_generales', login_url='bases:sin_permisos')
def DatosClienteJuridico(request, cliente_ruc=None):
    template_name="clientes/datosclientejuridico_form.html"
    contexto={}
    formulario={}
    datoscliente={}
    
    cliente = Datos_generales.objects\
        .filter(cxcliente=cliente_ruc).first()

    if request.method=='GET':
        datoscliente = Personas_juridicas.objects\
            .filter(cxcliente=cliente_ruc).first()
        if datoscliente:
            e={ 
                'cxcliente':datoscliente.cxcliente,
                'ctnombrecorto':datoscliente.ctnombrecorto,
                'cxtipoempresa':datoscliente.cxtipoempresa,
                'ctcontacto':datoscliente.ctcontacto,
                'ladministrasocios':datoscliente.ladministrasocios,
                'ladministraindividual':datoscliente.ladministraindividual,
                'ctobjetosocial':datoscliente.ctobjetosocial,
                'cxrepresentante1':datoscliente.cxrepresentante1,
                'ctrepresentante1':datoscliente.ctrepresentante1,
                'dvencimientocargorepresentante1':date.isoformat(datoscliente.dvencimientocargorepresentante1),
                'ctcargorepresentante1':datoscliente.ctcargorepresentante1,
                'cxestadocivilrepresentante1':datoscliente.cxestadocivilrepresentante1,
                'cttelefonorepresentante1':datoscliente.cttelefonorepresentante1,
                'cxrepresentante2':datoscliente.cxrepresentante2,
                'ctrepresentante2':datoscliente.ctrepresentante2,
                'dvencimientocargorepresentante2':date.isoformat(datoscliente.dvencimientocargorepresentante2),
                'ctcargorepresentante2':datoscliente.ctcargorepresentante2,
                'cxestadocivilrepresentante2':datoscliente.cxestadocivilrepresentante2,
                'cttelefonorepresentante2':datoscliente.cttelefonorepresentante2,
                'cxrepresentante3':datoscliente.cxrepresentante3,
                'ctrepresentante3':datoscliente.ctrepresentante3,
                'dvencimientocargorepresentante3':date.isoformat(datoscliente.dvencimientocargorepresentante3),
                'ctcargorepresentante3':datoscliente.ctcargorepresentante3,
                'cxestadocivilrepresentante3':datoscliente.cxestadocivilrepresentante3,
                'cttelefonorepresentante3':datoscliente.cttelefonorepresentante3,
            }
            formulario=PersonaJuridicaForm(e)
        else:
            formulario=PersonaJuridicaForm()

    contexto={'nombrecliente':cliente
            , 'form':formulario
            }

    if request.method=='POST':

        ctnombrecorto = request.POST.get("ctnombrecorto")
        cxtipoempresa = request.POST.get("cxtipoempresa")
        ctcontacto = request.POST.get("ctcontacto")
        ladministrasocios = request.POST.get("ladministrasocios")
        ladministraindividual = request.POST.get("ladministraindividual")
        ctobjetosocial = request.POST.get("ctobjetosocial")
        cxrepresentante1 = request.POST.get("cxrepresentante1")
        ctrepresentante1 = request.POST.get("ctrepresentante1")
        dvencimientocargorepresentante1 = request.POST.get("dvencimientocargorepresentante1")
        ctcargorepresentante1 = request.POST.get("ctcargorepresentante1")
        cxestadocivilrepresentante1 = request.POST.get("cxestadocivilrepresentante1")
        cttelefonorepresentante1 = request.POST.get("cttelefonorepresentante1")
        cxrepresentante2 = request.POST.get("cxrepresentante2")
        ctrepresentante2 = request.POST.get("ctrepresentante2")
        dvencimientocargorepresentante2 = request.POST.get("dvencimientocargorepresentante2")
        ctcargorepresentante2 = request.POST.get("ctcargorepresentante2")
        cxestadocivilrepresentante2 = request.POST.get("cxestadocivilrepresentante2")
        cttelefonorepresentante2 = request.POST.get("cttelefonorepresentante2")
        cxrepresentante3 = request.POST.get("cxrepresentante3")
        ctrepresentante3 = request.POST.get("ctrepresentante3")
        dvencimientocargorepresentante3 = request.POST.get("dvencimientocargorepresentante3")
        ctcargorepresentante3 = request.POST.get("ctcargorepresentante3")
        cxestadocivilrepresentante3 = request.POST.get("cxestadocivilrepresentante3")
        cttelefonorepresentante3 = request.POST.get("cttelefonorepresentante3")

        datoscliente = Personas_juridicas.objects\
            .filter(cxcliente=cliente.cxcliente).first()

        administrasocios_on=False; administraindividual_on=False

        if ladministrasocios: administrasocios_on= True
        if ladministraindividual: administraindividual_on= True

        if not datoscliente:
            datoscliente= Personas_juridicas(
                cxcliente = cliente.cxcliente,
                ctnombrecorto = ctnombrecorto,
                cxtipoempresa = cxtipoempresa,
                ctcontacto = ctcontacto,
                ladministrasocios = administrasocios_on,
                ladministraindividual = administraindividual_on,
                ctobjetosocial = ctobjetosocial,
                cxrepresentante1 = cxrepresentante1,
                ctrepresentante1 = ctrepresentante1,
                dvencimientocargorepresentante1 = dvencimientocargorepresentante1,
                ctcargorepresentante1 = ctcargorepresentante1,
                cxestadocivilrepresentante1 = cxestadocivilrepresentante1,
                cttelefonorepresentante1 = cttelefonorepresentante1,
                cxrepresentante2 = cxrepresentante2,
                ctrepresentante2 = ctrepresentante2,
                dvencimientocargorepresentante2 = dvencimientocargorepresentante2,
                ctcargorepresentante2 = ctcargorepresentante2,
                cxestadocivilrepresentante2 = cxestadocivilrepresentante2,
                cttelefonorepresentante2 = cttelefonorepresentante2,
                cxrepresentante3 = cxrepresentante3,
                ctrepresentante3 = ctrepresentante3,
                dvencimientocargorepresentante3 = dvencimientocargorepresentante3,
                ctcargorepresentante3 = ctcargorepresentante3,
                cxestadocivilrepresentante3 = cxestadocivilrepresentante3,
                cttelefonorepresentante3 = cttelefonorepresentante3,
                cxusuariocrea = request.user
            )
            if datoscliente:
                datoscliente.save()
        else:

            datoscliente.ctnombrecorto = ctnombrecorto
            datoscliente.cxtipoempresa = cxtipoempresa
            datoscliente.ctcontacto = ctcontacto
            datoscliente.ladministrasocios = administrasocios_on
            datoscliente.ladministraindividual = administraindividual_on
            datoscliente.ctobjetosocial = ctobjetosocial
            datoscliente.cxrepresentante1 = cxrepresentante1
            datoscliente.ctrepresentante1 = ctrepresentante1
            datoscliente.dvencimientocargorepresentante1 = dvencimientocargorepresentante1
            datoscliente.ctcargorepresentante1 = ctcargorepresentante1
            datoscliente.cxestadocivilrepresentante1 = cxestadocivilrepresentante1
            datoscliente.cttelefonorepresentante1 = cttelefonorepresentante1
            datoscliente.cxrepresentante2 = cxrepresentante2
            datoscliente.ctrepresentante2 = ctrepresentante2
            datoscliente.dvencimientocargorepresentante2 = dvencimientocargorepresentante2
            datoscliente.ctcargorepresentante2 = ctcargorepresentante2
            datoscliente.cxestadocivilrepresentante2 = cxestadocivilrepresentante2
            datoscliente.cttelefonorepresentante2 = cttelefonorepresentante2
            datoscliente.cxrepresentante3 = cxrepresentante3
            datoscliente.ctrepresentante3 = ctrepresentante3
            datoscliente.dvencimientocargorepresentante3 = dvencimientocargorepresentante3
            datoscliente.ctcargorepresentante3 = ctcargorepresentante3
            datoscliente.cxestadocivilrepresentante3 = cxestadocivilrepresentante3
            datoscliente.cttelefonorepresentante3 = cttelefonorepresentante3
            datoscliente.cxusuariomodifica = request.user.id

            datoscliente.save()

            return redirect("clientes:listaclientes")

    return render(request, template_name, contexto)

@login_required(login_url='/login/')
@permission_required('clientes.view_datos_generales', login_url='bases:sin_permisos')
def CuentasBancariasCliente(request, cliente_ruc):
    template_name = "clientes/listacuentasbancariascliente.html"
    cliente = Datos_generales.objects.filter(cxcliente=cliente_ruc).first()
    contexto={'cliente':cliente
            }
    return render(request, template_name, contexto)

def DetalleCuentasBancarias(request, cliente_ruc = None):
    # cliente = Datos_generales.objects.filter(cxcliente=cliente_id).first()
    cuentas = Cuentas_bancarias.objects\
        .filter(cxparticipante__cxparticipante=cliente_ruc)\
            .filter( leliminado = False)
    tempBlogs = []

    # Converting `QuerySet` to a Python Dictionary
    for i in range(len(cuentas)):
        tempBlogs.append(DocumentoADictionario(cuentas[i])) # Converting `QuerySet` to a Python Dictionary

    docjson = tempBlogs

    data = {"total": cuentas.count(),
        "totalNotFiltered": cuentas.count(),
        "rows": docjson 
        }

    return HttpResponse(JsonResponse( data))

def DocumentoADictionario(doc):
    output = {}
    output['id'] = doc.id
    output["Banco"] = doc.cxbanco.ctbanco
    output["TipoCuenta"] = doc.cxtipocuenta
    output["Cuenta"] = doc.cxcuenta
    output["Propia"] = doc.lpropia
    output["Activa"] = doc.lactiva

    # determinar si la cuenta es la de transferencia
    x = Cuenta_transferencia.objects.filter(cxcuenta = doc).first()
    if x:
        output["Default"] = True
    else:
        output["Default"] = False

    output["IdPropietario"] = doc.cxidpropietario
    output["Propietario"] =  doc.ctnombrepropietario

    return output

@login_required(login_url='/login/')
@permission_required('clientes.update_cuentas_bancarias', login_url='bases:sin_permisos')
def EliminarCuentaBancaria(request, pk):
    # la eliminacion es lógica

    cuenta = Cuentas_bancarias.objects.filter(pk=pk).first()

    if not cuenta:
        return HttpResponse("Cuenta no encontrada")

    if request.method=="GET":

        with transaction.atomic():

            # marcar como eliminado
            cuenta.leliminado = True
            cuenta.cxusuarioelimina = request.user.id
            cuenta.save()

            # eliminar la relacion cuentas de transferencias
            cliente = cuenta.cxparticipante.cxparticipante
            ctacte = Cuenta_transferencia.objects.filter(cxcliente=cliente).first()

            if ctacte.cxcuenta.id == pk:
                ctacte.leliminado = True
                ctacte.cxusuarioelimina = request.user.id
                ctacte.save()

    return HttpResponse("OK")

@login_required(login_url='/login/')
@permission_required('clientes.update_cuentas_bancarias', login_url='bases:sin_permisos')
def ActualizarCuentaTransferencia(request, pk, cliente_ruc):

    cuenta = Cuentas_bancarias.objects.filter(pk=pk).first()

    if not cuenta:
        return HttpResponse(0)

    if request.method=="GET":
        cliente = Datos_generales.objects.filter(cxcliente=cliente_ruc).first()
        ctacte = Cuenta_transferencia.objects.filter(cxcliente=cliente).first()
        if not ctacte:
            ctacte = Cuenta_transferencia(cxcliente=cliente
            , cxcuenta=cuenta
            , cxusuariocrea=request.user)
        else:        
            ctacte.cxcuenta = cuenta

        ctacte.save()

    return HttpResponse("OK")

@login_required(login_url='/login/')
@permission_required('clientes.view_datos_compradores', login_url='bases:sin_permisos')
def DatosCompradores(request, comprador_id=None):
    template_name="clientes/datoscomprador_form.html"
    contexto={}
    idcomprador={}
    datosparticipante={}
    formulario={}
    form_comprador={}
    datoscomprador={}
    
    if request.method=='GET':
        datosparticipante = Datos_participantes.objects\
            .filter(cxparticipante=comprador_id).first()
            
        if datosparticipante:
            e={ 
                'cxtipoid':datosparticipante.cxtipoid,
                'cxparticipante':datosparticipante.cxparticipante,
                'ctnombre':datosparticipante.ctnombre,
                # 'cxzona': datosparticipante.cxzona,
                'cxlocalidad':datosparticipante.cxlocalidad,
                # 'cxestado':datosparticipante.cxestado,
                'ctdireccion':datosparticipante.ctdireccion,
                'ctemail':datosparticipante.ctemail,
                'ctemail2':datosparticipante.ctemail2,
                'cttelefono1':datosparticipante.cttelefono1,
                'cttelefono2':datosparticipante.cttelefono2,
                'ctcelular':datosparticipante.ctcelular,
                'ctgirocomercial':datosparticipante.ctgirocomercial,
            }
            idcomprador=datosparticipante.cxparticipante
            formulario=ParticipanteForm(e)
            # si encuentra registro de datos participantes buscar en datos de cliente

            datoscomprador = Datos_compradores.objects\
                .filter(cxcomprador=idcomprador).first()
            
            if datoscomprador:
                e={
                    'cxactividad':datoscomprador.cxactividad,
                    'cxcomprador':datosparticipante.cxparticipante
                }
                form_comprador=CompradorForm(e)
        else:
            formulario=ParticipanteForm()
            form_comprador=CompradorForm()

            # datoscliente=Datos_generales.objects.filter(pk=0)
            
    contexto={'datosparticipante':datosparticipante
            , 'form_participante':formulario
            , 'form_comprador':form_comprador
            }

    if request.method=='POST':
        # cxtipoid=request.POST.get("cxtipoid")
        cxtipoid="R"
        idcomprador=request.POST.get("cxparticipante")
        ctnombre=request.POST.get("ctnombre")
        # cxzona=request.POST.get("cxzona")
        cxlocalidad=request.POST.get("cxlocalidad")
        # cxestado=request.POST.get("cxestado")
        ctdireccion=request.POST.get("ctdireccion")
        cttelefono1=request.POST.get("cttelefono1")
        cttelefono2=request.POST.get("cttelefono2")
        ctcelular=request.POST.get("ctcelular")
        ctemail=request.POST.get("ctemail")
        ctemail2=request.POST.get("ctemail2")
        ctgirocomercial=request.POST.get("ctgirocomercial")

        if not comprador_id:
            datosparticipante = Datos_participantes(
                cxtipoid=cxtipoid,
                cxparticipante=idcomprador,
                ctnombre=ctnombre,
                # 'cxzona': datosparticipante.cxzona,
                cxlocalidad=cxlocalidad,
                # 'cxestado':datosparticipante.cxestado,
                ctdireccion=ctdireccion,
                ctemail=ctemail,
                ctemail2=ctemail2,
                cttelefono1=cttelefono1,
                cttelefono2=cttelefono2,
                ctcelular=ctcelular,
                ctgirocomercial=ctgirocomercial,
                cxusuariocrea= request.user
            )
            if datosparticipante:
                datosparticipante.save()
        else:
            datosparticipante = Datos_participantes.objects\
                .filter(cxparticipante=comprador_id).first()

            if datosparticipante:
                datosparticipante.cxtipoid = cxtipoid
                datosparticipante.cxparticipante=idcomprador
                datosparticipante.ctnombre=ctnombre
                # datosparticipante.cxzona=cxzona
                datosparticipante.cxlocalidad=cxlocalidad
                # datosparticipante.cxestado=cxestado
                datosparticipante.ctdireccion=ctdireccion
                datosparticipante.ctemail=ctemail
                datosparticipante.ctemail2=ctemail2
                datosparticipante.cttelefono1=cttelefono1
                datosparticipante.cttelefono2=cttelefono2
                datosparticipante.ctcelular=ctcelular
                datosparticipante.ctgirocomercial=ctgirocomercial
                datosparticipante.cxusuariomodifica = request.user.id

                datosparticipante.save()
            
        # datos en tabla compradores

        datoscomprador = Datos_compradores.objects\
            .filter(cxcomprador=idcomprador).first()

        cxactividad = request.POST.get("cxactividad")

        if not datoscomprador:
            datoscomprador= Datos_compradores(
                cxcomprador = datosparticipante,
                cxactividad = cxactividad,
                cxusuariocrea = request.user
            )
            if datoscomprador:
                datoscomprador.save()
        else:
            datoscomprador.cxactividad=cxactividad
            datoscomprador.cxusuariomodifica = request.user.id

            datoscomprador.save()

        return redirect("clientes:listacompradores")

    return render(request, template_name, contexto)

