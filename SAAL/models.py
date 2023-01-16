
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

DOC_CHOICES = (
    ('En Servicio', _(u"En Servicio (ES)")),
    ('Baja Presion', _(u"Baja Presion (BP)")),
    ('Suspendido', _(u"Suspendido (SP)")),
    ('Daño Critico', _(u"Daño Critico (DC)"))
)


class Tarifa(models.Model):
    IdTarifa = models.CharField(primary_key=True, max_length=4, null=False)
    Valor = models.CharField(max_length=5, null=False)
    Mantenimiento = models.CharField(max_length=5, null=False)
    Recargo = models.CharField(max_length=5, null=False)
    TarifaReconexion = models.CharField(max_length=5, null=True)
    TarifaSuspencion = models.CharField(max_length=5, null=True)
    bifamiliar = models.CharField(max_length=5, null=True)
    especial = models.CharField(max_length=5, null=True)
    multifamiliar = models.CharField(max_length=5, null=True)
    FechaInicial = models.DateTimeField(auto_now=True)
    Ano = models.CharField(max_length=4, null=True)

    def __str__(self):
        return "%s" % self.IdTarifa

    class Meta:
        verbose_name_plural = "Listado de Tarifas"
        verbose_name = "Tarifa"


class Acueducto(models.Model):
    IdAcueducto = models.CharField(primary_key=True, max_length=9, null=False)
    Nombre = models.CharField(max_length=150, null=False)
    DirOficina = models.CharField(max_length=100, null=False)
    logo = models.ImageField(upload_to='usuarios', default='usuarios/usuario.png')
    Relegal = models.CharField(max_length=60, null=False)
    Telefono = models.CharField(max_length=11, null=False)
    Estado = models.CharField(max_length=30, null=True, choices=DOC_CHOICES, default='ES')
    IdTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    Email = models.EmailField(null=True)

    def __str__(self):
        return "%s" % self.IdAcueducto

    class Meta:
        verbose_name_plural = "Lista de Acueductos"
        verbose_name = "Lista de Acueductos"


DOC_CHOICES2 = (
    ('Presidente', _(u"Presidente (Pdte)")),
    ('Cartera', _(u"Cartera (Ct)")),
    ('Operario', _(u"Operario (Ope)")),
    ('Auxiliar', _(u"Auxiliar (Aux)")),
    ('Administrador de sistemas', _(u"Administrador de sistemas(Dir)")),
)


