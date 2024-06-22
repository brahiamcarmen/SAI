
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
    IdTarifa = models.AutoField(primary_key=True)
    Valor = models.CharField(max_length=5, null=False)
    Mantenimiento = models.CharField(max_length=5, null=False)
    Recargo = models.CharField(max_length=5, null=False)
    TarifaReconexion = models.CharField(max_length=5, null=True)
    TarifaSuspencion = models.CharField(max_length=5, null=True)
    comercial = models.CharField(max_length=5, null=True)
    industrial = models.CharField(max_length=5, null=True)
    oficial = models.CharField(max_length=5, null=True)
    especial = models.CharField(max_length=5, null=True)
    valormetro = models.CharField(max_length=10, null=True)
    m3 = models.CharField(max_length=4, null=True)
    FechaInicial = models.DateTimeField(auto_now=True)
    Ano = models.CharField(max_length=4, null=True)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdTarifa

    class Meta:
        verbose_name_plural = "Listado de Tarifas"
        verbose_name = "Tarifa"

class Sectores(models.Model):
    IdSector= models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=10)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.Nombre

    class Meta:
        verbose_name_plural = "Lista de sectores"
        verbose_name = "Listado de sectores"

class Acueducto(models.Model):
    IdAcueducto = models.CharField(primary_key=True, max_length=9, null=False)
    Nombre = models.CharField(max_length=150, null=False)
    Sigla = models.CharField(max_length=20, null=True)
    DirOficina = models.CharField(max_length=100, null=False)
    logo = models.ImageField(upload_to='usuarios')
    Relegal = models.CharField(max_length=60, null=False)
    Telefono = models.CharField(max_length=11, null=False)
    Estado = models.CharField(max_length=30, null=True, choices=DOC_CHOICES, default='ES')
    IdTarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE)
    Email = models.EmailField(null=True)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdAcueducto

    class Meta:
        verbose_name_plural = "Lista de Acueductos"
        verbose_name = "Lista de Acueductos"


DOC_CHOICES2 = (
    ('Presidente', _(u"Presidente")),
    ('Operario', _(u"Operario)")),
    ('Secretario/a', _(u"Secretario/a")),
    ('Tesorero/a', _(u"Tesorero/a")),
    ('Auxiliar', _(u"Auxiliar")),
)

DOC_CHOICES22 = (
    ('Nivel 1', _(u"Nivel 1")),
    ('Nivel 2', _(u"Nivel 2")),
    ('Nivel 3', _(u"Nivel 3")),
)

DOC_CHOICES23 = (
    ('Area administrativa', _(u"Area administrativa")),
    ('Area operativa', _(u"Area operativa)")),
)
class Usuario(models.Model):
    IdUsuario = models.CharField(primary_key=True,max_length=25, null=False)
    fotoUsuario = models.ImageField(upload_to='usuarios', default='usuarios/usuario.png')
    TipoUsuario = models.CharField(max_length=100, null=True, choices=DOC_CHOICES22)
    FechaCreacion = models.DateTimeField(auto_now_add=True)
    Cargo = models.CharField(max_length=50, null=False,choices=DOC_CHOICES2)
    Departamento = models.CharField(max_length=50, null=False, choices=DOC_CHOICES23)
    celular = models.CharField(max_length=10, null=False)
    usuid = models.OneToOneField(User, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.usuid.username

    class Meta:
        verbose_name_plural = "Datos usuarios"
        verbose_name = "Datos usuario"


class Poblacion(models.Model):
    IdPoblacion = models.CharField(primary_key=True, max_length=15, null=False)
    Descripcion = models.CharField(max_length=50, null=False)
    objects = models.Manager()
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
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
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
    ('Especial', _(u"Especial")),
)

