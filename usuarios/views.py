# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from SAAL.models import Usuario, Tarifa, Credito, AsignacionBloque, Novedades
from SAAL.models import OrdenesSuspencion, OrdenesReconexion, Poblacion, Factura, Ciclo, EstadoCuenta
from SAAL.models import Vivienda, SolicitudGastos, Propietario, Medidores, Pqrs, RespuestasPqrs
from SAAL.models import CobroMatricula, Permisos, Pagos, Cierres, Acueducto, ValorMatricula
from SAAL.models import Proveedor,Asignacion, Consumos, Conceptos
from SAAL.forms import FormAgregarGasto, FormRegistroPqrs, RegistroUsuario, RegistroUsuario2, RegistroVivienda
from SAAL.forms import AcueductoAForm, PermisosForm, CobroMatriculaForm, CostoMForm, FormRespuestaPqrs,FormAsignarMedidor
from SAAL.forms import RegistroPropietario, TarifasForm, ModificaPropietario, FormRegistroCredito, FormRegistroProveedor
from SAAL.forms import CambioFormEstado, AcueductoForm, GastosForm, MedidoresForm, PoblacionForm, ModificaVivienda
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse
from openpyxl import Workbook
import openpyxl
import qrcode
from openpyxl.drawing.image import Image
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from usuarios.ConectorPython import *
from django.db.models import Sum

# Reemplaza estos valores con tus credenciales de Google Mail
username = 'sistemas.acueducto.caimalito@gmail.com'

#SECTORES
SECTOR1 = 'Pasonivel Viejo'
SECTOR2 = 'Pasonivel Destapada'
SECTOR3 = 'Caimalito Centro'
SECTOR4 = 'Barrio Nuevo'
SECTOR5 = '20 de julio'
SECTOR6 = 'Carbonera'
SECTOR7 = 'Hacienda'

# ESTADOS PRERIOS
ESTADOS1 = 'Operativo'
ESTADOS2 = 'Suspendido'
ESTADOS3 = 'Mantenimiento'
ESTADOS4 = 'Retirado'

#NOVEDADES
NOVEDAD1 = 'Cerrada'

# Tiempos de facturacion
DIASFACTURACION = 10
DIASPARASUSPENCION = 15
# permisos
CT = 'AC'
# TARIFA
TARIFA = 10000
# ------------
EF = 'Emitida'
EPC = 'Se registro propietario'
EPM = 'Se modifico propietario'
DESC = 'Null'
ECV = 'Se registro vivienda'
EMV = 'Se modifico vivienda'
# Tipo novedades
DES = 'Descuento'
ADI = 'Adicion'
# estados suspenciones
SA = 'Anulada'
SP = 'Pendiente'
SJ = 'Ejecutada'
TARIFASUSPENCION = 17000
# estados ciclos
EC = 'SIN PAGAR'
EC2 = 'PAGO'
EC3 = 'ANULADA'
# EstadosFacturas
FE = 'Emitida'
FV = 'Vencida'
FP = 'Paga'
FA = 'Anulada'
# Estadoscuentasdecobro
Estadocue = 'Mantenimiento'
# otros
REPORTESUSPEN = 'Suspedido'
# sectores
S1 = 'Pasonivel Viejo'
S2 = 'Pasonivel Destapada'
S3 = 'Caimalito Centro'
S4 = 'Barrio Nuevo'
S5 = '20 de julio'

# ESTADOS PRERIOS
E1 = 'Operativo'
E2 = 'Suspendido'
E3 = 'Retirado'
E4 = 'En construcion'

C1 = 'Ciclo 1'
C2 = 'Ciclo 2'
C3 = 'Ciclo 3'
C4 = 'Ciclo 4'

T1 = 'Residencial'
T2 = 'Comercial'
T3 = 'Inductrial'
DESCOBRO = 'Concepto matricula'
COBROCONSUMO = 'Cobro por consumo'
ESTCOBRO = 'Pendiente'
ESTCOBRO2 = 'Pago'
ESTADO1 = "Pendiente"
ESTADO2 = "Aprobada"
ESTADO3 = "Anulada"
ESTADOCERTI = "En proceso"
ESTADOPQR1 = "Pendiente"


