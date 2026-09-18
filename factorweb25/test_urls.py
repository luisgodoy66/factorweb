"""URLconf vacio para las suites que no resuelven URLs.

`factorweb25.urls` importa las vistas de todas las apps, y esas vistas a su
vez importan modelos de apps que no forman parte de las suites enfocadas
(p. ej. empresa.tests_seguridad). Al no declarar rutas, la suite puede
ejecutarse sin arrastrar todo el proyecto.
"""
urlpatterns = []