DOC_CHOICES8 = (
    ('Pasonivel Viejo', _(u"Sector pasonivel viejo")),
    ('Pasonivel Destapada', _(u"Sector pasonivel destapada")),
    ('Caimalito Centro', _(u"Sector caimalito centro")),
    ('Barrio Nuevo', _(u"Sector barrio nuevo")),
    ('20 de julio', _(u"Sector 20 de julio")),
    ('Hacienda', _(u"Hacienda")),
    ('Carbonera', _(u"Carbonera")),
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
    EstadoServicio = models.CharField(max_length=60, null=False, default='Operativo')
    IdPropietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    usuid = models.ForeignKey(User, on_delete=models.CASCADE)
    MatriculaAnt = models.CharField(max_length=4, null=False)
    InfoInstalacion = models.CharField(max_length=30, choices=DOC_CHOICES7)
    ProfAcometida = models.CharField(max_length=4, null=False)
    CantHabitantes = models.CharField(max_length=2, null=False)
    FichaCastral = models.CharField(max_length=26, null=True)
    Diametro = models.CharField(max_length=5, null=True)
    # You should have the default 'objects' manager by default
    objects = models.Manager()

    def __str__(self):
        return "%s %s %s" % (self.IdVivienda, self.Direccion, self.NumeroCasa)

    class Meta:
        verbose_name_plural = "Lista de Viviendas"
        verbose_name = "Lista de Viviendas"


class Ciclo(models.Model):
    IdCiclo = models.CharField(max_length=5, primary_key=True)
    Nombre = models.CharField(max_length=10)
    objects = models.Manager()
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
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdEstadoCuenta

    class Meta:
        verbose_name_plural = "Estados de cuenta"
        verbose_name = "Estado de cuenta"


DOC_CHOICES10 = (
    ('No certificada', _(u"No certificada")),
    ('Certificada', _(u"Certificada"))
)

DOC_CHOICES11 = (
    ('SI', _(u"SI")),
    ('NO', _(u"NO"))
)


class Medidores(models.Model):
    IdMedidor = models.CharField(primary_key=True, max_length=10, null=False)
    Marca = models.CharField(max_length=100, null=False)
    Modelo = models.CharField(max_length=100, null=False)
    Tipo = models.CharField(max_length=50, null=False)
    Designacion = models.CharField(max_length=100, null=False)
    clase = models.CharField(max_length=100, null=False)
    Diametronominal = models.CharField(max_length=100, null=False)
    AnoFabricacion = models.CharField(max_length=4, null=False)
    Estado = models.CharField(max_length=35, null=False, default='Sin asignar')
    Certificado = models.CharField(max_length=100, null=False, choices=DOC_CHOICES11)
    Fecha = models.DateTimeField(auto_now_add=True, null=True)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % (self.IdMedidor)

    class Meta:
        verbose_name_plural = "Listado de Medidores"
        verbose_name = "Medidor"


DOC_C = (
    ('Operativo', _(u"Operativo")),
    ('Retirado', _(u"Retirado"))
)

class Asignacion(models.Model):
    IdRegistro = models.AutoField(primary_key=True)
    IdMedidor = models.ForeignKey(Medidores, on_delete=models.CASCADE)
    IdVivienda = models.ForeignKey(Vivienda,on_delete=models.CASCADE)
    Fecha = models.DateTimeField(auto_now_add=True)
    Estado = models.CharField(max_length=40, null=False, choices=DOC_C, default='Operativo')
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdRegistro

    class Meta:
        verbose_name_plural = "Asignados"
        verbose_name = "Asignar"


class ValorMatricula(models.Model):
    IdValor = models.AutoField(primary_key=True)
    Valor = models.CharField(max_length=10, null=False)
    Fecha = models.DateTimeField(auto_now=True)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.Valor

    class Meta:
        verbose_name_plural = "listado de valor de matricula"
        verbose_name = "valor matricula"


DOC_CHOICES12 = (
    ('1', _(u"1")),
    ('2', _(u"2")),
    ('4', _(u"4")),
    ('5', _(u"5")),
    ('6', _(u"6")),
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
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdCobroM, self.Descripcion)

    class Meta:
        verbose_name_plural = "Cobro matriculas"
        verbose_name = "Cobro matricula"


DOC_CHOICES20 = (
    ('Gerencia', _(u"Gerencia")),
    ('Secretaria general', _(u"Secretaria general")),
    ('Control interno', _(u"Control interno")),
    ('Subgerencia tecnica', _(u"Subgerencia tecnica")),
    ('Subgerencia operaciones', _(u"Subgerencia operaciones")),
    ('Subgerencia comercial', _(u"Subgerencia comercial")),
    ('Subgerencia financiera y administrativa', _(u"Subgerencia financiera y administrativa")),
)

DOC_CHOICES21 = (
    ('Servicios publicos', _(u"Pago - servicios publicos")),
    ('Nomina', _(u"Pago - nomina")),
    ('Viaticos', _(u"Pago - viaticos")),
    ('Impuestos', _(u"Pago - impuestos")),
    ('Mantenimiento infrastructura', _(u"Pago - Mantenimiento de infraestructura")),
    ('Compra de materiales', _(u"Pago - Compra de materiales")),
    ('Compra de accesorios', _(u"Pago - Compra de accesorios")),
    ('Transporte', _(u"Pago - transporte")),
)

DOC_CHOICES16 = (
    ('Persona natural', _(u"Persona natural")),
    ('Personeria juridica', _(u"Personeria juridica")),
)


class Proveedor(models.Model):
    IdProvedor = models.CharField(max_length=30, primary_key=True, null=False)
    Nombrecompleto = models.CharField(max_length=100, null=False)
    Personeria = models.CharField(max_length=100, null=True, choices=DOC_CHOICES16)
    Direccion = models.CharField(max_length=100, null=False)
    telefono = models.CharField(max_length=100, null=False)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdProvedor, self.Nombrecompleto)

    class Meta:
        verbose_name_plural = "Proveedores"
        verbose_name = "Proveedor"