class Usuario(models.Model):
    IdUsuario = models.AutoField(primary_key=True)
    fotoUsuario = models.ImageField(upload_to='usuarios', default='usuarios/usuario.png')
    TipoUsuario = models.CharField(max_length=100, blank=True, null=True, choices=DOC_CHOICES2, default='Auxiliar')
    FechaCreacion = models.DateTimeField(auto_now_add=True)
    Departamento = models.CharField(max_length=50, null=False)
    celular = models.CharField(max_length=10, null=False)
    usuid = models.OneToOneField(User, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.usuid.username

    class Meta:
        verbose_name_plural = "Datos usuarios"
        verbose_name = "Datos usuario"


class Poblacion(models.Model):
    IdPoblacion = models.CharField(primary_key=True, max_length=15, null=False)
    Descripcion = models.CharField(max_length=50, null=False)

    def __str__(self):
        return "%s" % self.Descripcion

    class Meta:
        verbose_name_plural = "Tipos de poblacion"
        verbose_name = "Tipo de poblacion"


class Propietario(models.Model):
    IdPropietario = models.CharField(primary_key=True, max_length=15, null=False)
    Nombres = models.CharField(max_length=50, null=False)
    Apellidos = models.CharField(max_length=50, null=False)
    NoTelefono = models.CharField(max_length=60, null=False)
    Email = models.EmailField(max_length=150, null=True)
    IdPoblacion = models.ForeignKey(Poblacion, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.Nombres, self.Apellidos)

    class Meta:
        verbose_name_plural = "Lista de Propietarios"
        verbose_name = "Lista de Propietarios"


DOC_CHOICES3 = (
    ('1', _(u"Bajo-bajo (1)")),
    ('2', _(u"Bajo (2)")),
    ('3', _(u"Medio-bajo  (3)")),
    ('Co', _(u"Comercial (Co)")),
    ('Ins', _(u"Industrial (Ins)"))
)
DOC_CHOICES4 = (
    ('Operativo', _(u"Operativo (OP)")),
    ('Suspendido', _(u"Suspendido (SP)")),
    ('Mantenimiento', _(u"Mantenimiento (MT)")),
    ('Retirado', _(u"Retirado  (RD)")),
    ('Conexion nueva', _(u"Conexion nueva (CN)"))
)

DOC_CHOICES5 = (
    ('Residencial', _(u"Instalacion Residencial (Res)")),
    ('Comercial', _(u"Instalacion Comercial (Com)")),
    ('Industrial', _(u"Instalacion Industrial (Ind)"))
)

DOC_CHOICES6 = (
    ('2', _(u"Ciclo pasonivel viejo")),
    ('3', _(u"Ciclo Barrio nuevo")),
    ('4', _(u"Ciclo caimalito via principal")),
    ('5', _(u"Ciclo 20 julio")),
)

DOC_CHOICES7 = (
    ('Unifamiliar', _(u"Unifamiliar")),
    ('Bifamiliar', _(u"Bifamiliar")),
    ('Multifamiliar', _(u"Multifamiliar")),
    ('Comercial', _(u"Comercial")),
    ('Especial', _(u"Especial")),
    ('Agricola', _(u"Agricola"))
)

DOC_CHOICES8 = (
    ('Pasonivel Viejo', _(u"Sector pasonivel viejo")),
    ('Pasonivel Destapada', _(u"Sector pasonivel destapada")),
    ('Caimalito Centro', _(u"Sector caimalito centro")),
    ('Barrio Nuevo', _(u"Sector barrio nuevo")),
    ('20 de julio', _(u"Sector 20 de julio")),
    ('Pasonivel la loma', _(u"Sector pasonivel la loma")),
    ('Hacienda', _(u"Hacienda")),
    ('Via nacional', _(u"Sector Via nacional")),
    ('Caimalito centro dos', _(u"Sector caimalito centro dos")),
    ('Destapada', _(u"Sector destapada")),
)

DOC_CHOICES9 = (
    ('Anulada', _(u"Anular solicitud")),
    ('Aprobada', _(u"Aprobar solicitud"))
)
DOC_CHOICES30 = (
    ('1', _(u"1 - predio")),
    ('2', _(u"2 - predios")),
    ('3', _(u"3 - predios")),
    ('4', _(u"4 - predios")),
    ('5', _(u"5 - predios"))
)


class Vivienda(models.Model):
    IdVivienda = models.CharField(primary_key=True, max_length=15, null=False)
    Direccion = models.CharField(max_length=20, null=False, choices=DOC_CHOICES8)
    NumeroCasa = models.CharField(max_length=8, null=False)
    Piso = models.CharField(max_length=2, null=True, blank=True)
    CantPredios = models.CharField(null=False, max_length=40, choices=DOC_CHOICES30)
    Ciclo = models.CharField(null=False, max_length=40, choices=DOC_CHOICES6)
    TipoInstalacion = models.CharField(max_length=60, null=False, choices=DOC_CHOICES5, default='Res')
    Estrato = models.CharField(max_length=60, null=False, choices=DOC_CHOICES3, default='1')
    EstadoServicio = models.CharField(max_length=60, null=False, choices=DOC_CHOICES4, default='EC')
    IdPropietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    usuid = models.ForeignKey(User, on_delete=models.CASCADE)
    MatriculaAnt = models.CharField(max_length=4, null=False)
    InfoInstalacion = models.CharField(max_length=30, choices=DOC_CHOICES7)
    ProfAcometida = models.CharField(max_length=4, null=False)
    CantHabitantes = models.CharField(max_length=2, null=False)
    FichaCastral = models.CharField(max_length=26, null=True)
    Diametro = models.CharField(max_length=5, null=True)

    def __str__(self):
        return "%s %s %s" % (self.IdVivienda, self.Direccion, self.NumeroCasa)

    class Meta:
        verbose_name_plural = "Lista de Viviendas"
        verbose_name = "Lista de Viviendas"


class Ciclo(models.Model):
    IdCiclo = models.CharField(max_length=5, primary_key=True)
    Nombre = models.CharField(max_length=10)

    def __str__(self):
        return "%s" % self.Nombre

    class Meta:
        verbose_name_plural = "Lista de Ciclos"
        verbose_name = "Listado de ciclos"


class EstadoCuenta(models.Model):
    IdEstadoCuenta = models.AutoField(primary_key=True)
    Valor = models.IntegerField(default=0)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=100)
    FechaActualizacion = models.DateTimeField(auto_now=True)
    Descripcion = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.IdEstadoCuenta

    class Meta:
        verbose_name_plural = "Estados de cuenta"
        verbose_name = "Estado de cuenta"


