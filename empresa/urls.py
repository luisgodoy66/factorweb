from django.urls import URLPattern, path
from .views import TiposFactoringView, TipoFactoringNew , TipoFactoringEdit\
    , TasasFactoringView, TasaFactoringNew, TasaFactoringEdit\
    , ClasesParticipanteView, ClasesParticipanteNew\
    , CuentasBancariasView, CuentaBancariaNew, CuentaBancariaEdit\
    , LocalidadesView, LocalidadesNew, LocalidadesEdit

urlpatterns = [
    path('listatiposfactoring/',TiposFactoringView.as_view()
    , name='listatiposfactoring'),
    path('tipofactoringnuevo/',TipoFactoringNew.as_view()
    , name='tipofactoring_nuevo'),
    path('tipofactoringedit/<int:pk>',TipoFactoringEdit.as_view()
    , name='tipofactoring_editar'),
    path('listatasasfactoring/',TasasFactoringView.as_view()
    , name='listatasasfactoring'),
    path('tasafactoringnueva/',TasaFactoringNew.as_view()
    , name='tasafactoring_nueva'),
    path('tasafactoringedit/<int:pk>',TasaFactoringEdit.as_view()
    , name='tasafactoring_editar'),
    path('listaclasesparticipantes/',ClasesParticipanteView.as_view()
    , name='listaclasesparticipantes'),
    path('datosclaseparticipante_nueva', ClasesParticipanteNew.as_view()
    , name="datosclaseparticipante_nueva"),
    path('listacuentasbancarias/',CuentasBancariasView.as_view()
    ,name='listacuentasbancarias'),
    path('cuentabancarianueva/',CuentaBancariaNew.as_view()
    ,name='cuentabancaria_nueva'),
    path('cuentabancariaedit/<int:pk>',CuentaBancariaEdit.as_view()
    ,name='cuentabancaria_editar'),
    path('listalocalidades/',LocalidadesView.as_view(),name='listalocalidades'),
    path('localidadnueva/',LocalidadesNew.as_view(),name='localidad_nueva'),
    path('localidadedit/<int:pk>',LocalidadesEdit.as_view(),name='localidad_editar'),
 ]