class Inicio(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/inicio.html'
    form_class = AcueductoForm

    def get(self, request):
        try:
            version = open('static/serial/Version.txt', 'r')
            versionp = version.read()
            version2 = open('static/serial/NombreProyecto.txt', 'r')
            nombreproyecto = version2.read()
            version3 = open('static/serial/NombreProyectoL.txt', 'r')
            nombreproyectol = version3.read()

            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            tipousuario = datos.TipoUsuario
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)
            nombreacueducto = acueducto.Nombre
            novedades = Novedades.objects.all().order_by("-IdNovedad")[:3]
            # mensualidades:
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ano1 = fechaexp.year
            # Los argumentos serán: Año, Mes, Día, Hora, Minutos, Segundos, Milisegundos.
            new_date = datetime(ano1, ciclo, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano1, ciclo, 28, 23, 59, 59, 00000)
            pagos2 = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            pago0 = 0
            for i in pagos2:
                valor = i.ValorPago
                pago0 += int(valor)

            predios = Vivienda.objects.filter(EstadoServicio=ESTADOS1).count()
            recaudot = int(predios) * 10000

            porcentaje = pago0 / recaudot * 100
            # mensualidades:
            ciclo2 = fechaexp.month - 1
            ano2 = fechaexp.year
            # Los argumentos serán: Año, Mes, Día, Hora, Minutos, Segundos, Milisegundos.
            new_date3 = datetime(ano2, ciclo2, 1, 1, 00, 00, 00000)
            new_date4 = datetime(ano2, ciclo2, 28, 23, 59, 59, 00000)
            factuasemi = Factura.objects.filter(FechaExpe__gte=new_date3, FechaExpe__lte=new_date4).count()
            pagos3 = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).count()
            contador = pagos3 / factuasemi * 100

            if pagos3 ==0:
                promedio = 0
                promtarifa = 0

            else:
                promedio = pago0 / pagos3
                promtarifa = promedio / 10000 * 100

            viviendas = Vivienda.objects.filter(EstadoServicio=ESTADOS1) | Vivienda.objects.filter(EstadoServicio=ESTADOS3)| Vivienda.objects.filter(EstadoServicio=ESTADOS2)
            personas = 0
            for i in viviendas:
                valor = int(i.CantHabitantes)
                personas += valor

            suscriptoresactivos = Vivienda.objects.filter(EstadoServicio=ESTADOS3)| Vivienda.objects.filter(EstadoServicio=ESTADOS1) | Vivienda.objects.filter(EstadoServicio=ESTADOS2)
            suscriptores = 0
            for i in suscriptoresactivos:
                valor = 1
                suscriptores += valor

            # paso nivel
            pop = Vivienda.objects.filter(Direccion=SECTOR1, EstadoServicio=ESTADOS1).count()
            pma =Vivienda.objects.filter(Direccion=SECTOR1, EstadoServicio=ESTADOS3).count()
            psu = Vivienda.objects.filter(Direccion=SECTOR1, EstadoServicio=ESTADOS2).count()
            pdop = Vivienda.objects.filter(Direccion=SECTOR2, EstadoServicio=ESTADOS1).count()
            pdma = Vivienda.objects.filter(Direccion=SECTOR2, EstadoServicio=ESTADOS3).count()
            pdsu = Vivienda.objects.filter(Direccion=SECTOR2, EstadoServicio=ESTADOS2).count()
            pn = pop + pma + psu + pdop + pdma + pdsu

            #caimalito centro
            cop = Vivienda.objects.filter(Direccion=SECTOR3, EstadoServicio=ESTADOS1).count()
            cma =Vivienda.objects.filter(Direccion=SECTOR3, EstadoServicio=ESTADOS3).count()
            csu = Vivienda.objects.filter(Direccion=SECTOR3, EstadoServicio=ESTADOS2).count()
            cc = cop + cma + csu
            #Barrio nuevo
            bop = Vivienda.objects.filter(Direccion=SECTOR4, EstadoServicio=ESTADOS1).count()
            bma = Vivienda.objects.filter(Direccion=SECTOR4, EstadoServicio=ESTADOS3).count()
            bsu = Vivienda.objects.filter(Direccion=SECTOR4, EstadoServicio=ESTADOS2).count()
            bn = bop + bma + bsu

            #20 de julio
            vop = Vivienda.objects.filter(Direccion=SECTOR5, EstadoServicio=ESTADOS1).count()
            vma = Vivienda.objects.filter(Direccion=SECTOR5, EstadoServicio=ESTADOS3).count()
            vsu = Vivienda.objects.filter(Direccion=SECTOR5, EstadoServicio=ESTADOS2).count()
            vj = vop + vma + vsu

            #Hacienda
            hop = Vivienda.objects.filter(Direccion=SECTOR7, EstadoServicio=ESTADOS1).count()
            hma = Vivienda.objects.filter(Direccion=SECTOR7, EstadoServicio=ESTADOS3).count()
            hsu = Vivienda.objects.filter(Direccion=SECTOR7, EstadoServicio=ESTADOS2).count()
            ha = hop + hma + hsu

            # Hacienda
            caop = Vivienda.objects.filter(Direccion=SECTOR6, EstadoServicio=ESTADOS1).count()
            cama = Vivienda.objects.filter(Direccion=SECTOR6, EstadoServicio=ESTADOS3).count()
            casu = Vivienda.objects.filter(Direccion=SECTOR6, EstadoServicio=ESTADOS2).count()
            ca = caop + cama + casu

            contarasig = Asignacion.objects.filter(Estado='Operativo').count()
            vapo = Consumos.objects.all().aggregate(Consumo=Sum('Consumo'))
            suma8 = vapo['Consumo']

            return render(request,
                          self.template_name, {'tipousuario': tipousuario, 'nombreproyecto': nombreproyecto,
                                               'nombreproyectol': nombreproyectol, 'acueducto': nombreacueducto,
                                               'versionp': versionp,'personas':personas,
                                               'novedades': novedades, 'pagos': pago0,'suscriptores':suscriptores,
                                               'porcentaje': int(porcentaje), 'contador': int(contador),
                                               'facturaspagas': pagos3, 'promedio': int(promedio),
                                               'promtarifa': int(promtarifa),
                                               'pn':pn, 'vj':vj, 'cc':cc, 'bn':bn, 'ha':ha,'ca':ca, 'contarasig': contarasig, 'suma8': suma8})
        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ListaViviendas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listaviviendas.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)
            listaviviendas = Vivienda.objects.filter(IdAcueducto=acueducto.pk)
            tipousuario = Permisos.objects.filter(usuid=datos, TipoPermiso='ALP').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'viviendas': listaviviendas,
                                  'notificaciones': contadorpen,
                                  'listapqrs': listapqrs,
                                  'totalnoti': totalnoti
                              })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de '
                                                              'acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ListaPropietarios(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listapropietarios.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            listavivienda = Vivienda.objects.filter(IdAcueducto=dr.pk)
            usuarios = Propietario.objects.all()
            tipousuario = Permisos.objects.filter(usuid=datos, TipoPermiso='ALS').exists()
            if tipousuario is True:
                return render(request, self.template_name, {'usuarios': usuarios, 'viviendas': listavivienda,
                                                            'notificaciones': contadorpen, 'listapqrs': listapqrs,
                                                            'totalnoti': totalnoti})
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a '
                                                              'esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AgregarPropietario(LoginRequiredMixin, View):
    login_url = '/'
    form_class = RegistroPropietario
    template_name = 'usuarios/registropropietario.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            form = self.form_class()
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AIS').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'form': form,
                                  'notificaciones': contadorpen,
                                  'listapqrs': listapqrs,
                                  'totalnoti': totalnoti
                              })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a '
                                                              'esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            idpropietario = request.POST.get("IdPropietario")
            nombres = request.POST.get("Nombres")
            apellidos = request.POST.get("Apellidos")
            notelefono = request.POST.get("NoTelefono")
            email = request.POST.get("Email")
            idpoblacion = request.POST.get("IdPoblacion")
            poblacion = Poblacion.objects.get(IdPoblacion=idpoblacion)

            validarpro = Propietario.objects.filter(IdPropietario=idpropietario).exists()
            if validarpro is True:
                messages.add_message(request, messages.ERROR, 'El usuario ya existe')
                return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

            else:
                if int(idpropietario) <= 400000:
                    messages.add_message(request, messages.ERROR, 'El numero de identificacion del '
                                                                  'propietario no es valido')
                    return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

                else:
                    propietario = Propietario(IdPropietario=idpropietario, Nombres=nombres, Apellidos=apellidos,
                                              NoTelefono=notelefono, Email=email, IdPoblacion=poblacion)

                    if propietario is not None:
                        propietario.save()
                        messages.add_message(request, messages.INFO, 'el propietario se agrego correctamente')
                        return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

                    else:
                        messages.add_message(request, messages.ERROR, 'El propietario no se pudo agregar')
                        return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ModificarPropietario(LoginRequiredMixin, View):
    login_url = '/'
    form_class = ModificaPropietario
    template_name = 'usuarios/modificarpropietario.html'

    def get(self, request, idpropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=idpropietario)
            form = self.form_class(instance=datospropietario)
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACMT').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'form': form})
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de acceso a '
                                                              'esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idpropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=idpropietario)
            form = self.form_class(request.user, request.POST, instance=datospropietario)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'la informacion del propietario se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ModificarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    form_class = ModificaVivienda
    template_name = 'usuarios/modificarvivienda.html'

    def get(self, request, idvivienda):
        try:
            idvivienda = str(idvivienda)
            datosvivienda = Vivienda.objects.get(IdVivienda=idvivienda)
            form = self.form_class(instance=datosvivienda)
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACMP').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'form': form, 'matricula': idvivienda})

            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de '
                                                              'acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idvivienda):
        try:
            datosvivienda = Vivienda.objects.get(IdVivienda=idvivienda)
            form = self.form_class(request.user, request.POST, instance=datosvivienda)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'la informacion de la vivienda se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VisualizarPropietario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verpropietario.html'

    def get(self, request, idpropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=idpropietario)
            viviendas = Vivienda.objects.filter(IdPropietario=idpropietario)
            return render(request, self.template_name,
                          {
                              'viviendas': viviendas,
                              'IdPropietario': datospropietario.IdPropietario,
                              'Nombres': datospropietario.Nombres,
                              'Apellidos': datospropietario.Apellidos,
                              'NoTelefono': datospropietario.NoTelefono,
                              'Email': datospropietario.Email,
                              'IdPoblacion': datospropietario.IdPoblacion
                          })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VisualizarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/vervivienda.html'

    def get(self, request, idvivienda):
        try:
            vivienda = Vivienda.objects.get(IdVivienda=idvivienda)
            viviendainfo = Vivienda.objects.filter(IdVivienda=idvivienda)
            estados = EstadoCuenta.objects.filter(IdVivienda=idvivienda)
            cobromatricula = CobroMatricula.objects.filter(IdVivienda=idvivienda, Estado=ESTCOBRO)
            pagos = Pagos.objects.filter(IdVivienda=idvivienda)
            contpagos = Pagos.objects.filter(IdVivienda=idvivienda).count()
            filtropagos = Pagos.objects.filter(IdVivienda=idvivienda).order_by("-IdPago")[:1]
            fecha = datetime.today()
            verificarestado = EstadoCuenta.objects.get(IdVivienda=idvivienda)
            idestado = verificarestado.IdEstadoCuenta
            resultado = verificarestado.Valor
            facturas = Factura.objects.filter(IdEstadoCuenta=idestado).order_by("-IdFactura")
            nofacturas = Factura.objects.filter(IdEstadoCuenta=idestado).count()
            facturasemi = Factura.objects.filter(IdEstadoCuenta=idestado).order_by("-IdFactura")[:1]
            vafacemi = Factura.objects.filter(IdEstadoCuenta=idestado, Estado=FE).exists()
            matriculas = CobroMatricula.objects.filter(IdVivienda=idvivienda)
            matriculas2 = CobroMatricula.objects.filter(IdVivienda=idvivienda).exists()
            reconexion = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestado).order_by("-IdOrden")
            suspenciones = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestado).order_by("-IdOrden")
            contsus = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestado).count()
            contre = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestado).count()
            filtrosuspenciones = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestado, Estado='Pendiente').exists()
            validarcobro = CobroMatricula.objects.filter(IdVivienda=idvivienda, Estado=ESTCOBRO)
            validarretiro = Novedades.objects.filter(matricula=idvivienda, TipoNovedad='Retiro').exists()
            novretiro = Novedades.objects.filter(matricula=idvivienda, TipoNovedad='Retiro')
            reparaciones = 0
            matri = 0
            for i in validarcobro:
                valor = i.Cuota
                matri += int(valor)

            lista = []
            for k in facturas:
                idenfactura = k.IdFactura
                pago = Pagos.objects.filter(IdFactura=idenfactura).exists()
                if pago is True:
                    lista.append(idenfactura)

            pagado = 0
            for g in pagos:
                valor = int(g.ValorPago)
                pagado += valor

            seis = 0
            useis = None
            cinco = 0
            ucinco = None
            cuatro = 0
            ucuatro = None
            tres = 0
            utres = None
            dos = 0
            udos = None
            uno = 0
            uuno = None
            contarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).count()
            if contarconsumo == 1:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:3]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes

            elif contarconsumo == 2:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:3]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes
                segundoobjeto = consultarconsumo[1]
                cinco = segundoobjeto.Consumo
                ucinco = segundoobjeto.mes

            elif contarconsumo == 3:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:3]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes
                segundoobjeto = consultarconsumo[1]
                cinco = segundoobjeto.Consumo
                ucinco = segundoobjeto.mes
                tercerobjeto = consultarconsumo[2]
                cuatro = tercerobjeto.Consumo
                ucuatro = tercerobjeto.mes

            elif contarconsumo == 4:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:4]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes
                segundoobjeto = consultarconsumo[1]
                cinco = segundoobjeto.Consumo
                ucinco = segundoobjeto.mes
                tercerobjeto = consultarconsumo[2]
                cuatro = tercerobjeto.Consumo
                ucuatro = tercerobjeto.mes
                cuartoobjeto = consultarconsumo[3]
                tres = cuartoobjeto.Consumo
                utres = cuartoobjeto.mes

            elif contarconsumo == 5:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:5]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes
                segundoobjeto = consultarconsumo[1]
                cinco = segundoobjeto.Consumo
                ucinco = segundoobjeto.mes
                tercerobjeto = consultarconsumo[2]
                cuatro = tercerobjeto.Consumo
                ucuatro = tercerobjeto.mes
                cuartoobjeto = consultarconsumo[3]
                tres = cuartoobjeto.Consumo
                utres = cuartoobjeto.mes
                quintoobjeto = consultarconsumo[4]
                dos = quintoobjeto.Consumo
                udos = quintoobjeto.mes

            elif contarconsumo >= 6:
                consultarconsumo = Consumos.objects.filter(IdVivienda=idvivienda).order_by("-IdRegistro")[:6]
                primerobjeto = consultarconsumo[0]
                seis = primerobjeto.Consumo
                useis = primerobjeto.mes
                segundoobjeto = consultarconsumo[1]
                cinco = segundoobjeto.Consumo
                ucinco = segundoobjeto.mes
                tercerobjeto = consultarconsumo[2]
                cuatro = tercerobjeto.Consumo
                ucuatro = tercerobjeto.mes
                cuartoobjeto = consultarconsumo[3]
                tres = cuartoobjeto.Consumo
                utres = cuartoobjeto.mes
                quintoobjeto = consultarconsumo[4]
                dos = quintoobjeto.Consumo
                udos = quintoobjeto.mes
                sextoobjeto = consultarconsumo[5]
                uno = sextoobjeto.Consumo
                uuno = segundoobjeto.mes

            asignado = Asignacion.objects.filter(IdVivienda=idvivienda, Estado='Operativo').exists()

            return render(request, self.template_name, {
                'nore': contre, 'nosus': contsus, 'pagado': pagado, 'nofac': nofacturas, 'asignado': asignado,
                'lista': lista, 'facturas': facturas, 'cobromatricula': cobromatricula, 'suspenciones': suspenciones,
                'reconexion': reconexion, 'facturasemi': facturasemi, 'matriculas': matriculas,
                'direccion': vivienda.Direccion, 'casa': vivienda.NumeroCasa, 'piso': vivienda.Piso,
                'matricula': vivienda.IdVivienda, 'tipo': vivienda.TipoInstalacion,
                'estrato': vivienda.Estrato, 'tipop': vivienda.InfoInstalacion, 'estado': vivienda.EstadoServicio,
                'propietario': vivienda.IdPropietario, 'fichacatastral': vivienda.FichaCastral,
                'estados': estados, 'pagos': pagos, 'fecha': fecha, 'ultimopago': filtropagos,
                'vafacemi': vafacemi, 'viviendainfo': viviendainfo,
                'aportes': resultado, 'cobromatricula1': matri,
                'repaciones': reparaciones,
                'filtro': filtrosuspenciones, 'contpagos': contpagos, 'vmatri': matriculas2,'novedadr': validarretiro,
                'novretiro':novretiro,'seis': int(seis),'useis': useis,'cinco': cinco,'ucinco':ucinco, 'cuatro':cuatro,'ucuatro':ucuatro,
                'tres': tres, 'utres': utres, 'dos': dos, 'udos':udos, 'uno': uno, 'uuno':uuno
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AgregarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    form_class = RegistroVivienda
    vizualizarv = VisualizarVivienda
    template_name = 'usuarios/registrovivienda.html'

    def get(self, request, idbloque):
        try:
            form = self.form_class()
            matricula = AsignacionBloque.objects.get(IdBloque=idbloque)
            asignada = matricula.Matricula
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AIP').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'form': form,
                                  'asignada': asignada
                              })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta '
                                                              'seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idbloque):
        try:
            matricula = AsignacionBloque.objects.get(IdBloque=idbloque)
            asignada = matricula.Matricula
            idvivienda = asignada
            direccion = request.POST.get("Direccion")
            numerocasa = request.POST.get("NumeroCasa")
            piso = request.POST.get("Piso")
            ciclo = request.POST.get("Ciclo")
            tipoinstalacion = request.POST.get("TipoInstalacion")
            estrato = request.POST.get("Estrato")
            estadoservicio = request.POST.get("EstadoServicio")
            idpropietario = request.POST.get("IdPropietario")
            matricula = request.POST.get("MatriculaAnt")
            infoinstalacion = request.POST.get("InfoInstalacion")
            profacometida = request.POST.get("ProfAcometida")
            canthabitantes = request.POST.get("CantHabitantes")
            fichacatastral = request.POST.get("FichaCastral")
            diametro = request.POST.get("Diametro")
            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)
            propietario = Propietario.objects.get(IdPropietario=idpropietario)
            validarvi = Vivienda.objects.filter(IdVivienda=idvivienda).exists()
            if validarvi is True:
                messages.add_message(request, messages.ERROR, 'la Vivienda ya existe')
                return HttpResponseRedirect(reverse('usuarios:matriculas'))

            else:
                vivienda = Vivienda(IdVivienda=idvivienda, Direccion=direccion, NumeroCasa=numerocasa, Piso=piso,
                                    Ciclo=ciclo, TipoInstalacion=tipoinstalacion, Estrato=estrato,
                                    EstadoServicio=estadoservicio, IdPropietario=propietario, MatriculaAnt=matricula,
                                    InfoInstalacion=infoinstalacion, ProfAcometida=profacometida,
                                    CantHabitantes=canthabitantes, IdAcueducto=acueducto,
                                    FichaCastral=fichacatastral, Diametro=diametro, usuid=datos.usuid)
                vivienda.save()
                estadocuenta = EstadoCuenta(Valor=0, IdVivienda=vivienda, Estado='Operativo', Descripcion=COBROCONSUMO)
                estadocuenta.save()
                matriculas = AsignacionBloque.objects.get(IdBloque=idbloque)
                matriculas.Estado = 'Asignada'
                matriculas.Estadocuenta = estadocuenta.IdEstadoCuenta
                matriculas.save()
                ver = self.vizualizarv()
                messages.add_message(request, messages.INFO, 'La informacion del predio se agrego correctamente')
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Estadoscuenta(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/estadosdecuenta.html'

    def get(self, request):
        try:
            # operaciones de conteo
            operativos = EstadoCuenta.objects.filter(Estado='Operativo').count()
            mantenimiento = EstadoCuenta.objects.filter(Estado='Mantenimiento').count()
            retirados = EstadoCuenta.objects.filter(Estado='Retirado').count()
            suspendidos = EstadoCuenta.objects.filter(Estado='Suspendido').count()

            # operaciones de suma
            operativo = EstadoCuenta.objects.filter(Estado='Operativo')
            contoperativos = 0
            for i in operativo:
                valor = i.Valor
                contoperativos += valor

            mantenimientos = EstadoCuenta.objects.filter(Estado='Mantenimiento')
            contmantenimiento = 0
            for i in mantenimientos:
                valor = i.Valor
                contmantenimiento += valor

            suspendido = EstadoCuenta.objects.filter(Estado='Suspendido')
            contsuspendido = 0
            for i in suspendido:
                valor = i.Valor
                contsuspendido += valor

            retirado = EstadoCuenta.objects.filter(Estado='Retirado')
            contretirado = 0
            for i in retirado:
                valor = i.Valor
                contretirado += valor

            usuario = Usuario.objects.get(usuid=request.user.pk)
            totalcuentas = EstadoCuenta.objects.all().count()

            totalfac = Factura.objects.all().count()
            facemi2 = Factura.objects.filter(Estado=FE).count()
            facven = Factura.objects.filter(Estado=FV).count()
            facpg = Factura.objects.filter(Estado=FP).count()
            facanu = Factura.objects.filter(Estado=FA).count()

            facturasvalor = Factura.objects.filter(Estado='Emitida').aggregate(Total=Sum('Total'))
            total = facturasvalor['Total']

            vapo = EstadoCuenta.objects.filter(Estado='Operativo').aggregate(Valor=Sum('Valor'))
            sumatotal = vapo['Valor']
            vasu = EstadoCuenta.objects.filter(Estado='Suspendido').aggregate(Valor=Sum('Valor'))
            sumatotal2 = vasu['Valor']
            vama = EstadoCuenta.objects.filter(Estado='Mantenimiento').aggregate(Valor=Sum('Valor'))
            sumatotal3 = vama['Valor']
            vare = EstadoCuenta.objects.filter(Estado='Retirado').aggregate(Valor=Sum('Valor'))
            sumatotal4 = vare['Valor']

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ACC').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'operativos': int(operativos), 'mantenimiento': int(mantenimiento),
                                  'retirados': int(retirados), 'suspendidos': int(suspendidos),
                                  'contoperativos': contoperativos, 'contretirados': contretirado,
                                  'contmantenimiento': contmantenimiento, 'contsuspendidos': contsuspendido,
                                  'totalcuentascobro': totalcuentas, 'total': total, 'vapo': sumatotal,
                                  'vasu':sumatotal2, 'vama':sumatotal3, 'vare':sumatotal4,
                                  'totalvalores': contoperativos + contmantenimiento + contretirado + contsuspendido,
                                  'totalfac':totalfac,  'facven':facven, 'facanu': facanu, 'facpg':facpg, 'facemi': facemi2
                              })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class GenerarCobros(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/generarcobros.html'

    def get(self, request):
        try:
            estadoscuenta = EstadoCuenta.objects.filter(Estado='Operativo')|EstadoCuenta.objects.filter(Estado='Mantenimiento')|EstadoCuenta.objects.filter(Estado='Suspendido')
            cont = 0
            for i in estadoscuenta:
                cont += 1

            return render(request, self.template_name, {
                'cont': cont})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            # Fechas
            ye = datetime.now()
            ano = ye.year
            # consultafacturasconestados"emitida"
            facturas = Factura.objects.filter(Estado=FE).count()
            # Consultadetarifaeusuario
            usuarios = Usuario.objects.get(usuid=request.user.pk)
            acueducto = usuarios.IdAcueducto
            acueductos = Acueducto.objects.get(IdAcueducto=acueducto)
            idtarifa = acueductos.IdTarifa
            tarifa1 = Tarifa.objects.get(IdTarifa=idtarifa)
            tarifaoperativos = tarifa1.Valor
            tarifamantenimiento = tarifa1.Mantenimiento
            estados = EstadoCuenta.objects.all()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ACC').exists()
            if tipousuario is True:
                if facturas >= 1:
                    messages.add_message(request, messages.ERROR,
                                         'No se puede generar cobros, hay facturacion con estado *emitida*', ano)
                    return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

                else:
                    cont = 0
                    for k in estados:
                        if k.Estado == 'Operativo':
                            estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=k.pk)
                            estadoscu.Valor += int(tarifaoperativos)
                            estadoscu.save()
                            cont += 1
                        elif k.Estado == 'Mantenimiento':
                            estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=k.pk)
                            estadoscu.Valor += int(tarifamantenimiento)
                            estadoscu.save()
                            cont += 1
                        else:
                            pass
                    messages.add_message(request, messages.SUCCESS, 'Se generaron ', cont, ' cobros')
                    return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class ReportesCiclo(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            sector = request.GET.get("ciclo")
            centro = str(sector)
            viviendas = Vivienda.objects.filter(Ciclo=centro)
            wb = Workbook()
            ws = wb.active
            ws['A1'] = "Reporte de predios"
            ws.merge_cells('A1:B1')
            ws['A2'] = 'Matricula'
            ws['B2'] = 'Dirección'
            ws['C2'] = 'NumeroCasa'
            ws['D2'] = 'Piso'
            ws['E2'] = 'Ciclo'
            ws['F2'] = 'TipoInstalación'
            ws['G2'] = 'Estrato'
            ws['H2'] = 'EstadoServicio'
            ws['I2'] = 'Propietario'
            ws['J2'] = 'Acueducto'
            ws['K2'] = 'Usuario'
            ws['L2'] = 'MatriculaAnt'
            ws['M2'] = 'InfoInstalación'
            ws['N2'] = 'ProfAcometida'
            ws['O2'] = 'CantHabitantes'

            cont = 3

            for vivienda in viviendas:
                ws.cell(row=cont, column=1).value = vivienda.IdVivienda
                ws.cell(row=cont, column=2).value = vivienda.Direccion
                ws.cell(row=cont, column=3).value = vivienda.NumeroCasa
                ws.cell(row=cont, column=4).value = vivienda.Piso
                ws.cell(row=cont, column=5).value = vivienda.Ciclo
                ws.cell(row=cont, column=6).value = vivienda.TipoInstalacion
                ws.cell(row=cont, column=7).value = vivienda.Estrato
                ws.cell(row=cont, column=8).value = vivienda.EstadoServicio
                ws.cell(row=cont, column=9).value = str(vivienda.IdPropietario)
                ws.cell(row=cont, column=10).value = str(vivienda.IdAcueducto)
                ws.cell(row=cont, column=11).value = str(vivienda.usuid)
                ws.cell(row=cont, column=12).value = vivienda.MatriculaAnt
                ws.cell(row=cont, column=13).value = vivienda.InfoInstalacion
                ws.cell(row=cont, column=14).value = vivienda.ProfAcometida
                ws.cell(row=cont, column=15).value = vivienda.CantHabitantes

                cont += 1

            archivo_predios = "ReportePorCiclo.xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Busquedas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/busquedas.html'
    propietario = VisualizarPropietario
    predio = VisualizarVivienda

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AB').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'notificaciones': contadorpen,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti
                })

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            tipo = request.POST.get("tipo")
            identificacion = request.POST.get("identificacion")

            if tipo == "Cedula de ciudadania" and identificacion is not None:
                titular = Propietario.objects.filter(IdPropietario=identificacion).exists()
                if titular is True:
                    idpropietario = identificacion
                    ver = self.propietario()
                    ejercutar = ver.get(request, idpropietario)
                    return ejercutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del titular no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            elif tipo == "Numero de matricula" and identificacion is not None:
                predio = Vivienda.objects.filter(IdVivienda=identificacion).exists()
                if predio is True:
                    idvivienda = identificacion
                    ver = self.predio()
                    ejecutar = ver.get(request, idvivienda)
                    return ejecutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del predio no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            elif tipo == "Referencia" and identificacion is not None:
                estadocuenta = EstadoCuenta.objects.filter(IdEstadoCuenta=identificacion).exists()
                if estadocuenta is True:
                    estadocuentas = EstadoCuenta.objects.get(IdEstadoCuenta=identificacion)
                    idvivienda = estadocuentas.IdVivienda.pk
                    ver = self.predio()
                    ejecutar = ver.get(request, idvivienda)
                    return ejecutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del predio no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            else:
                messages.add_message(request, messages.WARNING, 'Informacion incompleta')
                return HttpResponseRedirect(reverse('usuarios:busquedas'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ReporteCiclo(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            tipo = request.GET.get("tipo")
            ano = request.GET.get("Ano")

            if tipo and ano == 'Todo':
                estadocuenta = EstadoCuenta.objects.all()
                wb = Workbook()
                ws = wb.active
                ws['A1'] = "Reporte de ciclos"
                ws.merge_cells('A1:B1')
                ws['A2'] = 'Id Estado'
                ws['B2'] = 'Valor'
                ws['C2'] = 'Predio'
                ws['D2'] = 'Periodo'
                ws['E2'] = 'Estado'
                ws['F2'] = 'Año'
                cont = 3

                for estado in estadocuenta:
                    ws.cell(row=cont, column=1).value = estado.IdEstadoCuenta
                    ws.cell(row=cont, column=2).value = estado.Valor
                    ws.cell(row=cont, column=3).value = str(estado.IdVivienda)
                    ws.cell(row=cont, column=4).value = str(estado.IdCiclo)
                    ws.cell(row=cont, column=5).value = estado.Estado
                    ws.cell(row=cont, column=6).value = estado.ano

                    cont += 1

                archivo_propi = "ReporteCiclos.xlsx"
                response = HttpResponse(content_type="application/ms-excel")
                content = "attachment; filename = {0}".format(archivo_propi)
                response['Content-Disposition'] = content
                wb.save(response)
                return response

            else:
                estadocuenta = EstadoCuenta.objects.filter(Estado=tipo, ano=ano)
                wb = Workbook()
                ws = wb.active
                ws['A1'] = "Reporte de ciclos"
                ws.merge_cells('A1:B1')
                ws['A2'] = 'Id Estado'
                ws['B2'] = 'Valor'
                ws['C2'] = 'Predio'
                ws['D2'] = 'Periodo'
                ws['E2'] = 'Estado'
                ws['F2'] = 'Año'
                cont = 3

                for estado in estadocuenta:
                    ws.cell(row=cont, column=1).value = estado.IdEstadoCuenta
                    ws.cell(row=cont, column=2).value = estado.Valor
                    ws.cell(row=cont, column=3).value = str(estado.IdVivienda)
                    ws.cell(row=cont, column=4).value = str(estado.IdCiclo)
                    ws.cell(row=cont, column=5).value = estado.Estado
                    ws.cell(row=cont, column=6).value = estado.ano

                    cont += 1

                archivo_propi = "ReporteCiclos.xlsx"
                response = HttpResponse(content_type="application/ms-excel")
                content = "attachment; filename = {0}".format(archivo_propi)
                response['Content-Disposition'] = content
                wb.save(response)
                return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ControlPresupuestal(LoginRequiredMixin, View):
    login_url = '/'
    form_class = GastosForm
    template_name = 'usuarios/gastos.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            solicitudesgastos = SolicitudGastos.objects.filter(Estado=ESTADO1)
            form = self.form_class()
            contador = SolicitudGastos.objects.all().count()
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            contadorapro = SolicitudGastos.objects.filter(Estado=ESTADO2).count()
            contadoranu = SolicitudGastos.objects.filter(Estado=ESTADO3).count()
            aprobado = SolicitudGastos.objects.filter(Estado=ESTADO2)

            credito = Credito.objects.filter(Estado='Vigente')
            pagos = Pagos.objects.all()
            viviendasope = Vivienda.objects.filter(EstadoServicio=E1).count()
            nit = usuario.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=nit)
            tarifa = acueducto.IdTarifa.Valor

            totalpormes = int(int(viviendasope) * int(tarifa))
            pago = 0
            for i in pagos:
                valor = i.ValorPago
                pago += int(valor)

            suma2 = 0
            for i in aprobado:
                valor = int(i.Valor)
                suma2 += valor

            suma8 = 0
            for i in credito:
                valor = int(i.ValorPendiente)
                suma8 += valor

            totalingresos = pago
            gastos = int(suma2)
            presupuesto = totalingresos - gastos
            # mensualidades:
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ano1 = fechaexp.year
            # Los argumentos serán: Año, Mes, Día, Hora, Minutos, Segundos, Milisegundos.
            new_date = datetime(ano1, ciclo, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano1, ciclo, 30, 23, 59, 59, 00000)
            pagos2 = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            gastosaprobados = SolicitudGastos.objects.filter(Fecha__gte=new_date, Fecha__lte=new_date2,
                                                             Estado=ESTADO2).all()

            gasto4 = 0
            for i in gastosaprobados:
                valor = int(i.Valor)
                gasto4 += valor

            pago0 = 0
            for i in pagos2:
                valor = i.ValorPago
                pago0 += int(valor)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ACP').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'porcentaje': int(pago0 / totalpormes * 100),
                    'form': form,
                    'solicitudesgastos': solicitudesgastos,
                    'contador': contador,
                    'contadorp': contadorpen,
                    'contadora': contadorapro,
                    'contadoranu': contadoranu,
                    'gastos': gastos,
                    'pago': int(totalingresos),
                    'presupuesto': presupuesto,
                    'ingresomensual': pago0,
                    'gastosmensuales': gasto4,
                    'credito': suma8,

                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class GenerarGasto(LoginRequiredMixin, View):
    login_url = '/'
    form_class = FormAgregarGasto
    template_name = 'usuarios/generargasto.html'

    def get(self, request):
        try:
            form = self.form_class()
            return render(request, self.template_name, {
                'form': form,
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            area = request.POST.get("AreaResponsable")
            tiposolicitud = request.POST.get("TipoSolicitud")
            valor = request.POST.get("Valor")
            numerofactura = request.POST.get("NumeroFactura")
            descripcion = request.POST.get("Descripcion")
            proveedor = request.POST.get("IdProveedor")
            consulp = Proveedor.objects.get(IdProvedor=proveedor)
            usuario = Usuario.objects.get(usuid=request.user.pk)

            if area and numerofactura and tiposolicitud and valor and descripcion is not None:
                solicitud = SolicitudGastos(IdUsuario=usuario, Descripcion=descripcion,
                                            TipoSolicitud=tiposolicitud, Valor=valor,
                                            Estado=ESTADO1, AreaResponsable=area, NumeroFactura=numerofactura,
                                            IdProveedor=consulp)
                solicitud.save()
                messages.add_message(request, messages.INFO, 'la solicitud se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.ERROR, 'Informacion incompleta')
                return HttpResponseRedirect(reverse('usuarios:generargasto'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class BuscarSolicitud(LoginRequiredMixin, View):
    login_url = '/'
    form_class = GastosForm
    template_name = 'usuarios/modificarestado.html'

    def get(self, request, IdSoGa):
        try:
            solicitud = SolicitudGastos.objects.get(IdSoGa=IdSoGa)
            lsg = SolicitudGastos.objects.filter(IdSoGa=IdSoGa)
            form = self.form_class(instance=solicitud)
            return render(request, self.template_name,
                          {
                              'lsg': lsg,
                              'form': form,
                              'estado': solicitud.Estado,
                              'IdSoGa': solicitud.IdSoGa
                          })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdSoGa):
        try:
            solicitud = SolicitudGastos.objects.get(IdSoGa=IdSoGa)
            form = self.form_class(request.POST, instance=solicitud)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'El estado de la orden de modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'No se puedo modificar el estado de la orden, verifique la informacion')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ListasGastos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listasgastos.html'

    def get(self, request):
        try:
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            solicitudesgastos = SolicitudGastos.objects.all().order_by("-IdSoGa")
            cierre = Cierres.objects.all()
            contador = SolicitudGastos.objects.all().count()
            contcierre = Cierres.objects.all().count()

            return render(request, self.template_name, {
                'solicitudesgastos': solicitudesgastos,
                'contador': contador,
                'cierres': cierre,
                'contcierre': contcierre,
                'notificaciones': contadorpen,
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroMedidor(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registromedidor.html'
    form_class = MedidoresForm

    def get(self, request):
        try:

            form = self.form_class()
            return render(request, self.template_name, {
                'form': form
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        form = self.form_class(request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'El medidor se asigno correctamente')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

            else:
                messages.add_message(request, messages.ERROR, 'El predio ya tiene medidor asignado')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AsignarMedidor(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/asignacionmedidor.html'
    form_class = FormAsignarMedidor

    def get(self, request, IdMedidor):
        try:
            consulta1 = Medidores.objects.get(IdMedidor=IdMedidor)
            form = self.form_class(instance=consulta1)
            return render(request, self.template_name, {
                'form': form
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdMedidor):
        try:
            idmedidor = IdMedidor
            idvivienda = request.POST.get("IdVivienda")
            estado = request.POST.get("Estado")
            consultarpredio = Asignacion.objects.filter(IdVivienda=idvivienda, Estado='Operativo').exists()

            if consultarpredio is False:
                vivienda = Vivienda.objects.get(IdVivienda=idvivienda)
                medidor = Medidores.objects.get(IdMedidor=idmedidor)
                medidor.Estado ='Asignado'
                medidor.save()
                asignacion = Asignacion(IdMedidor=medidor, IdVivienda=vivienda, Estado='Operativo')
                asignacion.save()
                messages.add_message(request, messages.INFO, 'El medidor se asigno correctamente')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

            else:
                messages.add_message(request, messages.ERROR, 'El predio ya tiene un medidor asignado y operativo')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class Perfil(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/perfil.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            nit = usuario.IdAcueducto
            permiso = 1
            mispermisos = Permisos.objects.filter(usuid=usuario)
            acueducto = Acueducto.objects.filter(IdAcueducto=nit)
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            hoy = datetime.now()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if permiso == 1:
                return render(request, self.template_name,
                              {'mispermisos': mispermisos,
                               'foto': usuario.fotoUsuario,
                               'celular': usuario.celular,
                               'departamento': usuario.Departamento,
                               'cargo': usuario.TipoUsuario,
                               'fechac': usuario.FechaCreacion,
                               'ultimo': hoy,
                               'acueducto': acueducto,
                               'notificaciones': contadorpen,
                               'listapqrs': listapqrs,
                               'totalnoti': totalnoti,
                               'tipousuario': tipousuario
                               })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene permisos de acceso')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroPoblacion(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registropoblacion.html'
    form_class = PoblacionForm

    def get(self, request):
        try:
            form = self.form_class()
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'form': form, 'notificaciones': contadorpen, 'listapqrs': listapqrs, 'totalnoti': totalnoti})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            idpoblacion = request.POST.get("IdPoblacion")
            descripcion = request.POST.get("Descripcion")
            verificacion = Poblacion.objects.filter(IdPoblacion=idpoblacion).exists()

            if verificacion is False:
                poblacion = Poblacion(IdPoblacion=idpoblacion, Descripcion=descripcion)
                poblacion.save()
                messages.add_message(request, messages.INFO, 'El tipo de poblacion se creo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'Ese tipo de poblacion ya existe')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroCostoM(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registrocostomatricula.html'
    form_class = CostoMForm

    def get(self, request):
        try:
            form = self.form_class()

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'form': form
                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            valor = request.POST.get("Valor")

            if valor is not None:
                poblacion = ValorMatricula(Valor=valor)
                poblacion.save()
                messages.add_message(request, messages.INFO, 'El valor se agrego correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'Debe ingresar un valor al campo')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroTarifa(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registrotarifa.html'
    form_class = TarifasForm

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            form = self.form_class()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'form': form
                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        form = self.form_class(request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'La informacion se guardo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'Ya existe una tarifa con esa informacion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ImprimirTiquet(LoginRequiredMixin):
    login_url = '/'

    def get(self, request):
        try:
            impresoras = ConectorV3.obtenerImpresoras()
            print("Las impresoras son:")
            print(impresoras)

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroPqr(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registropqrs.html'
    form_class = FormRegistroPqrs

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACFA').exists()
            if tipousuario is False:
                form = self.form_class()
                return render(request, self.template_name, {'form': form})
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            nombre = request.POST.get("Nombre")
            celular = request.POST.get("Telefono")
            correo = request.POST.get("Correo")
            direccion = request.POST.get("Direccion")
            tiposolicitud = request.POST.get("TipoSolicitud")
            clasificacion = request.POST.get("Clasificacion")
            descripcion = request.POST.get("Descripcion")
            usuario = Usuario.objects.get(usuid=request.user.pk)
            pqr = Pqrs(Nombre=nombre, Telefono=celular, Descripcion=descripcion, Correo=correo, Direccion=direccion,
                       TipoSolicitud=tiposolicitud, Clasificacion=clasificacion, Estado=ESTADOPQR1, usuid=usuario)
            pqr.save()
            idpqr = pqr.IdPqrs
            messages.add_message(request, messages.INFO,
                                 'La pqrs se ' + str(tiposolicitud) + ' registro correctamente, RADICADO No: ' + str(
                                     idpqr))
            return HttpResponseRedirect(reverse('usuarios:listapqrs'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ListaPqrs(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listapqrs.html'

    def get(self, request):
        try:
            listado = Pqrs.objects.all().order_by("-IdPqrs")
            total = Pqrs.objects.all().count()
            lista = Pqrs.objects.filter(Estado='Pendiente')
            contcerrada = Pqrs.objects.filter(Estado='Cerrada').count()
            contpendiente = Pqrs.objects.filter(Estado='Pendiente').count()
            # tipo de solicitud
            contpeticion = Pqrs.objects.filter(TipoSolicitud='Peticion').count()
            contquejas = Pqrs.objects.filter(TipoSolicitud='Queja').count()
            contsolicitud = Pqrs.objects.filter(TipoSolicitud='Solicitud').count()
            contreclamo = Pqrs.objects.filter(TipoSolicitud='Reclamo').count()

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='APQRS').exists()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            if tipousuario is True:
                return render(request, self.template_name, {
                    'lista': lista,
                    'total': total,
                    'contp': contpeticion,
                    'contq': contquejas,
                    'conts': contsolicitud,
                    'contr': contreclamo,
                    'contpen': contpendiente,
                    'contcerrada': contcerrada,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti,
                    'listado': listado

                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VerPqr(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verpqr.html'

    def get(self, request, idpqr):
        try:
            pqr = Pqrs.objects.filter(IdPqrs=idpqr)
            respuesta = RespuestasPqrs.objects.filter(IdPqrs=idpqr)
            idsolicitud = Pqrs.objects.get(IdPqrs=idpqr)

            return render(request, self.template_name, {
                'pqr': pqr,
                'respuestas': respuesta,
                'idsolicitud': idsolicitud
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RespuestaPqrs(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/respuestapqr.html'
    form_class = FormRespuestaPqrs

    def get(self, request, idsolicitud):
        try:
            prq = Pqrs.objects.get(IdPqrs=idsolicitud)
            form = self.form_class()

            return render(request, self.template_name, {
                'form': form,
                'idsolicitud': idsolicitud
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idsolicitud):
        try:
            id = 1
            soporte = request.FILES.get("Soporte")
            descripcion = request.POST.get("Descripcion")
            pqrs = Pqrs.objects.get(IdPqrs=idsolicitud)
            if id>=1:
                cpqrs = Pqrs.objects.get(IdPqrs=idsolicitud)
                cpqrs.Estado = NOVEDAD1
                cpqrs.save()
                respuesta = RespuestasPqrs(IdPqrs=pqrs, Descripcion=descripcion, Soporte=soporte)
                respuesta.save()
                messages.add_message(request, messages.INFO, 'La respuesta se agrego correctamente')
                return HttpResponseRedirect(reverse('usuarios:listapqrs'))

            else:
                messages.add_message(request, messages.WARNING, 'No se pudo agregar la respuesta')
                return HttpResponseRedirect(reverse('usuarios:listapqrs'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class CambioEstadoFacturas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/anularfs.html'

    def get(self, request):
        try:
            facturasemi = Factura.objects.filter(Estado=FE).count()
            orsuspencion = OrdenesSuspencion.objects.filter(Estado='Pendiente').count()
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AMFV').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'facturasemi': facturasemi,
                                  'orsus': orsuspencion,
                              })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            facturas = Factura.objects.filter(Estado=FE)
            ordensus = OrdenesSuspencion.objects.filter(Estado="Pendiente")
            verificacion = Factura.objects.filter(Estado=FE).count()
            if verificacion >= 1:
                for factura in facturas:
                    cambio = Factura.objects.get(IdFactura=factura.pk)
                    cambio.Estado = FV
                    cambio.save()

                for orden in ordensus:
                    cambio = OrdenesSuspencion.objects.get(IdOrden=orden.pk)
                    cambio.Estado = "Anulada"
                    cambio.UsuarioEjecuta = "Sistema"
                    cambio.save()

                messages.add_message(request, messages.INFO, 'Se cambio el estado de las facturas vigentes a vencidas y se anularon las ordenes de suspencion vigentes')
                return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))
            else:
                messages.add_message(request, messages.ERROR, 'No hay facturacion vigente')
                return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class GeneradorFacturas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/generadorfacturas.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)

            facturasemi = Factura.objects.all().count()
            facturasemitidas = Factura.objects.filter(Estado=FE)
            facturasemitidas2 = Factura.objects.filter(Estado=FE).count()
            facturasven = Factura.objects.filter(Estado=FV).count()
            facturaspg = Factura.objects.filter(Estado=FP).count()
            facturasanu = Factura.objects.filter(Estado=FA).count()
            facturas = Factura.objects.filter(Estado='Emitida').order_by("-IdFactura")
            suma = 0
            for i in facturasemitidas:
                valor = int(i.Total)
                suma += valor

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AGF').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {'totalemitidas': facturasemitidas2,
                               'facturasven': facturasven,
                               'facturasemi': facturasemi,
                               'facturaspg': facturaspg,
                               'facturasanu': facturasanu,
                               'suma': suma,
                               'facturas': facturas
                               })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            # consulta de existencias
            usuario = Usuario.objects.get(usuid=request.user.pk)
            facturas = Factura.objects.filter(Estado=FE).exists()
            # fechas
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ciclos = Ciclo.objects.get(IdCiclo=ciclo)
            mes = ciclos.Nombre
            fechalimite = fechaexp + timedelta(days=DIASFACTURACION)
            estadosoperativos = EstadoCuenta.objects.filter(Estado='Operativo') | EstadoCuenta.objects.filter(
                Estado='Mantenimiento') | EstadoCuenta.objects.filter(Estado='Suspendido')
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='GF').exists()
            if tipousuario is True:
                if facturas is False:
                    contador = 0
                    for i in estadosoperativos:
                        # consultaestadocuenta
                        estadoc = EstadoCuenta.objects.get(IdEstadoCuenta=i.pk)
                        consumo = estadoc.Valor
                        idestadocuenta = estadoc.IdEstadoCuenta

                        # consulta cuota matricula
                        idvivienda = estadoc.IdVivienda
                        verificacion = CobroMatricula.objects.filter(IdVivienda=idvivienda, Estado='Pendiente')
                        cuotamatricula = 0
                        for e in verificacion:
                            valor = e.Cuota
                            cuotamatricula += int(valor)

                        # consulta facturas vencidas
                        consumo1 = estadoc.Valor - 1000
                        vencidas = -1
                        for f in range(1, consumo1, TARIFA):
                            if f != consumo:
                                vencidas += 1

                        # total valor factura
                        totalfactura = int(cuotamatricula) + int(consumo)
                        factura = Factura(Matricula=idvivienda, Estado='Emitida', IdEstadoCuenta=estadoc,
                                          periodofacturado=mes, aporteporconsumo=consumo,
                                          cuotamatricula=cuotamatricula, reconexion=0,
                                          suspencion=0, TotalConsumo=consumo,
                                          facturasvencidas=vencidas, FechaExpe=fechaexp, FechaLimite=fechalimite,
                                          IdCiclo=ciclos, Total=totalfactura)
                        factura.save()
                        contador += 1

                    messages.add_message(request, messages.INFO, 'Se generaron ' + str(contador) + ' facturas ')
                    return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

                else:
                    messages.add_message(request, messages.ERROR, 'No se puede generar facturas verifique nuevamente')
                    return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Suspenciones(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/generadorsuspenciones.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            cantanuladas = OrdenesSuspencion.objects.filter(Estado=SA).count()
            cantejecutadas = OrdenesSuspencion.objects.filter(Estado=SJ).count()
            cantpendientes = OrdenesSuspencion.objects.filter(Estado=SP).count()
            ordenessuspenciones = OrdenesSuspencion.objects.filter(Estado=SP)
            ordenesreconexion = OrdenesReconexion.objects.filter(Estado=SP)
            contreeje = OrdenesReconexion.objects.filter(Estado=SJ).count()
            contrepen = OrdenesReconexion.objects.filter(Estado=SP).count()
            totales = OrdenesSuspencion.objects.all().count()

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ASR').exists()

            if tipousuario is True:
                return render(request, self.template_name, {
                    'anuladas': cantanuladas,
                    'pendientes': cantpendientes,
                    'ejecutadas': cantejecutadas,
                    'ordsus': ordenessuspenciones,
                    'ordrec': ordenesreconexion,
                    'rependientes': contrepen,
                    'reejecutadas': contreeje,
                    'total': totales

                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            s = (datetime.today())
            fecha = s + timedelta(days=DIASPARASUSPENCION)
            estadoscuenta = EstadoCuenta.objects.filter(Estado='Operativo') | EstadoCuenta.objects.filter(
                Estado='Mantenimiento')

            for estado in estadoscuenta:
                idestado = estado.IdEstadoCuenta
                estadocu = EstadoCuenta.objects.get(IdEstadoCuenta=idestado)
                valor = estadocu.Valor
                verificacion = OrdenesSuspencion.objects.filter(IdEstadoCuenta=estadocu, Estado=SP).exists()
                if verificacion is False:
                    if valor >= TARIFASUSPENCION:
                        orden = OrdenesSuspencion(Deuda=valor, FechaEjecucion=fecha, Generado='auto', Estado=SP,
                                                  UsuarioEjecuta='Font', IdEstadoCuenta=estadocu)
                        orden.save()

            messages.add_message(request, messages.INFO, 'Se generaron las ordenes de suspencion correspondientes')
            return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Reconexiones(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/generadorreconexiones.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            total = OrdenesReconexion.objects.all().count()
            ordenesreconexion = OrdenesReconexion.objects.filter(Estado=SP)
            contreeje = OrdenesReconexion.objects.filter(Estado=SJ).count()
            contrepen = OrdenesReconexion.objects.filter(Estado=SP).count()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ASR').exists()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            if tipousuario is True:
                return render(request, self.template_name, {
                    'ordrec': ordenesreconexion,
                    'rependientes': contrepen,
                    'reejecutadas': contreeje,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti,
                    'total': total

                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ListasOrdenes(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listasordenes.html'

    def get(self, request):
        try:
            ordenessuspenciones = OrdenesSuspencion.objects.all()
            ordenesreconexion = OrdenesReconexion.objects.all()
            return render(request, self.template_name,
                          {'ordsus': ordenessuspenciones,
                           'ordrec': ordenesreconexion})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VerOrdenSuspencion(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verordensuspencion.html'

    def get(self, request, IdOrden):
        try:
            ordenessuspencion = OrdenesSuspencion.objects.get(IdOrden=IdOrden)
            ots = OrdenesSuspencion.objects.filter(IdOrden=IdOrden)
            idorden = ordenessuspencion.IdOrden
            estado = ordenessuspencion.Estado

            return render(request, self.template_name,
                          {'idorden': idorden,
                           'estado': estado,
                           'ots': ots,
                           })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdOrden):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            usu = str(usuario)
            idorden = IdOrden
            idacueducto = usuario.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            idtarifa = acueducto.IdTarifa
            tarifa = Tarifa.objects.get(IdTarifa=idtarifa)
            valorsuspencion = tarifa.TarifaSuspencion
            orden = OrdenesSuspencion.objects.filter(IdOrden=IdOrden).exists()
            otra = OrdenesSuspencion.objects.get(IdOrden=IdOrden)
            idestadocuenta = otra.IdEstadoCuenta
            descripcion = 'Suspención'
            estado = ESTADO1
            s = (datetime.today())
            if orden is True:
                ordensuspencion = OrdenesSuspencion.objects.get(IdOrden=IdOrden)
                ordensuspencion.Estado = SJ
                ordensuspencion.FechaEjecucion = s
                ordensuspencion.UsuarioEjecuta = usu
                ordensuspencion.save()
                estadocuent = ordensuspencion.IdEstadoCuenta
                estadoscuenta = EstadoCuenta.objects.get(IdEstadoCuenta=estadocuent.pk)
                estadoscuenta.Estado = E2
                estadoscuenta.save()
                idvivienda = estadoscuenta.IdVivienda
                vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
                vivienda.EstadoServicio = E2
                vivienda.save()
                concepto = Conceptos(Tipo=descripcion, Observacion='OTS: '+idorden, Estado='Sin facturar',
                                     Valor=valorsuspencion, IdVivienda=idvivienda.pk)
                concepto.save()
                messages.add_message(request, messages.INFO, 'La orden se cerro correctamente')
                return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AnularFactura(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/anularfactura.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AF').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'notificaciones': contadorpen,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti
                })
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            numerofactura = request.POST.get("factura", "")
            factura = Factura.objects.filter(IdFactura=numerofactura).exists()
            if factura is True:
                fac = Factura.objects.get(IdFactura=numerofactura)
                fac.Estado = FA
                fac.save()
                messages.add_message(request, messages.INFO, 'La factura se anulo correctamente')
                return HttpResponseRedirect(reverse('usuarios:anularfactura'))

            else:
                messages.add_message(request, messages.WARNING, 'El numero de factura ingresado no existe')
                return HttpResponseRedirect(reverse('usuarios:anularfactura'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class DescargarFactura(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, IdFactura):
        try:
            # datos factura
            factura = Factura.objects.get(IdFactura=IdFactura)
            noaporte = factura.IdFactura
            estado = factura.Estado
            idestadocuenta = factura.IdEstadoCuenta
            periodofacturado = factura.periodofacturado
            aporteporconsumo = factura.aporteporconsumo
            cuotamatricula = factura.cuotamatricula
            reconexion = factura.reconexion
            suspencion = factura.suspencion
            facturasvencidas = factura.facturasvencidas
            FechaExpe = factura.FechaExpe
            FechaLimite = factura.FechaLimite
            Total = factura.Total
            # datos estado cuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=idestadocuenta.pk)
            matricula = estadocuenta.IdVivienda
            # identificador de vivienda
            vivienda = Vivienda.objects.get(IdVivienda=matricula.pk)
            idmatricula = vivienda.IdVivienda
            idtitular = vivienda.IdPropietario
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            piso = vivienda.Piso
            estrato = vivienda.Estrato
            tipoinstalacion = vivienda.TipoInstalacion
            tipodepredio = vivienda.InfoInstalacion
            estadoservicio = vivienda.EstadoServicio
            ciclo = vivienda.Ciclo
            diametro = vivienda.Diametro
            cantpredios = vivienda.CantPredios
            # identificador de propietario
            titular = Propietario.objects.get(IdPropietario=idtitular.pk)
            nombretitular = titular.Nombres
            apellidotitular = titular.Apellidos
            nombrecompleto = nombretitular + ' ' + apellidotitular
            # codigoqr
            qr = qrcode.QRCode(
                version=4,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=0,
            )
            qr.add_data(noaporte)
            qr.make(fit=True)
            imga = qr.make_image(fill_color="black", back_color="white")
            imga.save('static/ModeloFactura/output.png')
            # libro excel
            condicion=0
            if condicion == 0:
                qr = qrcode.QRCode(
                    version=6,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=4,
                    border=0,
                )
                qr.add_data(noaporte)
                qr.make(fit=True)
                imga = qr.make_image(fill_color="black", back_color="white")
                imga.save('static/ModeloFactura/output.png')
                wb = openpyxl.load_workbook('static/ModeloFactura/002-0-230723.xlsx')
                ws = wb.active
                img = openpyxl.drawing.image.Image('static/ModeloFactura/output.png')
                ws.add_image(img, 'B16')
                if int(facturasvencidas) >= 1:
                    imagen = openpyxl.drawing.image.Image('static/ModeloFactura/corte1.png')
                    ws.add_image(imagen, 'AV26')
                else:
                    pass
                # factura matricula estado
                ws['A11'] = noaporte
                ws['O12'] = idmatricula
                ws['A14'] = estado
                # suscriptor
                ws['Y12'] = nombrecompleto
                ws['O6'] = sector + ' Cs ' + casa + ' Ps ' + piso
                ws['AN9'] = diametro
                ws['AG6'] = estrato
                ws['AK6'] = tipoinstalacion
                ws['AG9'] = tipodepredio
                ws['AH4'] = estadoservicio
                # Periodo facturado
                ws['A26'] = periodofacturado
                # ultimo pago
                consultarpago = Pagos.objects.filter(IdVivienda=matricula).exists()
                if consultarpago is True:
                    filtropagos = Pagos.objects.filter(IdVivienda=matricula).order_by("-IdPago")[:1]
                    consultarp = Pagos.objects.get(IdPago=filtropagos)
                    ws['Z17'] = consultarp.IdPago
                    ws['AE17'] = consultarp.FechaPago
                    ws['AL17'] = int(consultarp.ValorPago)
                else:
                    mensaje = "No Registra"
                    ws['Z17'] = mensaje
                    ws['AE17'] = mensaje
                    ws['AL17'] = mensaje

                # Periodo facturado
                if int(aporteporconsumo) > 0:
                    ws['AR19'] = 'Aportes - < 20M3'
                    ws['BJ19'] = facturasvencidas
                    ws['BM19'] = int(aporteporconsumo)

                if int(suspencion) > 0:
                    ws['AR21'] = 'Aporte por suspensión'
                    ws['BM21'] = suspencion

                if int(reconexion) > 0:
                    ws['AR22'] = 'Orden de reconexón'
                    ws['BM22'] = reconexion

                if int(cuotamatricula) > 0:
                    cobromatri = CobroMatricula.objects.get(IdVivienda=matricula)
                    saldo = cobromatri.ValorPendiente
                    cuotasp = cobromatri.CuotasPendientes
                    ws['AR23'] = 'Derecho de conexión'
                    ws['BF23'] = int(saldo)
                    ws['BJ23'] = cuotasp
                    ws['BM23'] = int(cuotamatricula)

                # total concepto de acueducto
                ws['BM26'] = int(Total)
                # facturas vencidas
                ws['O16'] = facturasvencidas

                # fechas de procedimiento
                ws['A31'] = FechaExpe
                ws['A33'] = FechaLimite

                if int(facturasvencidas) >= 1:
                    fechalimite = FechaLimite + timedelta(days=8)
                    ws['A33'] = 'Inmediato'
                    ws['A35'] = fechalimite
                else:
                    ws['A33'] = FechaLimite

                # total a pagar condional 0
                if int(Total) <= 0:
                    ws['A39'] = 0
                else:
                    ws['A39'] = int(Total)

                ws.title = IdFactura
                archivo_predios = str(IdFactura) + ".xlsx"
                response = HttpResponse(content_type="application/ms-excel")
                content = "attachment; filename = {0}".format(archivo_predios)
                response['Content-Disposition'] = content
                wb.save(response)
                return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VerOrdenReconexion(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verordenreconexion.html'

    def get(self, request, IdOrden):
        try:
            ordenesreconexicion = OrdenesReconexion.objects.get(IdOrden=IdOrden)
            otr = OrdenesReconexion.objects.filter(IdOrden=IdOrden)
            idorden = ordenesreconexicion.IdOrden
            estado = ordenesreconexicion.Estado

            return render(request, self.template_name,
                          {'idorden': idorden,
                           'estado': estado,
                           'otr': otr
                           })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdOrden):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            usu = str(usuario)
            idorden = IdOrden
            idacueducto = usuario.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            idtarifa = acueducto.IdTarifa
            tarifa = Tarifa.objects.get(IdTarifa=idtarifa)
            valorreconexion = tarifa.TarifaReconexion
            estado = ESTADO1
            descripcion = 'Reconexion'
            otra = OrdenesReconexion.objects.get(IdOrden=IdOrden)
            idestadocuenta = otra.IdEstadoCuenta
            orden = OrdenesReconexion.objects.filter(IdOrden=IdOrden).exists()
            s = (datetime.today())
            fecha = s
            if orden is True:
                ordensuspencion = OrdenesReconexion.objects.get(IdOrden=IdOrden)
                ordensuspencion.Estado = SJ
                ordensuspencion.FechaEjecucion = fecha
                ordensuspencion.UsuarioEjecuta = usu
                ordensuspencion.save()
                estadocuent = ordensuspencion.IdEstadoCuenta
                estadoscuenta = EstadoCuenta.objects.get(IdEstadoCuenta=estadocuent.pk)
                estadoscuenta.Estado = E1
                estadoscuenta.save()
                idvivienda = estadoscuenta.IdVivienda
                vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
                vivienda.EstadoServicio = E1
                vivienda.save()
                concepto = Conceptos(Tipo=descripcion, Observacion='OTS: ' + idorden, Estado='Sin facturar',
                                     Valor=valorreconexion, IdVivienda=idvivienda.pk)
                concepto.save()
                messages.add_message(request, messages.INFO,
                                     'La orden se cerro correctamente y el predio '
                                     'cambio de estado suspendido a operativo')
                return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class GeneradorFacturasIndividual(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/facturaindividual.html'

    def get(self, request, IdVivienda):
        try:
            estadoscuenta = EstadoCuenta.objects.filter(IdVivienda=IdVivienda)
            matricula = IdVivienda
            verificacion = CobroMatricula.objects.filter(IdVivienda=matricula, Estado=ESTCOBRO)
            return render(request, self.template_name,
                          {
                              'estadocuenta': estadoscuenta,
                              'matricula': matricula,
                              'matriculas': verificacion
                          })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ciclos = Ciclo.objects.get(IdCiclo=ciclo)
            fechalimite = fechaexp + timedelta(days=DIASFACTURACION)
            estadoc = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
            total = estadoc.Valor
            facturas = Factura.objects.filter(IdEstadoCuenta=estadoc, Estado=EF).count()
            if facturas >= 1:
                messages.add_message(request, messages.WARNING, 'Ya existe una factura pendiente de pago')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                verificacion = CobroMatricula.objects.get(IdVivienda=IdVivienda)
                if verificacion.Estado == ESTCOBRO:
                    otrocosto = verificacion.Cuota
                    final = int(total) + int(otrocosto)
                    factura = Factura(Estado=EF, FechaExpe=fechaexp, FechaLimite=fechalimite, Total=final,
                                      IdCiclo=ciclos,
                                      IdEstadoCuenta=estadoc, TotalConsumo=total, OtrosCobros=otrocosto)
                    factura.save()
                    messages.add_message(request, messages.INFO, 'La factura se creo correctamente')
                    return HttpResponseRedirect(reverse('usuarios:inicio'))

                else:
                    factura = Factura(Estado=EF, FechaExpe=fechaexp, FechaLimite=fechalimite,
                                      Total=total, IdCiclo=ciclos, IdEstadoCuenta=estadoc, TotalConsumo=total,
                                      OtrosCobros=0)
                    factura.save()
                    messages.add_message(request, messages.INFO, 'La factura se creo correctamente')
                    return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class DescargaMasivaFacturas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listamasivafacturas.html'

    def get(self, request):
        try:
            total = Factura.objects.filter(Estado='Emitida').count()
            facturas = Factura.objects.filter(Estado=EF).order_by('IdFactura')
            return render(request, self.template_name, {
                'facturas': facturas,
                'total': total,
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ReportePdfPagos(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        pagos = Pagos.objects.all()
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de pagos"
        ws['A1'] = 'Referencia de pago'
        ws['B1'] = 'Numero de factura'
        ws['C1'] = 'Año'
        ws['D1'] = 'Valor pagado'
        ws['E1'] = 'Efectivo'
        ws['F1'] = 'Cambio'
        ws['G1'] = 'Usuario recaudo'
        ws['H1'] = 'Matricula'
        ws['I1'] = 'Fecha de pago'
        sfecha = (datetime.today())
        cont = 2

        for pago in pagos:
            ws.cell(row=cont, column=1).value = pago.IdPago
            ws.cell(row=cont, column=2).value = str(pago.IdFactura)
            ws.cell(row=cont, column=3).value = pago.Ano
            ws.cell(row=cont, column=4).value = pago.ValorPago
            ws.cell(row=cont, column=5).value = pago.Efectivo
            ws.cell(row=cont, column=6).value = pago.Devuelta
            ws.cell(row=cont, column=7).value = str(pago.IdUsuario)
            ws.cell(row=cont, column=8).value = str(pago.IdVivienda)
            ws.cell(row=cont, column=9).value = str(pago.FechaPago)

            cont += 1

        archivo_propi = "ReportePagos" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_propi)
        response['Content-Disposition'] = content
        wb.save(response)
        return response


class ReporteCompleto(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        viviendas = Vivienda.objects.all()
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de predios"
        ws['A1'] = 'Matricula'
        ws['B1'] = 'Dirección'
        ws['C1'] = 'NumeroCasa'
        ws['D1'] = 'Piso'
        ws['E1'] = 'Ciclo'
        ws['F1'] = 'TipoInstalación'
        ws['G1'] = 'Estrato'
        ws['H1'] = 'EstadoServicio'
        ws['I1'] = 'Propietario'
        ws['J1'] = 'Acueducto'
        ws['K1'] = 'Usuario'
        ws['L1'] = 'MatriculaAnt'
        ws['M1'] = 'InfoInstalación'
        ws['N1'] = 'ProfAcometida'
        ws['O1'] = 'CantHabitantes'
        ws['P1'] = 'Numero de cedula'
        ws['Q1'] = 'Nombres'
        ws['R1'] = 'Apellidos'
        ws['S1'] = 'Telefono'
        ws['T1'] = 'Email'
        ws['U1'] = 'Tipo de poblacion'
        ws['V1'] = 'Referencia'
        ws['W1'] = 'Valor'
        ws['X1'] = 'Estado'
        ws['Y1'] = 'FechaActualizacion'
        ws['Z1'] = 'Ficha catastral'

        cont = 2

        for vivienda in viviendas:
            idpropietario = vivienda.IdPropietario
            ws.cell(row=cont, column=1).value = vivienda.IdVivienda
            ws.cell(row=cont, column=2).value = vivienda.Direccion
            ws.cell(row=cont, column=3).value = vivienda.NumeroCasa
            ws.cell(row=cont, column=4).value = vivienda.Piso
            ws.cell(row=cont, column=5).value = vivienda.Ciclo
            ws.cell(row=cont, column=6).value = vivienda.TipoInstalacion
            ws.cell(row=cont, column=7).value = vivienda.Estrato
            ws.cell(row=cont, column=8).value = vivienda.EstadoServicio
            ws.cell(row=cont, column=9).value = str(vivienda.IdPropietario)
            ws.cell(row=cont, column=10).value = str(vivienda.IdAcueducto)
            ws.cell(row=cont, column=11).value = str(vivienda.usuid)
            ws.cell(row=cont, column=12).value = vivienda.MatriculaAnt
            ws.cell(row=cont, column=13).value = vivienda.InfoInstalacion
            ws.cell(row=cont, column=14).value = vivienda.ProfAcometida
            ws.cell(row=cont, column=15).value = vivienda.CantHabitantes
            propietario = Propietario.objects.get(IdPropietario=idpropietario.pk)
            ws.cell(row=cont, column=16).value = propietario.IdPropietario
            ws.cell(row=cont, column=17).value = propietario.Nombres
            ws.cell(row=cont, column=18).value = propietario.Apellidos
            ws.cell(row=cont, column=19).value = propietario.NoTelefono
            ws.cell(row=cont, column=20).value = propietario.Email
            ws.cell(row=cont, column=21).value = str(propietario.IdPoblacion)
            estadocuenta = EstadoCuenta.objects.get(IdVivienda=vivienda)
            ws.cell(row=cont, column=22).value = str(estadocuenta.IdEstadoCuenta)
            ws.cell(row=cont, column=23).value = estadocuenta.Valor
            ws.cell(row=cont, column=24).value = estadocuenta.Estado
            ws.cell(row=cont, column=25).value = estadocuenta.FechaActualizacion
            ws.cell(row=cont, column=26).value = vivienda.FichaCastral

            cont += 1

        archivo_predios = "ReporteCompleto" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response


class ReporteSuspenciones(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, *args, **kwargs):
        pagos = OrdenesSuspencion.objects.filter(Estado=SP)
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        ws['A1'] = 'Id Orden'
        ws['B1'] = 'Deuda'
        ws['C1'] = 'Fecha expedicion'
        ws['D1'] = 'Fecha ejecucion'
        ws['E1'] = 'Generado'
        ws['F1'] = 'Estado'
        ws['G1'] = 'Usuario encargado'
        ws['H1'] = 'Referencia'
        ws['I1'] = 'Matricula'
        ws['J1'] = 'Sector'
        ws['K1'] = 'Casa'
        ws['L1'] = 'Piso'
        ws['M1'] = 'Ciclo'
        ws['N1'] = 'Tipo Instalacion'
        ws['O1'] = 'Estrato'
        ws['P1'] = 'Estado servicio'
        ws['Q1'] = 'Titular'
        ws['R1'] = 'Info instalacion'
        ws['S1'] = 'Profundidad acometida'
        ws['T1'] = 'Cant habitantes'
        cont = 2
        for suspencion in pagos:
            ws.cell(row=cont, column=1).value = suspencion.IdOrden
            ws.cell(row=cont, column=2).value = suspencion.Deuda
            ws.cell(row=cont, column=3).value = suspencion.FechaExpe
            ws.cell(row=cont, column=4).value = suspencion.FechaEjecucion
            ws.cell(row=cont, column=5).value = suspencion.Generado
            ws.cell(row=cont, column=6).value = suspencion.Estado
            ws.cell(row=cont, column=7).value = suspencion.UsuarioEjecuta
            ws.cell(row=cont, column=8).value = str(suspencion.IdEstadoCuenta)
            idestadocuenta = suspencion.IdEstadoCuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=idestadocuenta.pk)
            idvivienda = estadocuenta.IdVivienda
            vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
            ws.cell(row=cont, column=9).value = vivienda.IdVivienda
            ws.cell(row=cont, column=10).value = vivienda.Direccion
            ws.cell(row=cont, column=11).value = vivienda.NumeroCasa
            ws.cell(row=cont, column=12).value = vivienda.Piso
            ws.cell(row=cont, column=13).value = vivienda.Ciclo
            ws.cell(row=cont, column=14).value = vivienda.TipoInstalacion
            ws.cell(row=cont, column=15).value = vivienda.Estrato
            ws.cell(row=cont, column=16).value = vivienda.EstadoServicio
            ws.cell(row=cont, column=17).value = str(vivienda.IdPropietario)
            ws.cell(row=cont, column=18).value = vivienda.InfoInstalacion
            ws.cell(row=cont, column=19).value = vivienda.ProfAcometida
            ws.cell(row=cont, column=20).value = vivienda.CantHabitantes
            cont += 1

        archivo_predios = "Reporte ordenes suspencion" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response


class ReporteReconexion(LoginRequiredMixin, View):
    login_url = '/'

    def get(self):
        pagos = OrdenesReconexion.objects.filter(Estado=SP)
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        ws['A1'] = 'Id Orden'
        ws['B1'] = 'Deuda'
        ws['C1'] = 'Fecha expedicion'
        ws['D1'] = 'Fecha ejecucion'
        ws['E1'] = 'Generado'
        ws['F1'] = 'Estado'
        ws['G1'] = 'Usuario encargado'
        ws['H1'] = 'Referencia'
        ws['I1'] = 'Matricula'
        ws['J1'] = 'Sector'
        ws['K1'] = 'Casa'
        ws['L1'] = 'Piso'
        ws['M1'] = 'Ciclo'
        ws['N1'] = 'Tipo Instalacion'
        ws['O1'] = 'Estrato'
        ws['P1'] = 'Estado servicio'
        ws['Q1'] = 'Titular'
        ws['R1'] = 'Info instalacion'
        ws['S1'] = 'Profundidad acometida'
        ws['T1'] = 'Cant habitantes'
        cont = 2
        for suspencion in pagos:
            ws.cell(row=cont, column=1).value = suspencion.IdOrden
            ws.cell(row=cont, column=2).value = suspencion.Deuda
            ws.cell(row=cont, column=3).value = suspencion.FechaExpe
            ws.cell(row=cont, column=4).value = suspencion.FechaEjecucion
            ws.cell(row=cont, column=5).value = suspencion.Generado
            ws.cell(row=cont, column=6).value = suspencion.Estado
            ws.cell(row=cont, column=7).value = suspencion.UsuarioEjecuta
            ws.cell(row=cont, column=8).value = str(suspencion.IdEstadoCuenta)
            idestadocuenta = suspencion.IdEstadoCuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=idestadocuenta.pk)
            idvivienda = estadocuenta.IdVivienda
            vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
            ws.cell(row=cont, column=9).value = vivienda.IdVivienda
            ws.cell(row=cont, column=10).value = vivienda.Direccion
            ws.cell(row=cont, column=11).value = vivienda.NumeroCasa
            ws.cell(row=cont, column=12).value = vivienda.Piso
            ws.cell(row=cont, column=13).value = vivienda.Ciclo
            ws.cell(row=cont, column=14).value = vivienda.TipoInstalacion
            ws.cell(row=cont, column=15).value = vivienda.Estrato
            ws.cell(row=cont, column=16).value = vivienda.EstadoServicio
            ws.cell(row=cont, column=17).value = str(vivienda.IdPropietario)
            ws.cell(row=cont, column=18).value = vivienda.InfoInstalacion
            ws.cell(row=cont, column=19).value = vivienda.ProfAcometida
            ws.cell(row=cont, column=20).value = vivienda.CantHabitantes
            cont += 1

        archivo_predios = "Reporte ordenes reconexion" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response


class PagarMatricula(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/pagarmatricula.html'
    vervivienda = VisualizarVivienda

    def get(self, request, IdVivienda):
        try:
            matricula = CobroMatricula.objects.filter(IdVivienda=IdVivienda, Estado=ESTCOBRO)

            return render(request, self.template_name, {
                'matriculas': matricula
            })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            nuevascuotas = request.POST.get("pagomatricula")

            validacionmatricula = CobroMatricula.objects.get(IdVivienda=IdVivienda)
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idvivienda = vivienda.IdVivienda
            cantcuotas = validacionmatricula.CuotasPendientes
            valorpendiente = validacionmatricula.ValorPendiente
            resultado = int(valorpendiente) / int(nuevascuotas)

            if cantcuotas != nuevascuotas:
                validacionmatricula = CobroMatricula.objects.get(IdVivienda=IdVivienda)
                validacionmatricula.CuotasPendientes = nuevascuotas
                validacionmatricula.Cuota = int(resultado)
                validacionmatricula.save()
                messages.add_message(request, messages.INFO, 'El valor se refinancio correctamente')
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

            else:
                messages.add_message(request, messages.INFO,
                                     'Las cuotas deben ser diferentes a las asignadad inicialmente')
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class EnvioCorreo(LoginRequiredMixin):
    login_url = '/'

    def get(self, asunto, informacion, tipousuario):
        now = datetime.now()
        context = {'asunto': asunto, 'fecha': now, 'informacion': informacion, 'usuario': tipousuario}
        template = get_template('usuarios/correo.html')
        content = template.render(context)

        email = EmailMultiAlternatives(
            asunto,
            'Sistemas acueducto caimalito',
            settings.EMAIL_HOST_USER,
            [username]
        )
        email.attach_alternative(content, 'text/html')
        email.send()

class CambioTitular(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda
    template_name = 'usuarios/cambiotitular.html'
    predio = VisualizarVivienda

    def get(self, request, IdVivienda):
        try:
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idpropietario = vivienda.IdPropietario
            matricula = IdVivienda
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            infovivienda = matricula + " " + sector + " " + casa
            propietario = Propietario.objects.filter(IdPropietario=idpropietario.pk)
            usuario = Usuario.objects.get(usuid=request.user.pk)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACFA').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'propietario': propietario, 'matricula': matricula,
                                                            'informacion': infovivienda})
        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            idpropietario = request.POST.get("idpropietario")
            propietario = Propietario.objects.filter(IdPropietario=idpropietario).exists()
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idpropi = vivienda.IdPropietario.pk
            if idpropi == idpropietario:
                ver = self.predio()
                messages.add_message(request, messages.ERROR,
                                     'el documento del titular ingresado es el mismo que tiene asignado '
                                     'actualmente el predio, modifique la informacion del titular directamente')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

            else:
                if propietario is True:
                    usuario = Usuario.objects.get(usuid=request.user.pk)
                    vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                    propie = Propietario.objects.get(IdPropietario=idpropietario)
                    propie2 = Propietario.objects.get(IdPropietario=idpropi)
                    vivienda.IdPropietario = propie
                    vivienda.save()
                    tiponovedad = 'Cambio titular'
                    descripcion = 'se cambia titular de la matricula ' + str(IdVivienda) + ' de ' + str(
                        propie2) + ' por ' + str(propie) + ' por solicitud del interesado '
                    novedad = Novedades(Descripcion=descripcion, TipoNovedad=tiponovedad, usuario=usuario,
                                                 matricula=vivienda)
                    novedad.save()
                    ver = self.predio()
                    messages.add_message(request, messages.INFO, 'Se modifica el titular correctamente')
                    ejecutar = ver.get(request, IdVivienda)
                    return ejecutar

                else:
                    ver = self.predio()
                    messages.add_message(request, messages.ERROR, 'el documento ingresado no existe en el sistema')
                    ejecutar = ver.get(request, IdVivienda)
                    return ejecutar

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Mapa(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/mapa.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACMAPA').exists()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            if tipousuario is False:
                return render(request, self.template_name, {
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti
                })

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ModificarAcueducto(LoginRequiredMixin, View):
    login_url = '/'
    form_class = AcueductoAForm
    template_name = 'usuarios/modificarempresa.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            datosacueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            form = self.form_class(instance=datosacueducto)
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {'form': form, 'notificaciones': contadorpen, 'listapqrs': listapqrs,
                               'totalnoti': totalnoti})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            datosacueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            form = self.form_class(request.user, request.POST, instance=datosacueducto)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'La información se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AsignarPermisos(LoginRequiredMixin, View):
    login_url = '/'
    form_class = PermisosForm
    template_name = 'usuarios/asignacionpermisos.html'

    def get(self, request, usuid):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            usuario2 = Usuario.objects.filter(usuid=usuid)
            consultar = Usuario.objects.get(usuid=usuid)
            permisos = Permisos.objects.filter(usuid=consultar)
            form = self.form_class(instance=usuario)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {'form': form, 'usuario': usuario2, 'permisos': permisos})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            tipopermiso = request.POST.get("TipoPermiso")
            usuid = request.POST.get("usuid")
            usuario = Usuario.objects.get(usuid=usuid)
            nu = 1
            if nu == 1:
                permisos = Permisos(TipoPermiso=tipopermiso, usuid=usuario)
                permisos.save()
                messages.add_message(request, messages.INFO, 'la informacion se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class EliminarPermisos(LoginRequiredMixin, View):
    login_url = '/'
    form_class = PermisosForm
    template_name = 'usuarios/eliminarpermisos.html'

    def get(self, request, usuid):
        try:
            usuario1 = Usuario.objects.get(usuid=request.user.pk)
            usuario = Usuario.objects.get(usuid=usuid)
            form = self.form_class(instance=usuario)
            permisos = Permisos.objects.filter(usuid=usuid)
            tipousuario = Permisos.objects.filter(usuid=usuario1, TipoPermiso='SUPERADMIN').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'form': form, 'permisos': permisos})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            tipopermiso = request.POST.get("TipoPermiso")
            usuid = request.POST.get("usuid")
            permisos = Permisos.objects.filter(usuid=usuid)
            verificacion = Permisos.objects.filter(usuid=usuid, TipoPermiso=tipopermiso).exists()
            if verificacion is True:
                for i in permisos:
                    permiso = i.TipoPermiso
                    if permiso == tipopermiso:
                        idborar = i.IdPermiso
                        borrar = Permisos.objects.get(IdPermiso=idborar)
                        borrar.delete()
                messages.add_message(request, messages.INFO, 'la informacion se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'El codigo de permiso seleccionado no esta asignado al usuario')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AgregarUsuarios(LoginRequiredMixin, View):
    login_url = '/'
    form_class = RegistroUsuario
    form_class2 = RegistroUsuario2
    template_name = 'usuarios/agregarusuarios.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            form = self.form_class()
            form2 = self.form_class2()
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {'form': form, 'form2': form2, 'notificaciones': contadorpen, 'listapqrs': listapqrs,
                               'totalnoti': totalnoti
                               })

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usernames = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            nombres = request.POST.get("first_name")
            apellidos = request.POST.get("last_name")

            foto = request.FILES.get("fotoUsuario")
            tipousuario = request.POST.get("TipoUsuario")
            telefono = request.POST.get("celular")
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            validarusu = User.objects.filter(username=usernames).exists()
            if validarusu is True:
                messages.add_message(request, messages.ERROR, 'El usuario ya existe')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

            else:
                user = User.objects.create_user(username=usernames, password=password, email=email, first_name=nombres,
                                                last_name=apellidos)
                usuario = Usuario(fotoUsuario=foto, TipoUsuario=tipousuario, celular=telefono, usuid=user,
                                  IdAcueducto=idacueducto)
                user.save()
                usuario.save()
                messages.add_message(request, messages.INFO, 'El usuario se creo correctamente')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class DesactivarUsuarios(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/eliminarusuario.html'

    def get(self, request, usuid):
        try:
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            usuario = Usuario.objects.filter(usuid=usuid)
            user = User.objects.get(id=usuid)
            estado = user.is_active
            tipousuario = Permisos.objects.filter(usuid=usuario2, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {'usuario': usuario, 'estado': estado})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
        try:
            user = User.objects.get(id=usuid)
            estado = user.is_active
            if estado is True:
                user.is_active = False
                user.save()
                messages.add_message(request, messages.INFO, 'El usuario se desactivo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                user.is_active = True
                user.save()
                messages.add_message(request, messages.INFO, 'El usuario se activo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class EliminarPoblacion(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            identificador = request.GET.get("identificador")
            usuario = Usuario.objects.get(usuid=request.user.pk)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='SUPERADMIN').exists()
            if tipousuario is False:
                verificacion = Poblacion.objects.filter(IdPoblacion=identificador).exists()
                if verificacion is True:
                    tipo = Poblacion.objects.get(IdPoblacion=identificador)
                    tipo.delete()
                    messages.add_message(request, messages.INFO, 'Tipo de poblacion eliminado correctamente')
                    return HttpResponseRedirect(reverse('usuarios:perfil'))
                else:
                    messages.add_message(request, messages.ERROR, 'El tipo de poblacion no EXISTE')
                    return HttpResponseRedirect(reverse('usuarios:perfil'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class CambiarContraUsuario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/cambiarcontrasena.html'

    def get(self, request, usuid):
        try:
            print(usuid)
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            usuario = Usuario.objects.filter(usuid=usuid)
            tipousuario = Permisos.objects.filter(usuid=usuario2, TipoPermiso='AccessPanel').exists()

            if tipousuario is True:
                return render(request, self.template_name, {'usuario': usuario})

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
        try:
            contrasena = request.POST.get("contrasena","")
            recontrasena = request.POST.get("recontrasena","")

            if contrasena == recontrasena:
                user = User.objects.get(id=usuid)
                user.set_password(contrasena)
                user.save()
                messages.add_message(request, messages.INFO, 'la conseña se cambio correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.INFO, 'Las contraseñas no coinciden')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ReporteCobroMatricula(LoginRequiredMixin, View):
    login_url = '/'

    def get(self):
        matriculas = CobroMatricula.objects.all()
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "ReporteCobroMatricula"
        ws['A1'] = 'Referencia'
        ws['B1'] = 'Descripcion'
        ws['C1'] = 'Vivienda'
        ws['D1'] = 'Estado'
        ws['E1'] = 'Valor'
        ws['F1'] = 'Cant cuotas'
        ws['G1'] = 'Cuotas pendientes'
        ws['H1'] = 'Valor pendiente'
        ws['I1'] = 'Cuota mensual'

        cont = 2
        for suspencion in matriculas:
            ws.cell(row=cont, column=1).value = suspencion.IdCobroM
            ws.cell(row=cont, column=2).value = suspencion.Descripcion
            ws.cell(row=cont, column=3).value = str(suspencion.IdVivienda)
            ws.cell(row=cont, column=4).value = suspencion.Estado
            ws.cell(row=cont, column=5).value = str(suspencion.IdValor)
            ws.cell(row=cont, column=6).value = suspencion.CantCuotas
            ws.cell(row=cont, column=7).value = suspencion.CuotasPendientes
            ws.cell(row=cont, column=8).value = suspencion.ValorPendiente
            ws.cell(row=cont, column=9).value = suspencion.Cuota
            cont += 1

            archivo_predios = "ReporteCobroMatricula" + str(sfecha) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response


class CambiosMasivos(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            estado = "Pago"
            cuotaspendientes = 0
            valorpendiente = 0

            cobromatricula = CobroMatricula.objects.all()
            if cobromatricula is not None:
                for i in cobromatricula:
                    cobro = CobroMatricula.objects.get(IdCobroM=i.IdCobroM)
                    cobro.Estado = estado
                    cobro.CuotasPendientes = cuotaspendientes
                    cobro.ValorPendiente = valorpendiente
                    cobro.save()
                messages.add_message(request, messages.ERROR, 'se modificaron los estados correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class CambioEstado(LoginRequiredMixin, View):
    login_url = '/'
    form_class = CambioFormEstado
    vervivienda = VisualizarVivienda
    template_name = 'usuarios/cambioestado.html'
    predio = VisualizarVivienda

    def get(self, request, IdVivienda):
        try:
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            form = self.form_class(instance=vivienda)
            matricula = IdVivienda
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            estado = vivienda.EstadoServicio
            infovivienda = matricula + " " + sector + " " + casa + " " + estado
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACFA').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'matricula': matricula,
                                                            'informacion': infovivienda, 'form': form})
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            estado = request.POST.get("EstadoServicio")

            if estado == "Operativo":
                vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                vivienda.EstadoServicio = "Operativo"
                vivienda.save()
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
                estadocuenta.Estado = "Operativo"
                estadocuenta.save()
                ver = self.predio()
                messages.add_message(request, messages.INFO,
                                     'El estado del servicio se modifico correctamente a OPERATIVO')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

            elif estado == "Suspendido":
                vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                vivienda.EstadoServicio = "Suspendido"
                vivienda.save()
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
                estadocuenta.Estado = "Suspendido"
                estadocuenta.save()
                ver = self.predio()
                messages.add_message(request, messages.INFO,
                                     'El estado del servicio se modifico correctamente a SUSPENDIDO')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

            elif estado == "Retirado":
                vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                vivienda.EstadoServicio = "Retirado"
                vivienda.save()
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
                estadocuenta.Estado = "Retirado"
                estadocuenta.save()
                ver = self.predio()
                messages.add_message(request, messages.INFO,
                                     'El estado del servicio se modifico correctamente a RETIRADO')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

            else:
                vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                vivienda.EstadoServicio = "Mantenimiento"
                vivienda.save()
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
                estadocuenta.Estado = "Mantenimiento"
                estadocuenta.save()
                ver = self.predio()
                messages.add_message(request, messages.INFO,
                                     'El estado del servicio se modifico correctamente a MANTENIMIENTO')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class CierreFinanciero(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/cierrefinanciero.html'

    def get(self, request):
        try:
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            fechaexp = (datetime.today())
            ano1 = fechaexp.year
            ano2 = fechaexp.year
            new_date = datetime(ano1, 1, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano2, 12, 31, 23, 59, 59, 00000)
            pagosultimoano = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            gastossultimoano = SolicitudGastos.objects.filter(Fecha__gte=new_date, Fecha__lte=new_date2).all()
            lingresos = Pagos.objects.all()
            lgastos = SolicitudGastos.objects.filter(Estado='Aprobada')
            pingregos = Cierres.objects.all().order_by("-IdCierre")
            credito = Credito.objects.filter(Estado='Vigente')

            suma8 = 0
            for i in credito:
                suma8 += int(i.ValorPendiente)

            iua = 0
            for i in pagosultimoano:
                iua += int(i.ValorPago)

            gua = 0
            for i in gastossultimoano:
                gua += int(i.Valor)

            ingre = 0
            for i in pingregos:
                ingre += int(i.Ingresos)

            gas = 0
            for i in pingregos:
                gas += int(i.Gastos)

            ingresos = 0
            for i in lingresos:
                ingresos += int(i.ValorPago)

            gastos = 0
            for i in lgastos:
                gastos += int(i.Valor)

            saldo = ingresos - gastos
            saldo2 = ingre - gas

            tipousuario = Permisos.objects.filter(usuid=usuario2, TipoPermiso='ACF').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'saldo': saldo,
                    'ingre': ingre,
                    'gas': gas,
                    'saldo2': saldo2,
                    'iua': iua,
                    'gua': gua,
                    'cierres': pingregos,
                    'credito': suma8

                })

            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            # entradas de la vista
            username1 = request.POST.get("username", "")
            password1 = request.POST.get("password", "")
            ingresos = request.POST.get("ingresos", "")
            egresos = request.POST.get("egresos", "")
            presupuesto = request.POST.get("presupuesto", "")
            periodo = request.POST.get("periodo", "")
            ano = request.POST.get("ano", "")
            # mensualidades:
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ano1 = fechaexp.year
            # Los argumentos serán: Año, Mes, Día, Hora, Minutos, Segundos, Milisegundos.
            new_date = datetime(ano1, ciclo, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano1, ciclo, 30, 23, 59, 59, 00000)
            pagos2 = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            gastosaprobados = SolicitudGastos.objects.filter(Fecha__gte=new_date, Fecha__lte=new_date2,
                                                             Estado=ESTADO2).all()
            gasto4 = 0
            for i in gastosaprobados:
                valor = int(i.Valor)
                gasto4 += valor

            pago0 = 0
            for i in pagos2:
                valor = i.ValorPago
                pago0 += int(valor)

            filtro = Cierres.objects.filter(Ciclo=periodo, Ano=ano).exists()
            usuario = auth.authenticate(username=username1, password=password1)
            if usuario is not None and usuario.is_active:
                if filtro is False:
                    if pago0 == int(ingresos) and gasto4 == int(egresos):
                        cierre = Cierres(Ingresos=ingresos, Gastos=egresos, Presupuesto=presupuesto, Ciclo=periodo,
                                         Ano=ano, NoRecaudo=usuario2)
                        cierre.save()
                        messages.add_message(request, messages.INFO, 'El cierre se efectuo correctamente')
                        return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

                    else:
                        messages.add_message(request, messages.ERROR,
                                             'Los valores no coinciden con los valores calculados por el sistema')
                        return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

                else:
                    messages.add_message(request, messages.ERROR, 'El periodo ingresado ya esta registrado')
                    return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

            else:
                messages.add_message(request, messages.ERROR, 'Credenciales incorrectas')
                return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ReporteCierre(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            cierres = Cierres.objects.all()
            sfecha = (datetime.today())
            wb = Workbook()
            ws = wb.active
            ws.title = 'Reporte de cierres'
            ws['A1'] = 'Id Cierre'
            ws['B1'] = 'Ingresos'
            ws['C1'] = 'Egresos'
            ws['D1'] = 'Saldo'
            ws['E1'] = 'Periodo'
            ws['F1'] = 'Año'
            ws['G1'] = 'Fecha de cierre'
            ws['H1'] = 'Usuario'
            cont = 2

            for cierre in cierres:
                ws.cell(row=cont, column=1).value = cierre.IdCierre
                ws.cell(row=cont, column=2).value = cierre.Ingresos
                ws.cell(row=cont, column=3).value = cierre.Gastos
                ws.cell(row=cont, column=4).value = cierre.Presupuesto
                ws.cell(row=cont, column=5).value = cierre.Ciclo
                ws.cell(row=cont, column=6).value = cierre.Ano
                ws.cell(row=cont, column=7).value = cierre.Fecha
                ws.cell(row=cont, column=8).value = cierre.NoRecaudo

                cont += 1

            archivo_predios = "ReporteCierresPeriodicos" + str(sfecha) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ReporteGastos(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            cierres = SolicitudGastos.objects.all()
            sfecha = (datetime.today())
            wb = Workbook()
            ws = wb.active
            ws.title = 'Reporte de gastos'
            ws['A1'] = 'Id gasto'
            ws['B1'] = 'Usuario registro'
            ws['C1'] = 'Descripcion'
            ws['D1'] = 'Tipo de solicitud'
            ws['E1'] = 'Valor'
            ws['F1'] = 'Estado'
            ws['G1'] = 'Fecha'
            ws['H1'] = 'AreaResponsable'
            cont = 2

            for cierre in cierres:
                ws.cell(row=cont, column=1).value = cierre.IdSoGa
                ws.cell(row=cont, column=2).value = str(cierre.IdUsuario)
                ws.cell(row=cont, column=3).value = cierre.Descripcion
                ws.cell(row=cont, column=4).value = cierre.TipoSolicitud
                ws.cell(row=cont, column=5).value = cierre.Valor
                ws.cell(row=cont, column=6).value = cierre.Estado
                ws.cell(row=cont, column=7).value = cierre.Fecha
                ws.cell(row=cont, column=8).value = cierre.AreaResponsable

                cont += 1

            archivo_predios = "Reportegastos" + str(sfecha) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")



class PanelAdmin(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/paneladmin.html'

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                # Consulta SQL para obtener el tamaño total de la base de datos en bytes
                cursor.execute(
                    "SELECT SUM(data_length + index_length) AS total_size FROM information_schema.tables "
                    "WHERE table_schema = DATABASE();")

                # Obtener el tamaño total de la base de datos en bytes
                result = cursor.fetchone()
                total_size_in_bytes = result[0] if result else 0

                # Convertir el tamaño total a megabytes
                total_size_in_megabytes = total_size_in_bytes / (1024 * 1024)

            usuario = Usuario.objects.get(usuid=request.user.pk)
            nit = usuario.IdAcueducto
            ye = datetime.now()
            ano = ye.year
            cantusu = Usuario.objects.all().count()
            usuarios = Usuario.objects.all()
            tarifas = Tarifa.objects.all().order_by('-IdTarifa')
            tarifa = Tarifa.objects.filter(Ano=ano)
            poblaciones = Poblacion.objects.all()
            matriculas = ValorMatricula.objects.all()
            acueducto = Acueducto.objects.get(IdAcueducto=nit)
            usuario = Usuario.objects.get(usuid=request.user.pk)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name, {
                    'ano': str(ano),
                    'logo': acueducto.logo,
                    'razonsocial': acueducto.Nombre,
                     'rlegal': acueducto.Relegal,
                    'sigla': acueducto.Sigla,
                    'nit': acueducto.IdAcueducto,
                    'direccion': acueducto.DirOficina,
                    'email': acueducto.Email,
                    'legal': acueducto.Relegal,
                    'telefono': acueducto.Telefono,
                    'estado': acueducto.Estado,
                    'tarifa': acueducto.IdTarifa.Valor,
                    'cantusu': cantusu,
                    'usuarios': usuarios,
                    'tarifas': tarifas,
                    'activa': tarifa,
                    'matriculas': matriculas,
                    'poblacion': poblaciones,
                    'mb': int(total_size_in_megabytes)

                }
                              )
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class PerfilUsuario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/perfilusuario.html'

    def get(self, request, IdUsuario):
        try:
            idusuario = IdUsuario
            usuario = Usuario.objects.get(usuid=request.user.pk)
            # inicio consultas
            infousuario = Usuario.objects.get(IdUsuario=idusuario)
            user = User.objects.get(username=infousuario.usuid)

            consultaradmin = Permisos.objects.filter(usuid=infousuario, TipoPermiso='AccessPanel').exists()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:

                return render(request, self.template_name, {
                    'cedula': infousuario.usuid_id,
                    'foto': infousuario.fotoUsuario,
                    'usuario': user.username,
                    'nombres': user.first_name,
                    'apellidos': user.last_name,
                    'celular': infousuario.celular,
                    'email': user.email,
                    'cargo': infousuario.TipoUsuario,
                    'fechac': infousuario.FechaCreacion,
                    'ultimo': user.last_login,
                    'departamento': infousuario.Departamento,
                    'tipousuario':consultaradmin

                }
                              )
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class ImprimirSoporteP(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, IdPago):
        try:
            # pago
            usuario = Usuario.objects.get(usuid=request.user.pk)
            telefono = str(usuario.IdAcueducto.Telefono)
            pago = Pagos.objects.get(IdPago=IdPago)
            idfactura = pago.IdFactura
            idpago = str(pago.IdPago)
            fecha1 = pago.FechaPago
            fecha = str(fecha1.year) + '-' + str(fecha1.month) + '-' + str(fecha1.day) + ' ' + str(
                fecha1.hour) + ':' + str(fecha1.minute)
            valorpago = str(pago.ValorPago)
            resta = str(pago.resta)
            # factura
            factura = Factura.objects.get(IdFactura=idfactura.pk)
            idfac = str(factura.IdFactura)
            periodo = factura.IdCiclo.Nombre
            referencia = str(factura.Matricula)
            totalfactura = str(factura.Total)
            # Impresora
            nombreImpresora = "termica3"
            conector = ConectorV3()
            conector.Iniciar()
            conector.DeshabilitarElModoDeCaracteresChinos()
            conector.EstablecerAlineacion(ALINEACION_CENTRO)
            conector.TextoSegunPaginaDeCodigos(2, "cp850", "¡AUECAAC ESP!\n")
            conector.EscribirTexto("NIT 900.017.239-2\n")
            conector.EstablecerEnfatizado(True)
            conector.EscribirTexto("COMPROBANTE DE PAGO\n")
            conector.EstablecerEnfatizado(False)
            conector.Feed(1)
            conector.EstablecerAlineacion(ALINEACION_IZQUIERDA)
            conector.EscribirTexto("Numero de transaccion: ")
            conector.EscribirTexto(idpago + "\n")
            conector.EscribirTexto("Numero de factura: ")
            conector.EscribirTexto(idfac + "\n")
            conector.EscribirTexto("Fecha de pago: ")
            conector.EscribirTexto(fecha + "\n")
            conector.EscribirTexto("Punto de pago: Oficina principal\n")
            conector.EscribirTexto("Whatsapp: " + telefono + "\n")
            conector.EscribirTexto("Periodo de pago: " + periodo + "\n")
            conector.EscribirTexto("Referencia: \n")
            conector.EscribirTexto(referencia + "\n")
            conector.Feed(1)
            conector.EscribirTexto("Estado de cuenta antes de este \n")
            conector.EscribirTexto("pago: ")
            conector.EscribirTexto("$ " + totalfactura + "\n")
            conector.EscribirTexto("Resta: ")
            conector.EscribirTexto("$ " + resta + "\n")
            conector.EstablecerAlineacion(ALINEACION_CENTRO)
            conector.EscribirTexto("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n")
            conector.EstablecerEnfatizado(True)
            conector.EscribirTexto("Valor pagado: ")
            conector.EstablecerEnfatizado(False)
            conector.EscribirTexto("$ " + valorpago + "\n")
            conector.EscribirTexto("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n")
            conector.EstablecerEnfatizado(True)
            conector.EscribirTexto("Para cualquier acto de reclamacion, debera presentar este soporte de pago\n")
            conector.EstablecerEnfatizado(False)
            conector.Feed(1)
            conector.EscribirTexto("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n")
            conector.Feed(1)
            conector.EstablecerAlineacion(ALINEACION_CENTRO)
            conector.Corte(1)
            conector.Pulso(48, 60, 120)
            respuesta = conector.imprimirEn(nombreImpresora)
            if respuesta is True:
                messages.add_message(request, messages.INFO, 'impreso correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.ERROR, respuesta)
                return HttpResponseRedirect(reverse('usuarios:inicio'))
        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class PazSalvo(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda

    def get(self, request, matricula):
        try:
            idvivienda = matricula
            vivienda = Vivienda.objects.get(IdVivienda=idvivienda)
            estado = vivienda.EstadoServicio
            idpropietario = vivienda.IdPropietario
            titular = Propietario.objects.get(IdPropietario=idpropietario.pk)
            nombrecompleto = str(titular.Nombres) + ' ' + str(titular.Apellidos)
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            direccion = sector + ' Casa No ' + casa
            now = datetime.now()
            dia = now.day
            mes = now.month
            anio = now.year

            if 1 == 1:
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=idvivienda)
                valor = estadocuenta.Valor
                if valor <= 0:
                    wb = openpyxl.load_workbook('static/Formatos/E8CPS.xlsx')
                    ws = wb.active
                    # primer mensaje
                    ws['U9'] = idvivienda
                    ws['A10'] = nombrecompleto
                    ws['A11'] = direccion
                    ws[
                        'A16'] = 'no aplica'
                    ws['A22'] = 'El presente certificado se expide por solicitud del interesado a los ' + str(
                        dia) + ' días del mes ' + str(mes) + ' del año ' + str(anio)
                    if estado == 'Operativo':
                        ws[
                            'A26'] = 'Como el predio tiene la matricula activa, el presente certificado ' \
                                     'solo es valido por 30 dias a partir de la fecha de expedicion.'
                    else:
                        ws['A26'] = ' '
                    ws.title = idvivienda
                    archivo_predios = "paz y salvo " + str(idvivienda) + ".xlsx"
                    response = HttpResponse(content_type="application/ms-excel")
                    content = "attachment; filename = {0}".format(archivo_predios)
                    response['Content-Disposition'] = content
                    wb.save(response)
                    return response
                else:
                    messages.add_message(request, messages.ERROR,
                                         'El predio no se encuentra a paz y salvo por conceptos de acueducto')
                    ver = self.vervivienda()
                    ejercutar = ver.get(request, idvivienda)
                    return ejercutar

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class CertificadoGral(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda

    def get(self, request):
        try:
            matricula = request.GET.get("matricula")
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            idpropietario = vivienda.IdPropietario
            propietario = Propietario.objects.get(IdPropietario=idpropietario.pk)
            estadocuenta = EstadoCuenta.objects.get(IdVivienda=matricula)
            idestadocuenta = estadocuenta.IdEstadoCuenta
            conceptomatricula = CobroMatricula.objects.get(IdVivienda=matricula)

            if vivienda is not None:
                wb = openpyxl.load_workbook('static/Formatos/R4C.xlsx')
                ws = wb.active
                # titular
                ws['W2'] = matricula
                ws['A7'] = propietario.Nombres
                ws['H7'] = propietario.Apellidos
                ws['W7'] = propietario.IdPropietario
                ws['A9'] = propietario.NoTelefono
                ws['H9'] = propietario.IdPoblacion.Descripcion
                ws['R9'] = propietario.Email
                # predio
                ws['A13'] = vivienda.Direccion
                ws['H13'] = vivienda.NumeroCasa
                ws['O13'] = vivienda.Piso
                ws['S13'] = vivienda.Ciclo
                ws['x13'] = vivienda.MatriculaAnt
                ws['A15'] = vivienda.InfoInstalacion
                ws['R15'] = vivienda.CantHabitantes
                ws['W15'] = vivienda.Estrato
                ws['A17'] = vivienda.TipoInstalacion
                ws['K15'] = vivienda.EstadoServicio
                ws['K17'] = vivienda.FichaCastral

                # Estado de cuenta
                ws['S35'] = estadocuenta.IdEstadoCuenta
                ws['Y35'] = estadocuenta.Estado
                ws['S37'] = estadocuenta.FechaActualizacion
                ws['Y37'] = estadocuenta.Valor

                # Estado de matricula
                ws['S27'] = conceptomatricula.IdCobroM
                ws['Y27'] = conceptomatricula.Estado
                ws['S29'] = conceptomatricula.CantCuotas
                ws['Y29'] = conceptomatricula.IdValor.Valor
                ws['S31'] = conceptomatricula.CuotasPendientes
                ws['W31'] = conceptomatricula.ValorPendiente
                ws['AA31'] = conceptomatricula.Cuota

                # ordenes de trabajo
                suspencionespen = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,
                                                                   Estado='Pendiente').count()
                suspencioneseje = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,
                                                                   Estado='Ejecutada').count()
                suspencionesanu = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,
                                                                   Estado='Anulada').count()
                ws['S42'] = suspencioneseje
                ws['U42'] = suspencionesanu
                ws['W42'] = suspencionespen
                reconexionespen = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestadocuenta,
                                                                   Estado='Pendiente').count()
                reconexioneseje = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestadocuenta,
                                                                   Estado='Ejecutada').count()
                ws['Y42'] = reconexioneseje
                ws['AA42'] = reconexionespen

                # ultimo pago
                filtropagos = Pagos.objects.filter(IdVivienda=matricula).order_by("-IdPago")[:1]
                idpago = Pagos.objects.get(IdPago=filtropagos)
                ws['S49'] = str(idpago)
                ws['Y49'] = 'Registrado'
                ws['S51'] = idpago.FechaPago
                ws['Y51'] = idpago.ValorPago

                # fechas de procedimiento
                now = datetime.now()
                new_date = now + timedelta(days=30)
                ws['A54'] = now
                ws['A56'] = new_date

                ws.title = matricula
                archivo_predios = "Certificado " + str(matricula) + ".xlsx"
                response = HttpResponse(content_type="application/ms-excel")
                content = "attachment; filename = {0}".format(archivo_predios)
                response['Content-Disposition'] = content
                wb.save(response)
                return response

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class CobroRecargo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/cobrorecargo.html'

    def get(self, request):
        try:
            estadoscuenta = EstadoCuenta.objects.all()
            cont = 0
            for i in estadoscuenta:
                valor = int(i.Valor)
                if valor >= 17000:
                    cont += 1

            return render(request, self.template_name, {
                'cont': cont})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            idtarifa = acueducto.IdTarifa
            tarifa = Tarifa.objects.get(IdTarifa=idtarifa)
            recargo = tarifa.Recargo

            estadoscuenta = EstadoCuenta.objects.all()
            cont = 0
            for i in estadoscuenta:
                valor = i.Valor
                if valor >= 17000:
                    cont += 1
                    estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=i.pk)
                    estadoscu.Valor += int(recargo)
                    estadoscu.save()

            messages.add_message(request, messages.INFO, 'Se genero el cobro de los recargos correctamente')
            return HttpResponseRedirect(reverse('usuarios:estadoscuenta'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VerFactura(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verfactura.html'
    imptiquet = ImprimirSoporteP

    def get(self, request):
        try:
            numerofactura = request.GET.get('factura', ' ')
            usuario = Usuario.objects.get(usuid=request.user.pk)
            anulada = Factura.objects.filter(IdFactura=numerofactura, Estado=FA).exists()
            paga = Factura.objects.filter(IdFactura=numerofactura, Estado=FP).exists()
            vencida = Factura.objects.filter(IdFactura=numerofactura, Estado=FV).exists()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AVF').exists()
            if tipousuario is True:
                consulta = Factura.objects.filter(IdFactura=numerofactura).exists()
                if consulta is True:
                    factura = Factura.objects.get(IdFactura=numerofactura)
                    idestado = factura.IdEstadoCuenta
                    estadoscuenta = EstadoCuenta.objects.get(IdEstadoCuenta=idestado.pk)
                    pagos = EstadoCuenta.objects.filter(IdEstadoCuenta=idestado.pk)
                    idvivienda = estadoscuenta.IdVivienda
                    cobromatricula = CobroMatricula.objects.filter(IdVivienda=idvivienda, Estado=ESTCOBRO)
                    vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
                    matricula = vivienda.IdVivienda
                    sector = vivienda.Direccion
                    casa = vivienda.NumeroCasa
                    piso = vivienda.Piso
                    fe = factura.FechaExpe
                    fl = factura.FechaLimite
                    total = factura.Total
                    ciclo = factura.IdCiclo
                    estadofactura = factura.Estado
                    aporteporconsumo = factura.aporteporconsumo
                    cuotamatricula = factura.cuotamatricula
                    reconexion = factura.reconexion
                    suspencion2 = factura.suspencion
                    cuenta = factura.IdEstadoCuenta
                    return render(request, self.template_name, {
                        'aportes': int(aporteporconsumo),
                        'cuenta': cuenta,
                        'cuotam': int(cuotamatricula),
                        'reconexion': int(reconexion),
                        'suspencion': int(suspencion2),
                        'cobromatricula': cobromatricula,
                        'estadoscuenta': total,
                        'factura': numerofactura,
                        'fe': fe,
                        'fl': fl,
                        'total': total,
                        'estadofactura': estadofactura,
                        'matricula': matricula,
                        'casa': casa,
                        'sector': sector,
                        'piso': piso,
                        'pagos': pagos,
                        'ciclo': ciclo,
                        'anulada': anulada,
                        'paga': paga,
                        'vencida': vencida,
                    })
                else:
                    messages.add_message(request, messages.ERROR, 'El numero de factura ingresado no existe')
                    return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.ERROR,
                                     'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            numerofactura = request.POST.get("factura", "")
            valorpagar = request.POST.get("valorp", "")
            efectivo = request.POST.get("efectivo", "")
            factura = Factura.objects.get(IdFactura=numerofactura)
            idestado = factura.IdEstadoCuenta
            estado = EstadoCuenta.objects.get(IdEstadoCuenta=idestado.pk)
            idvivienda = estado.IdVivienda
            descripcion = 'Consumo'
            formato = "%Y"
            s = (datetime.today())
            ano = s.strftime(formato)
            resta = int(estado.Valor) - int(valorpagar)
            devuelta = int(efectivo) - int(valorpagar)
            s = (datetime.today())
            fecha = s + timedelta(days=2)
            if int(valorpagar) >= 2000:
                pago = Pagos(IdFactura=factura, Ano=ano, ValorPago=valorpagar, Descripcion=descripcion,
                             Efectivo=efectivo, Devuelta=devuelta,
                             IdUsuario=usuario, IdVivienda=idvivienda, resta=resta)
                pago.save()
                idpago = pago.IdPago
                estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=idestado.pk)
                estadoscu.Valor = resta
                estadoscu.save()
                cambiofactura = Factura.objects.get(IdFactura=numerofactura)
                cambiofactura.Estado = FP
                cambiofactura.save()
                verifisus = OrdenesSuspencion.objects.filter(IdEstadoCuenta=estadoscu, Estado=SP).count()
                if verifisus >= 1:
                    suspencion = OrdenesSuspencion.objects.get(IdEstadoCuenta=estadoscu, Estado=SP)
                    suspencion.Estado = SA
                    suspencion.FechaEjecucion = s
                    suspencion.UsuarioEjecuta = 'Sistema'
                    suspencion.save()

                else:
                    estadoscuenta = EstadoCuenta.objects.filter(IdEstadoCuenta=idestado.pk, Estado=E2).exists()
                    valor = 'abono'
                    if estadoscuenta is True:
                        orden = OrdenesReconexion(Deuda=valor, FechaEjecucion=fecha, Generado='auto', Estado=SP,
                                                  UsuarioEjecuta='Font', IdEstadoCuenta=estadoscu)
                        orden.save()
                descripcion = 'Se registra pago: ' + str(idpago) + ' Factura: ' + str(
                    numerofactura) + ' Matricula: ' + str(idvivienda) + ' Valor: $' + str(valorpagar)
                novedad = Novedades(Descripcion=descripcion, TipoNovedad='Pago', usuario=usuario, matricula=idvivienda)
                novedad.save()
                tiquet2 = self.imptiquet()
                ejecutar = tiquet2.get(request, idpago)
                return ejecutar
            else:
                messages.add_message(request, messages.INFO, 'el valor a pagar debe ser superior a $2000')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class AnularPago(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/anularpago.html'

    def get(self, request):
        try:
            usuario = 0
            if usuario == 0:
                return render(request, self.template_name)

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            comprobante = request.POST.get("Numero")
            pago = Pagos.objects.get(IdPago=comprobante)
            matricula = pago.IdVivienda
            valorpagado = pago.ValorPago
            estadocuenta = EstadoCuenta.objects.get(IdVivienda=matricula)
            factura = Factura.objects.get(IdFactura=pago.IdFactura.pk)
            if int(comprobante) >= 1:
                factura.Estado = 'Emitida'
                factura.save()
                valor = estadocuenta.Valor + int(valorpagado)
                estadocuenta.Valor = valor
                estadocuenta.save()
                descripcion = 'Se anula pago no: ' + str(comprobante) + ' Matricula: ' + str(
                    pago.IdVivienda) + ' valor: ' + str(pago.ValorPago)
                novedad = Novedades(Descripcion=descripcion, matricula=matricula, usuario=usuario, TipoNovedad='Pago anulado')
                novedad.save()
                pago1 = Pagos.objects.get(IdPago=comprobante)
                pago1.delete()
                messages.add_message(request, messages.INFO, 'El pago se anulo correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, 'No se pudo anular el pago')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Matriculas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/matriculas.html'

    def get(self, request):
        try:
            # lista de predios
            pnv = Vivienda.objects.filter(Direccion='Pasonivel Viejo').count()
            pnd = Vivienda.objects.filter(Direccion='Pasonivel Destapada').count()
            cc = Vivienda.objects.filter(Direccion='Caimalito Centro').count()
            bn = Vivienda.objects.filter(Direccion='Barrio Nuevo').count()
            vj = Vivienda.objects.filter(Direccion='20 de julio').count()
            hd = Vivienda.objects.filter(Direccion='Hacienda').count()
            carb = Vivienda.objects.filter(Direccion='Carbonera').count()

            # disponible
            epnv = AsignacionBloque.objects.filter(Bloque='PNV', Estado='Sin asignar').count()
            epnd = AsignacionBloque.objects.filter(Bloque='PND', Estado='Sin asignar').count()
            ecc = AsignacionBloque.objects.filter(Bloque='CC', Estado='Sin asignar').count()
            ebn = AsignacionBloque.objects.filter(Bloque='BN', Estado='Sin asignar').count()
            ehd = AsignacionBloque.objects.filter(Bloque='HD', Estado='Sin asignar').count()
            evj = AsignacionBloque.objects.filter(Bloque='VJ', Estado='Sin asignar').count()
            car = AsignacionBloque.objects.filter(Bloque='CA', Estado='Sin asignar').count()

            # filtros
            fpnv = AsignacionBloque.objects.filter(Bloque='PNV', Estado='Sin asignar')
            fpnd = AsignacionBloque.objects.filter(Bloque='PND', Estado='Sin asignar')
            fcc = AsignacionBloque.objects.filter(Bloque='CC', Estado='Sin asignar')
            fbn = AsignacionBloque.objects.filter(Bloque='BN', Estado='Sin asignar')
            fhd = AsignacionBloque.objects.filter(Bloque='HD', Estado='Sin asignar')
            fvj = AsignacionBloque.objects.filter(Bloque='VJ', Estado='Sin asignar')
            fcar = AsignacionBloque.objects.filter(Bloque='CA', Estado='Sin asignar')

            usuario = 0
            if usuario == 0:
                return render(request, self.template_name,
                              {'pnv': pnv, 'pnd': pnd, 'cc': cc, 'bn': bn, 'vj': vj, 'hd': hd,
                               'epnv': epnv, 'epnd': epnd, 'ecc': ecc, 'ebn': ebn, 'ehd': ehd, 'evj': evj,
                               'fhd': fhd, 'fpnv': fpnv, 'fpnd': fpnd, 'fvj': fvj, 'fbn': fbn, 'fcc': fcc,
                               'car':car,'fcar':fcar, 'carb':carb
                               })
        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Bloque(LoginRequiredMixin, View):
    login_url = '/'

    def get(self):
        sector = 'Pasonivel Viejo'
        predios = Vivienda.objects.filter(Direccion=sector)
        suma = 0
        for i in predios:
            idvivienda = i.IdVivienda
            estadocuenta = EstadoCuenta.objects.get(IdVivienda=idvivienda)
            idestadocuenta = estadocuenta.IdEstadoCuenta
            buscar = AsignacionBloque.objects.get(Matricula=idvivienda)
            buscar.Estado = 'Asignada'
            buscar.Estadocuenta = idestadocuenta
            buscar.save()
            suma += 1

        return suma


class AsignarCargo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/asignacioncargo.html'
    form_class = CobroMatriculaForm
    vizualizarv = VisualizarVivienda

    def get(self, request, matricula):
        try:
            form = self.form_class
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            direccion = vivienda.Direccion + ' Cs ' + vivienda.NumeroCasa + ' Piso ' + vivienda.Piso
            bloque = AsignacionBloque.objects.get(Matricula=matricula)
            fecha = bloque.Fecha
            estadocuenta = bloque.Estadocuenta
            usuario1 = 0
            if usuario1 == 0:
                return render(request, self.template_name,
                              {'form': form, 'matricula': matricula, 'direccion': direccion, 'fecha': fecha,
                               'cuenta': estadocuenta})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, matricula):
        try:
            idvivienda = matricula
            descripcion = 'Cargo por conexion'
            estado = 'Pendiente'
            idvalor = request.POST.get("IdValor")
            cantcuotas = request.POST.get("CantCuotas")
            cuotaspendientes = cantcuotas
            vivienda = Vivienda.objects.filter(IdVivienda=idvivienda).exists()
            vivienda2 = Vivienda.objects.get(IdVivienda=idvivienda)
            valor = ValorMatricula.objects.get(IdValor=idvalor)
            valorpendiente = valor.Valor
            cuota = int(valorpendiente)
            if vivienda is True:
                matricula = CobroMatricula(Descripcion=descripcion, IdVivienda=vivienda2, Estado=estado, IdValor=valor,
                                           CantCuotas=cantcuotas,
                                           CuotasPendientes=cuotaspendientes, ValorPendiente=valorpendiente,
                                           Cuota=cuota)
                matricula.save()
                ver = self.vizualizarv()
                messages.add_message(request, messages.INFO, 'La informacion del predio se agrego correctamente')
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

            else:
                messages.add_message(request, messages.ERROR, 'ERROR')
                return HttpResponseRedirect(reverse('usuarios:matriculas'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Creditos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/creditos.html'

    def get(self, request):
        try:
            creditos = Credito.objects.all()
            vigentes = Credito.objects.filter(Estado='Vigente').count()
            creditosv = Credito.objects.filter(Estado='Vigente')
            creditosp = Credito.objects.filter(Estado='Pagado')
            pagados = Credito.objects.filter(Estado='Pagado').count()
            deudatotal = 0
            for i in creditos:
                valor = i.ValorInicial
                deudatotal += int(valor)

            deudapendiente = 0
            for i in creditos:
                valor = i.ValorPendiente
                deudapendiente += int(valor)

            usuario1 = 0
            if usuario1 == 0:
                return render(request, self.template_name, {'vigentes': vigentes,
                                                            'creditosv': creditosv, 'creditosp': creditosp,
                                                            'deudatotal': deudatotal,
                                                            'deudapendiente': deudapendiente, 'pagados': pagados})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroCredito(LoginRequiredMixin, View):
    login_url = '/'
    form_class = FormRegistroCredito
    template_name = 'usuarios/registrocredito.html'

    def get(self, request):
        try:
            form = self.form_class()
            return render(request, self.template_name,
                          {
                              'form': form
                          })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            form = self.form_class(request.POST)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'El credito se agrego correctamente')
                return HttpResponseRedirect(reverse('usuarios:credito'))

            else:
                messages.add_message(request, messages.ERROR, 'No se pudo agregar la informacion al sistema')
                return HttpResponseRedirect(reverse('usuarios:credito'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistroProveedor(LoginRequiredMixin, View):
    login_url = '/'
    form_class = FormRegistroProveedor
    template_name = 'usuarios/registroproveedor.html'

    def get(self, request, *args, **kwargs):
        try:
            form = self.form_class()
            return render(request, self.template_name,
                          {
                              'form': form
                          })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, *args):
        try:
            form = self.form_class(request.POST)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'La informacion del proveedor se agrego correctamente')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.ERROR, 'No se pudo agregar la informacion al sistema')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class VerCredito(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/vercredito.html'

    def get(self, request, idcredito):
        try:
            credito = Credito.objects.filter(IdCredito=idcredito)
            credito2 = Credito.objects.get(IdCredito=idcredito)
            estado = credito2.Estado
            verificarpagos = SolicitudGastos.objects.filter(NumeroFactura=idcredito)
            return render(request, self.template_name, {'credito': credito, 'pagos': verificarpagos, 'estado': estado})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idcredito):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            valor = request.POST.get("valor")
            credito = Credito.objects.get(IdCredito=idcredito)
            numcuota = credito.CuotasPendiente
            nombrecredito = credito.NombreCredito
            mensaje = 'Cuota no' + str(numcuota) + '|' + str(nombrecredito)
            savegasto = SolicitudGastos(Descripcion=mensaje, TipoSolicitud='Pago de creditos', Valor=valor,
                                        Estado='Pendiente',
                                        AreaResponsable='Area Administrativa', NumeroFactura=idcredito,
                                        IdUsuario=usuario)
            savegasto.save()
            cuotamenos = int(numcuota) - 1
            valorpen = int(credito.ValorPendiente) - int(valor)
            if cuotamenos <= 0:
                credito.CuotasPendiente = str(cuotamenos)
                credito.ValorPendiente = str(valorpen)
                credito.Estado = 'Pagado'
                credito.save()
                messages.add_message(request, messages.INFO, 'El credito fue pagado con exito')
                return HttpResponseRedirect(reverse('usuarios:credito'))

            else:
                credito.CuotasPendiente = str(cuotamenos)
                credito.ValorPendiente = str(valorpen)
                credito.save()
                messages.add_message(request, messages.INFO, 'La cuota se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:credito'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class PagoParcial(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/pagoparcial.html'

    def get(self, request):
        try:
            usuario = 0
            if usuario == 0:
                return render(request, self.template_name)

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class ReporteRetiro(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/retiro.html'

    def get(self, request, matricula):
        try:
            usuario = 0
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            matricula1 = vivienda.IdVivienda
            if usuario == 0:
                return render(request, self.template_name, {'idvivienda': matricula1})

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, matricula):
        try:
            usuarios = Usuario.objects.get(usuid=request.user.pk)
            Descripcion = request.POST.get("descripcion")
            usuario =0
            if usuario == 0:
                vivienda = Vivienda.objects.get(IdVivienda=matricula)
                registrarnovedad = Novedades(IdVivienda=vivienda,Descripcion=Descripcion, TipoNovedad='Retiro',usuario=usuarios)
                vivienda.EstadoServicio = 'Retirado'
                vivienda.save()
                registrarnovedad.save()
                messages.add_message(request, messages.INFO, 'La novedad se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))


        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class Consumo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/Consumos.html'

    def get(self, request):
        try:
            usuario = 0
            sinasignar = Medidores.objects.filter(Estado='Sin asignar')
            asignado = Asignacion.objects.filter(Estado='Operativo')
            contar = Asignacion.objects.filter(Estado='Operativo').count()
            vapo = Consumos.objects.all().aggregate(Consumo=Sum('Consumo'))
            suma = vapo['Consumo']

            if usuario == 0:
                return render(request, self.template_name,{
                    'sinasignar':sinasignar, 'asignado':asignado, 'contar': contar,'suma':suma
                })

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")


class RegistrarConsumo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/Registrarconsumos.html'

    def get(self, request):
        try:
            matricula = request.GET.get('matricula')
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            asignado = Asignacion.objects.filter(IdVivienda=matricula,Estado='Operativo').exists()

            if asignado == True:
                return render(request, self.template_name,{'matricula': matricula})
            else:
                messages.add_message(request, messages.ERROR, 'El predio no tiene micromedidor asignado')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            lecturaactual = request.POST.get("lectura")
            observacion = request.POST.get("observacion")
            matricula = request.POST.get("matricula")
            medidor = Asignacion.objects.get(IdVivienda=matricula)
            idmedidor = medidor.IdMedidor
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            consultarconsumo = Consumos.objects.filter(IdVivienda=matricula).exists()

            fechaexp = (datetime.today())
            mes1 = fechaexp.month
            ciclos = Ciclo.objects.get(IdCiclo=mes1)
            mes = ciclos.Nombre
            ano = fechaexp.year

            if consultarconsumo == False:
                consumo1 = Consumos(IdMedidor=idmedidor, IdVivienda=vivienda, Lecturaactual=lecturaactual,Lecturaanterior=0,Consumo=lecturaactual,promedio=lecturaactual,
                                    observaciones=observacion,diasconsumo=30, ano=ano, mes=mes)
                consumo1.save()
                messages.add_message(request, messages.INFO, 'La informacion se ha guardado correctamente')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

            else:
                vapo = Consumos.objects.filter(IdVivienda=matricula).aggregate(Consumo=Sum('Consumo'))
                suma = vapo['Consumo']
                cantidadregistros = Consumos.objects.filter(IdVivienda=matricula).count()
                consultarconsumo = Consumos.objects.filter(IdVivienda=matricula).order_by("-IdRegistro")[:1]
                primerobjeto = consultarconsumo[0]

                lecturaanterior = primerobjeto.Lecturaactual
                consumo = int(lecturaactual) - int(lecturaanterior)
                suma2 = consumo + suma
                promedio = suma2 / (cantidadregistros + 1)
                consumo1 = Consumos(IdMedidor=idmedidor, IdVivienda=vivienda, Lecturaactual=lecturaactual,
                                    Lecturaanterior=lecturaanterior, Consumo=consumo, promedio=int(promedio),
                                    observaciones=observacion, diasconsumo=30, ano=ano, mes=mes)
                consumo1.save()

                messages.add_message(request, messages.INFO, 'PRUEBA 1 EXISITOSA')
                return HttpResponseRedirect(reverse('usuarios:consumos'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class VerConsumo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/consumosuscriptor.html'

    def get(self, request, matricula):
        try:

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = True
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
            asignado = Asignacion.objects.get(IdVivienda=matricula,Estado='Operativo')
            idmedidor = asignado.IdMedidor
            medidor = Medidores.objects.get(IdMedidor=idmedidor)
            consumos = Consumos.objects.filter(IdVivienda=matricula).order_by("-IdRegistro")

            if tipousuario is True:
                return render(request, self.template_name, {'medidor': medidor.IdMedidor, 'estado':medidor.Estado,'estado2': asignado.Estado,
                                                            'matricula': matricula, 'consumos': consumos})
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta '
                                                              'seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class GenerarConceptos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/consumosuscriptor.html'

    def get(self, request):
        try:

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = True
            vivienda = Vivienda.objects.all()
            estados = EstadoCuenta.objects.filter(Estado='Operativo')|EstadoCuenta.objects.filter(Estado='Suspendido')

            if tipousuario is True:
                for i in estados:
                    if i.Valor <=0:
                        concepto = Conceptos(Tipo='Aporte fijo',Observacion='Marzo',Estado='Facturado',Valor=i.Valor,IdVivienda=i.IdVivienda)
                        concepto.save()

                    else:
                        concepto = Conceptos(Tipo='Aporte fijo', Observacion='Marzo', Estado='Sin facturar', Valor=i.Valor, IdVivienda=i.IdVivienda)
                        concepto.save()

                messages.add_message(request, messages.INFO, 'La operacion se realizo correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta '
                                                              'seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class GeneradorConceptos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/consumosuscriptor.html'

    def get(self, request):
        try:

            usuario = Usuario.objects.get(usuid=request.user.pk)
            acueducto = Acueducto.objects.get(IdAcueducto=usuario.IdAcueducto)
            idtarifa = acueducto.IdTarifa
            tarifa = Tarifa.objects.get(IdTarifa=idtarifa.pk)
            aportefijo = tarifa.Valor
            m3 = tarifa.m3
            valormetro = tarifa.valormetro
            fechaexp = (datetime.today())
            mes1 = fechaexp.month
            ciclos = Ciclo.objects.get(IdCiclo=mes1)
            mes = ciclos.Nombre
            ano = fechaexp.year
            tipousuario = True
            viviendas = Vivienda.objects.all()
            consumos = Consumos.objects.filter(mes=mes)
            matriculas = CobroMatricula.objects.filter(Estado='Pendiente')
            if tipousuario is True:
                for i in viviendas:
                    if i.EstadoServicio == 'Operativo':
                        vivienda = Vivienda.objects.get(IdVivienda=i.IdVivienda)
                        concepto = Conceptos(Tipo='Aporte fijo', Observacion=mes, Estado='Sin facturar',
                                             Valor=aportefijo, IdVivienda=vivienda)
                        concepto.save()

                for i in consumos:
                    if int(i.Consumo) > int(m3):
                        resta = int(i.Consumo) - int(m3)
                        resultado = int(valormetro) * resta
                        concepto = Conceptos(Tipo='Consumo complementario', Observacion=mes + ' - Consumo m3: ' + str(resta),
                                             Estado='Sin facturar', Valor=resultado, IdVivienda=i.IdVivienda)
                        concepto.save()

                for i in matriculas:
                    if int(i.CuotasPendientes) >=2:
                        editarcobro = CobroMatricula.objects.get(IdVivienda=i.IdVivienda)
                        editarcobro.CuotasPendientes = int(i.CuotasPendientes) - 1
                        editarcobro.ValorPendiente = int(i.ValorPendiente) - int(i.Cuota)
                        editarcobro.save()
                        concepto = Conceptos(Tipo='Aporte matricula', Observacion=mes + ' - Cuota No: ' + i.CuotasPendientes,
                                             Estado='Sin facturar', Valor=i.Cuota, IdVivienda=i.IdVivienda)
                        concepto.save()

                    else:
                        editarcobro = CobroMatricula.objects.get(IdVivienda=i.IdVivienda)
                        editarcobro.CuotasPendientes = int(i.CuotasPendientes) - 1
                        editarcobro.ValorPendiente = int(i.ValorPendiente) - int(i.Cuota)
                        editarcobro.Estado = 'Pago'
                        editarcobro.save()
                        concepto = Conceptos(Tipo='Aporte matricula', Observacion=mes + ' - Cuota No: ' + i.CuotasPendientes,
                                                 Estado='Sin facturar', Valor=i.Cuota, IdVivienda=i.IdVivienda)
                        concepto.save()

                messages.add_message(request, messages.INFO, 'La operacion se realizo correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta '
                                                              'seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")

class FacturadorConceptos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/consumosuscriptor.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = True
            retiro = Novedades.objects.all()

            if tipousuario is True:
                for i in retiro:
                    concepto = Novedades(Descripcion=i.Descripcion, TipoNovedad='Adicion', usuario=usuario,
                                             matricula=i.IdVivienda)
                    concepto.save()

                messages.add_message(request, messages.INFO, 'La operacion se realizo correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta '
                                                              'seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except ObjectDoesNotExist:
            return render(request, "pages-404.html")