class Factura(models.Model):
    IdFactura = models.AutoField(primary_key=True)
    Matricula = models.CharField(max_length=100, null=True)
    Estado = models.CharField(max_length=100, null=False)
    IdEstadoCuenta = models.ForeignKey(EstadoCuenta, on_delete=models.CASCADE)
    direccionentrega = models.CharField(max_length=100, null=True)
    periodofacturado = models.CharField(max_length=50, null=True)
    aporteporconsumo = models.CharField(max_length=100, null=True)
    cuotamatricula = models.CharField(max_length=100, null=True)
    reconexion = models.CharField(max_length=100, null=True)
    suspencion = models.CharField(max_length=100, null=True)
    TotalConsumo = models.CharField(max_length=100, null=True)
    facturasvencidas = models.CharField(max_length=100, null=True)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    FechaLimite = models.DateTimeField(null=True)
    IdCiclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE)
    OtrosCobros = models.CharField(max_length=100, null=False)
    Total = models.CharField(max_length=100, null=False)

    def __str__(self):
        return "%s" % self.IdFactura

    class Meta:
        verbose_name_plural = "Lista de facturas"
        verbose_name = "Generar factura"


DOC_CHOICES10 = (
    ('No certificada', _(u"No certificada")),
    ('Certificada', _(u"Certificada"))
)

DOC_CHOICES11 = (
    ('SI', _(u"SI")),
    ('NO', _(u"NO"))
)


class Certificaciones(models.Model):
    IdCertificacion = models.AutoField(primary_key=True)
    Nit = models.CharField(max_length=10, null=False)
    NombreEmpresa = models.CharField(max_length=300, null=False)
    Estado = models.CharField(max_length=25, null=False, choices=DOC_CHOICES10)
    Soporte = models.CharField(max_length=2, choices=DOC_CHOICES11, null=True, blank=True)
    Descripcion = models.CharField(max_length=500, null=True, blank=True)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.Estado

    class Meta:
        verbose_name_plural = "Listado de certificaciones"
        verbose_name = "Certificacion"