class SolicitudGastos(models.Model):
    IdSoGa = models.AutoField(primary_key=True)
    IdUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Descripcion = models.CharField(max_length=5000, null=False)
    TipoSolicitud = models.CharField(max_length=50, null=False, choices=DOC_CHOICES21)
    Valor = models.CharField(max_length=10, null=False)
    Estado = models.CharField(max_length=15, null=False, choices=DOC_CHOICES9)
    Fecha = models.DateTimeField(auto_now=True, null=False)
    AreaResponsable = models.CharField(max_length=100, null=False, choices=DOC_CHOICES20)
    NumeroFactura = models.CharField(max_length=10, null=False)
    IdProveedor= models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
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
    objects = models.Manager()
    def __str__(self):
        return "%s %s %s" % (self.IdPermiso, self.TipoPermiso, self.usuid)

    class Meta:
        verbose_name_plural = "Permisos"
        verbose_name = "Permiso"


DOC_CHOICES14 = (
    ('Peticion', _(u"Peticion")),
    ('Queja', _(u"Queja")),
    ('Reclamo', _(u"Reclamo")),
    ('Solicitud', _(u"Solicitud")),
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
    Nombre = models.CharField(max_length=100, null=True)
    FechaRadicado = models.DateTimeField(auto_now_add=True, null=False)
    Telefono = models.CharField(max_length=10, null=True)
    Correo = models.EmailField(max_length=60, null=True)
    Direccion = models.CharField(max_length=200, null=True)
    TipoSolicitud = models.CharField(max_length=50, null=True, choices=DOC_CHOICES14)
    Clasificacion = models.CharField(max_length=50, null=True, choices=DOC_CHOICES15)
    Descripcion = models.TextField(max_length=10000, null=True)
    usuid = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=40, null=False)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
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
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdRespuesta

    class Meta:
        verbose_name_plural = "Respuestas"
        verbose_name = "Respuestas"

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
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdCierre, self.Ciclo)

    class Meta:
        verbose_name_plural = "Lista de cierres mensuales"
        verbose_name = "Cierre mensual"

class AsignacionBloque(models.Model):
    IdBloque = models.AutoField(primary_key=True)
    Bloque = models.CharField(max_length=50, null=False)
    Matricula = models.CharField(max_length=150, null=False)
    Estado = models.CharField(max_length=150, null=False)
    Estadocuenta = models.CharField(max_length=150, null=True)
    Fecha = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdBloque

    class Meta:
        verbose_name_plural = "Bloques"
        verbose_name = "Bloque"



DOC_CHOICES17 = (
    ('Vigente', _(u"Vigente")),
    ('Pagado', _(u"Pagado")),
)


class Credito(models.Model):
    IdCredito = models.AutoField(primary_key=True)
    NombreCredito = models.CharField(max_length=40, null=False)
    IdProveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    ValorInicial = models.CharField(max_length=40, null=False)
    CantCuotas = models.CharField(max_length=3, null=False)
    ValorPendiente = models.CharField(max_length=10, null=False)
    CuotasPendiente = models.CharField(max_length=10, null=False)
    Fecha = models.DateTimeField(auto_now_add=True, null=False)
    Estado = models.CharField(max_length=10, null=False, choices=DOC_CHOICES17)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdCredito

    class Meta:
        verbose_name_plural = "Creditos"
        verbose_name = "Credito"

class Consumos(models.Model):
    IdRegistro = models.AutoField(primary_key=True)
    IdMedidor = models.ForeignKey(Medidores, on_delete=models.CASCADE)
    IdVivienda = models.ForeignKey(Vivienda,on_delete=models.CASCADE)
    Lecturaactual = models.IntegerField(null=False)
    Lecturaanterior = models.IntegerField(null=False)
    Consumo = models.IntegerField(null=False)
    promedio = models.CharField(max_length=20, null=False)
    observaciones = models.CharField(max_length=350, null=True)
    diasconsumo = models.CharField(max_length=10,null=False)
    ano = models.CharField(max_length=4, null=False)
    mes = models.CharField(max_length=20, null=False)
    Fecha = models.DateTimeField(auto_now_add=True)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdRegistro

    class Meta:
        verbose_name_plural = "Consumos"
        verbose_name = "Consumo"

class Conceptos(models.Model):
    IdRegistro = models.AutoField(primary_key=True)
    Tipo = models.CharField(max_length=350, null=True)
    Observacion = models.CharField(max_length=350, null=True)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=350, null=True)
    Fecha = models.DateTimeField(auto_now_add=True)
    Valor = models.IntegerField(null=True)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdRegistro

    class Meta:
        verbose_name_plural = "Conceptos de cobro"
        verbose_name = "Concepto de cobro"


