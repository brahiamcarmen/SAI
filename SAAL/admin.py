from django.contrib import admin
from SAAL.models import Usuario, ValorMatricula
from SAAL.models import Acueducto
from SAAL.models import Propietario
from SAAL.models import Vivienda
from SAAL.models import Ciclo
from SAAL.models import EstadoCuenta, Pagos
from SAAL.models import Tarifa, Pqrs
from SAAL.models import Medidores
from SAAL.models import Poblacion, SolicitudGastos, Permisos, RespuestasPqrs

admin.site.register(Acueducto)
admin.site.register(Propietario)
admin.site.register(Vivienda)
admin.site.register(Ciclo)
admin.site.register(EstadoCuenta)
admin.site.register(Tarifa)
admin.site.register(Medidores)
admin.site.register(Poblacion)
admin.site.register(SolicitudGastos)
admin.site.register(ValorMatricula)
admin.site.register(Permisos)
admin.site.register(Pqrs)
admin.site.register(RespuestasPqrs)
admin.site.register(Pagos)
admin.site.register(Usuario)