class ConfirCerti(models.Model):
    IdOrden = models.AutoField(primary_key=True)
    IdUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Fecha = models.DateTimeField(auto_now=True)
    IdCertificacion = models.ForeignKey(Certificaciones, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdOrden

    class Meta:
        verbose_name_plural = "listado de confirmaciones"
        verbose_name = "confirmacion"


class Medidores(models.Model):
    IdMedidor = models.CharField(primary_key=True, max_length=10, null=False)
    Marca = models.CharField(max_length=20, null=False)
    Tipo = models.CharField(max_length=20, null=False)
    LecturaInicial = models.CharField(max_length=6, null=False)
    AnoFabricacion = models.CharField(max_length=4, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdMedidor

    class Meta:
        verbose_name_plural = "Listado de Medidores"
        verbose_name = "Medidor"


class ValorMatricula(models.Model):
    IdValor = models.AutoField(primary_key=True)
    Valor = models.CharField(max_length=10, null=False)
    Fecha = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.Valor

    class Meta:
        verbose_name_plural = "listado de valor de matricula"
        verbose_name = "valor matricula"


DOC_CHOICES12 = (
    ('1', _(u"1")),
    ('2', _(u"2")),
    ('3', _(u"3")),
    ('4', _(u"4")),
    ('5', _(u"5")),
    ('6', _(u"6")),
    ('12', _(u"12")),
    ('24', _(u"24")),
    ('36', _(u"36"))
)


class CobroMatricula(models.Model):
    IdCobroM = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=20, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=15, null=False)
    IdValor = models.ForeignKey(ValorMatricula, on_delete=models.CASCADE)
    CantCuotas = models.CharField(max_length=10, null=False, choices=DOC_CHOICES12)
    CuotasPendientes = models.CharField(max_length=10, null=False)
    ValorPendiente = models.CharField(max_length=50, null=False)
    Cuota = models.CharField(max_length=50, null=False)

    def __str__(self):
        return "%s %s" % (self.IdCobroM, self.Descripcion)

    class Meta:
        verbose_name_plural = "Cobro matriculas"
        verbose_name = "Cobro matricula"


class SolicitudGastos(models.Model):
    IdSoGa = models.AutoField(primary_key=True)
    IdUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Descripcion = models.CharField(max_length=5000, null=False)
    TipoSolicitud = models.CharField(max_length=50, null=False)
    Valor = models.CharField(max_length=10, null=False)
    Estado = models.CharField(max_length=15, null=False, choices=DOC_CHOICES9)
    Fecha = models.DateTimeField(auto_now=True, null=False)
    AreaResponsable = models.CharField(max_length=100, null=False)
    NumeroFactura = models.CharField(max_length=10, null=False)

    def __str__(self):
        return "%s" % self.IdSoGa

    class Meta:
        verbose_name_plural = "solicitudes de gastos"
        verbose_name = "Solicitud de gasto"


DOC_CHOICES13 = (
    ('AccessPanel', _(u"Acceso - panel de administracion - AccessPanel")),
    ('AVLV', _(u"Acceso - Ver listado viviendas - AVLV")),
    ('AVF', _(u"Acceso - Ver factura - AVF")),
    ('AB', _(u"Acceso - Buscador - AB")),
    ('ALS', _(u"Acceso - Listado de suscriptores - ALS")),
    ('ALP', _(u"Acceso - Listado de predios - ALP")),
    ('AR', _(u"Acceso - Reportes - AR")),
    ('ACC', _(u"Acceso - Cuentas de cobro - ACC")),
    ('GCA', _(u"Generar - Cobro de aportes - GCA")),
    ('AIS', _(u"Agregar - Informacion suscriptor - AIS")),
    ('AIP', _(u"Agregar - Informacion predio - AIP")),
    ('AMFV', _(u"Acceso - Modulo de facturas vencidas - AMFV")),
    ('AGF', _(u"Acceso - Generador de facturas - AGF")),
    ('GF', _(u"Generar - Facturas - GF")),
    ('AF', _(u"Acceso - Anular facturas - AF")),
    ('AC', _(u"Acceso - Consumos - AC")),
    ('ASR', _(u"Acceso - Suspenciones y Reconexiones - ASR")),
    ('ACP', _(u"Acceso - Control presupuestal - ACP")),
    ('ACF', _(u"Acceso - Cierre financiero - ACF")),
    ('APQRS', _(u"Acceso - PQRS - APQRS")),
)


class Permisos(models.Model):
    IdPermiso = models.AutoField(primary_key=True)
    TipoPermiso = models.CharField(max_length=50, null=False, choices=DOC_CHOICES13)
    usuid = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s %s" % (self.IdPermiso, self.TipoPermiso, self.usuid)

    class Meta:
        verbose_name_plural = "Permisos"
        verbose_name = "Permiso"


DOC_CHOICES14 = (
    ('Peticion', _(u"Peticion")),
    ('Queja', _(u"Queja")),
    ('Reclamo', _(u"Reclamo")),
    ('Sugerencia', _(u"Sugerencia")),
)
DOC_CHOICES15 = (
    ('Atencion de daño - Externo', _(u"Atencion de daño - Externo")),
    ('Atencion de daño - Interno', _(u"Atencion de daño - Interno")),
    ('Facturacion', _(u"Facturacion")),
    ('Administracion', _(u"Administracion")),
    ('Multas', _(u"Multas")),
    ('Tesoreria', _(u"Tesoreria")),
)


class Pqrs(models.Model):
    IdPqrs = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=10, null=True)
    FechaRadicado = models.DateTimeField(auto_now_add=True, null=False)
    Telefono = models.CharField(max_length=10, null=True)
    Correo = models.EmailField(max_length=60, null=True)
    Direccion = models.CharField(max_length=200, null=True)
    TipoSolicitud = models.CharField(max_length=50, null=True, choices=DOC_CHOICES14)
    Clasificacion = models.CharField(max_length=50, null=True, choices=DOC_CHOICES15)
    Descripcion = models.TextField(max_length=5000, null=True)
    usuid = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=40, null=False)

    def __str__(self):
        return "%s %s" % (self.IdPqrs, self.TipoSolicitud)

    class Meta:
        verbose_name_plural = "Pqr"
        verbose_name = "Pqrs"


class RespuestasPqrs(models.Model):
    IdRespuesta = models.AutoField(primary_key=True)
    IdPqrs = models.ForeignKey(Pqrs, on_delete=models.CASCADE)
    Fecha = models.DateTimeField(auto_now_add=True)
    Descripcion = models.CharField(max_length=5000, null=False)
    Soporte = models.FileField(upload_to='respuestaspqr/', null=True)

    def __str__(self):
        return "%s" % self.IdRespuesta

    class Meta:
        verbose_name_plural = "Respuestas"
        verbose_name = "Respuestas"


class Pagos(models.Model):
    IdPago = models.AutoField(primary_key=True)
    FechaPago = models.DateTimeField(auto_now=True, null=False)
    IdFactura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    Ano = models.CharField(max_length=4, null=False)
    Descripcion = models.CharField(max_length=20, null=False)
    ValorPago = models.CharField(max_length=10, null=False)
    Efectivo = models.CharField(max_length=10, null=False)
    Devuelta = models.CharField(max_length=10, null=False)
    resta = models.CharField(max_length=10, null=True)
    IdUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdPago

    class Meta:
        verbose_name_plural = "Pagos"
        verbose_name = "Pago"