class ConceptosFacturados(models.Model):
    IdRegistro = models.AutoField(primary_key=True)
    AporteFijo = models.IntegerField(null=True)
    Complementario = models.IntegerField(null=True)
    CuotaMatricula = models.IntegerField(null=True)
    Suspencion = models.IntegerField(null=True)
    Reconexion = models.IntegerField(null=True)
    Recargo = models.IntegerField(null=True)
    AcuerdoPago = models.IntegerField(null=True)
    SaldoAnterior = models.IntegerField(null=True)
    Subsidio = models.IntegerField(null=True)
    Fecha = models.DateTimeField(auto_now_add=True)
    Total = models.IntegerField(null=True)
    Estado = models.CharField(max_length=10, null=True)
    Periodo = models.CharField(max_length=10, null=True)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdRegistro

    class Meta:
        verbose_name_plural = "Conceptos de cobro"
        verbose_name = "Concepto de cobro"

class Novedades(models.Model):
    IdNovedad = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=5000, null=False)
    TipoNovedad = models.CharField(max_length=100, null=False)
    Fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=30, null=False)
    matricula = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdNovedad, self.TipoNovedad)

    class Meta:
        verbose_name_plural = "Novedades"
        verbose_name = "Novedad"

class OrdenesTrabajo(models.Model):
    IdOrden = models.AutoField(primary_key=True)
    Deuda = models.CharField(max_length=10, null=False)
    Estado = models.CharField(max_length=10, null=False)
    TipoNovedad = models.CharField(max_length=100, null=False)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    FechaEjecucion = models.DateTimeField(null=False)
    usuario = models.CharField(max_length=30, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdOrden, self.TipoNovedad)

    class Meta:
        verbose_name_plural = "Novedades"
        verbose_name = "Novedad"

class Facturas(models.Model):
    IdFactura = models.AutoField(primary_key=True)
    Estado = models.CharField(max_length=100, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE,null=True)
    periodofacturado = models.CharField(max_length=50, null=True)
    facturasvencidas = models.CharField(max_length=100, null=True)
    FechaLimite = models.DateTimeField(auto_now=True)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    IdCiclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    Total = models.CharField(max_length=100, null=False)

    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdFactura

    class Meta:
        verbose_name_plural = "Lista de facturas"
        verbose_name = "Generar factura"

class Pagos(models.Model):
    IdPago = models.AutoField(primary_key=True)
    FechaPago = models.DateTimeField(auto_now=True, null=False)
    IdFactura = models.ForeignKey(Facturas, on_delete=models.CASCADE)
    Ano = models.CharField(max_length=4, null=False)
    Descripcion = models.CharField(max_length=20, null=False)
    ValorPago = models.CharField(max_length=10, null=False)
    Efectivo = models.CharField(max_length=10, null=False)
    Devuelta = models.CharField(max_length=10, null=False)
    resta = models.CharField(max_length=10, null=True)
    IdUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.IdPago

    class Meta:
        verbose_name_plural = "Pagos"
        verbose_name = "Pago"

class FechasFacturacion(models.Model):
    IdRegistro = models.CharField(max_length=5, primary_key=True)
    Nombre = models.CharField(max_length=15)
    FechaFacturacion = models.DateTimeField(null=False)
    Ano = models.CharField(max_length=4)
    Periodo = models.CharField(max_length=20)
    objects = models.Manager()
    def __str__(self):
        return "%s" % self.Nombre

    class Meta:
        verbose_name_plural = "Lista de Ciclos"
        verbose_name = "Listado de ciclos"

class AcuerdosPago(models.Model):
    IdAcuerdo = models.AutoField(primary_key=True)
    Tipo = models.CharField(max_length=20, null=False)
    Descripcion = models.CharField(max_length=250, null=False)
    IdVivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    Estado = models.CharField(max_length=15, null=False)
    Valor = models.IntegerField(null=True)
    CantCuotas = models.CharField(max_length=10, null=False, choices=DOC_CHOICES12)
    CuotasPendientes = models.CharField(max_length=10, null=False)
    ValorPendiente = models.CharField(max_length=50, null=False)
    Cuota = models.CharField(max_length=50, null=False)
    FechaExpe = models.DateTimeField(auto_now_add=True)
    IdAcueducto = models.ForeignKey(Acueducto, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s %s" % (self.IdAcuerdo, self.Descripcion)

class FacturasConceptos(models.Model):
    IdRegistro = models.AutoField(primary_key=True)
    IdFactura = models.ForeignKey(Facturas, on_delete=models.CASCADE)
    IdConcepto = models.ForeignKey(ConceptosFacturados, on_delete=models.CASCADE)
    objects = models.Manager()
    def __str__(self):
        return "%s" % (self.IdRegistro)