class OrdenesSuspencion(models.Model):
    IdOrden = models.AutoField(primary_key=True)
    Deuda = models.CharField(max_length=10, null=False)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    FechaEjecucion = models.DateTimeField(null=False)
    Generado = models.CharField(max_length=60, null=False)
    Estado = models.CharField(max_length=40, null=False)
    UsuarioEjecuta = models.CharField(max_length=100, null=False)
    IdEstadoCuenta = models.ForeignKey(EstadoCuenta, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdOrden

    class Meta:
        verbose_name_plural = "Ordenes de suspencion"
        verbose_name = "Orden de suspencion"


class OrdenesReconexion(models.Model):
    IdOrden = models.AutoField(primary_key=True)
    Deuda = models.CharField(max_length=10, null=False)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    FechaEjecucion = models.DateTimeField(null=False)
    Generado = models.CharField(max_length=20, null=False)
    Estado = models.CharField(max_length=40, null=False)
    UsuarioEjecuta = models.CharField(max_length=30, null=False)
    IdEstadoCuenta = models.ForeignKey(EstadoCuenta, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdOrden

    class Meta:
        verbose_name_plural = "Ordenes de Reconexion"
        verbose_name = "Orden de Reconexion"


class NovedadVivienda(models.Model):
    IdNovedad = models.AutoField(primary_key=True)
    TipoNovedad = models.CharField(max_length=100, null=False)
    Descripcion = models.CharField(max_length=5000, null=False)
    Valor = models.CharField(max_length=100, null=False)
    usuid = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Fecha = models.DateTimeField(auto_now_add=True)
    EstadoCuenta = models.ForeignKey(EstadoCuenta, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.TipoNovedad

    class Meta:
        verbose_name_plural = "Lista de Novedades Viviendas"
        verbose_name = "lista de Novedades"


class Cierres(models.Model):
    IdCierre = models.AutoField(primary_key=True)
    Ingresos = models.CharField(max_length=100, null=False)
    Gastos = models.CharField(max_length=100, null=False)
    Presupuesto = models.CharField(max_length=100, null=False)
    Ciclo = models.CharField(max_length=100, null=False)
    Ano = models.CharField(max_length=100, null=False)
    Fecha = models.DateTimeField(auto_now_add=True)
    NoRecaudo = models.CharField(max_length=100, null=False)
    Recaudado = models.CharField(max_length=100, null=False)

    def __str__(self):
        return "%s %s" % (self.IdCierre, self.Ciclo)

    class Meta:
        verbose_name_plural = "Lista de cierres mensuales"
        verbose_name = "Cierre mensual"


class NovedadesGenerales(models.Model):
    IdNovedad = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=5000, null=False)
    TipoNovedad = models.CharField(max_length=100, null=False)
    Fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=30, null=False)
    matricula = models.CharField(max_length=30, null=False)

    def __str__(self):
        return "%s %s" % (self.IdNovedad, self.TipoNovedad)

    class Meta:
        verbose_name_plural = "Novedades generales"
        verbose_name = "Novedad general"


class CobroOrdenes(models.Model):
    IdOrden = models.AutoField(primary_key=True)
    Fecha = models.DateTimeField(auto_now=True, null=False)
    IdEstadoCuenta = models.ForeignKey(EstadoCuenta, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=30, null=False)
    Valor = models.CharField(max_length=30, null=False)
    IdOrdenT = models.CharField(max_length=30, null=False)
    TipoOrden = models.CharField(max_length=30, null=False)

    def __str__(self):
        return "%s %s" % (self.IdOrden, self.TipoOrden)

    class Meta:
        verbose_name_plural = "Cobro ordenes SR"
        verbose_name = "Cobro orden"


class PagoOrdenes(models.Model):
    IdPagoSR = models.AutoField(primary_key=True)
    FechaPago = models.DateTimeField(auto_now=True, null=False)
    Valor = models.CharField(max_length=30, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    IdOrden = models.ForeignKey(CobroOrdenes, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.IdPagoSR

    class Meta:
        verbose_name_plural = "PagoOrdenes"
        verbose_name = "Pago orden"


class NovedadesSistema(models.Model):
    IdNovedad = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=150, null=False)
    Fecha = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.IdNovedad

    class Meta:
        verbose_name_plural = "Novedades"
        verbose_name = "Novedad"
