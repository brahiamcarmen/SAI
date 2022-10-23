# -*- coding: utf-8 -*-
import os
import socket
from django.shortcuts import render
from django.conf import settings
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from SAAL.models import Usuario, Tarifa, CobroOrdenes,PagoOrdenes,Certificaciones, Cierres, Acueducto, ConfirCerti, ValorMatricula, OrdenesSuspencion, OrdenesReconexion, Poblacion, Factura, Ciclo, EstadoCuenta,NovedadVivienda
from SAAL.models import Vivienda, SolicitudGastos, ArchivosAcueducto, Propietario, NovedadesSistema,Medidores, Pqrs, RespuestasPqrs,NovedadesGenerales, CobroMatricula, Permisos, Pagos, Archivos, AsignacionExterna
from SAAL.forms import RegistroUsuario, RegistroUsuario2, RegistroVivienda,AcueductoAForm,PermisosForm, CertificarForm, CobroMatriculaForm, CostoMForm, RespuestPqrForm, RegistroPropietario, TarifasForm , ModificaPropietario
from SAAL.forms import CambioFormEstado,AcueductoForm, GastosForm, MedidoresForm, PoblacionForm, ModificaVivienda
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

# Reemplaza estos valores con tus credenciales de Google Mail
username = 'sistemas.acueducto.caimalito@gmail.com'
#Tiempos de facturacion
DIASFACTURACION = 10
DIASPARASUSPENCION = 15
#permisos
CT = 'AC'
#TARIFA
TARIFA = 8000
#------------
EF= 'Emitida'
EPC = 'Se registro propietario'
EPM = 'Se modifico propietario'
DESC = 'Null'
ECV = 'Se registro vivienda'
EMV = 'Se modifico vivienda'
#Tipo novedades
DES = 'Descuento'
ADI = 'Adicion'
#estados suspenciones
SA = 'Anulada'
SP = 'Pendiente'
SJ = 'Ejecutada'
TARIFASUSPENCION = 14000
#estados ciclos
EC = 'SIN PAGAR'
EC2 = 'PAGO'
EC3 = 'ANULADA'
#EstadosFacturas
FE = 'Emitida'
FV = 'Vencida'
FP = 'Paga'
FA = 'Anulada'
#Estadoscuentasdecobro
Estadocue = 'Mantenimiento'
#otros
REPORTESUSPEN = 'Suspedido'
#sectores
S1 = 'Pasonivel Viejo'
S2 = 'Pasonivel Destapada'
S3 = 'Caimalito Centro'
S4 = 'Barrio Nuevo'
S5 = '20 de julio'
#ESTADOS PRERIOS
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
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            form = self.form_class(instance=acueducto)
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            novedades = NovedadesSistema.objects.all().order_by("-IdNovedad")[:5]
            return render(request,
                          self.template_name,
                            {
                            'tipousuario': tipousuario,
                            'nombreproyecto':nombreproyecto,
                            'nombreproyectol': nombreproyectol,
                            'acueducto': nombreacueducto,
                            'notificaciones': contadorpen,
                            'versionp': versionp,
                            'listapqrs': listapqrs,
                            'totalnoti': totalnoti,
                            'novedades': novedades
                            })
        except Acueducto.DoesNotExist:
            return render(request, "pages-404.html")
    def post(self, request):
        try:
            facturas = Factura.objects.filter(Estado='Emitida')
            cont = 0
            for i in facturas:
                idfactura = i.IdFactura
                consul = Pagos.objects.filter(IdFactura=idfactura).exists()
                if consul is True:
                    pago = Pagos.objects.get(IdFactura=idfactura)
                    idvivienda = pago.IdVivienda.pk
                    estadocuenta = EstadoCuenta.objects.get(IdVivienda=idvivienda)
                    factura = Factura.objects.get(IdFactura=idfactura)
                    factura.IdEstadoCuenta = str(estadocuenta.pk)
                    factura.save()
                    cont +=1

            if cont >=1:
                messages.add_message(request, messages.INFO,cont)
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, 'Error')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Pagos.DoesNotExist:
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
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
        except Acueducto.DoesNotExist:
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
                return render(request, self.template_name,
                            {
                                'usuarios': usuarios,
                                'viviendas': listavivienda,
                                'notificaciones': contadorpen,
                                'listapqrs': listapqrs,
                                'totalnoti': totalnoti
                            })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

class AgregarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    form_class = RegistroVivienda
    form_class2 = CobroMatriculaForm
    template_name = 'usuarios/registrovivienda.html'

    def get(self, request):
        try:
            form = self.form_class()
            form2 = self.form_class2()
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AIP').exists()
            if tipousuario is True:
                return render(request, self.template_name,
                              {
                                  'form': form,
                                  'form2': form2,
                                  'notificaciones': contadorpen,
                                  'listapqrs': listapqrs,
                                  'totalnoti': totalnoti

                              })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            idvivienda = request.POST.get("IdVivienda")
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
            idvalor = request.POST.get("IdValor")
            cantcuotas = request.POST.get("CantCuotas")
            fichacatastral = request.POST.get("FichaCastral")
            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            tipousuario = datos.TipoUsuario
            valormatricula = ValorMatricula.objects.get(IdValor=idvalor)
            costo = valormatricula.Valor
            cuota = int(costo) / int(cantcuotas)
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)
            propietario = Propietario.objects.get(IdPropietario=idpropietario)
            validarvi = Vivienda.objects.filter(IdVivienda=idvivienda).exists()
            if validarvi == True:
                messages.add_message(request, messages.ERROR, 'la Vivienda ya existe')
                return HttpResponseRedirect(reverse('usuarios:agregarvivienda'))

            else:
                vivienda = Vivienda(IdVivienda=idvivienda, Direccion=direccion, NumeroCasa=numerocasa, Piso=piso,Ciclo=ciclo,
                                    TipoInstalacion=tipoinstalacion, Estrato=estrato, EstadoServicio=estadoservicio,
                                    IdPropietario=propietario,MatriculaAnt=matricula, InfoInstalacion=infoinstalacion,
                                    ProfAcometida=profacometida,CantHabitantes=canthabitantes,IdAcueducto=acueducto,FichaCastral=fichacatastral, usuid=datos.usuid)
                vivienda.save()
                cobromatricula = CobroMatricula(Descripcion=DESCOBRO,Cuota=int(cuota), IdVivienda=vivienda, Estado=ESTCOBRO, IdValor=valormatricula, CantCuotas=cantcuotas, CuotasPendientes=cantcuotas, ValorPendiente=costo)
                cobromatricula.save()
                certificacion = Certificaciones(Nit=acueducto,NombreEmpresa=acueducto.Nombre, Estado=ESTADOCERTI, IdVivienda=vivienda)
                certificacion.save()
                estadocuenta = EstadoCuenta(Valor=0,IdVivienda=vivienda,Estado=Estadocue,Descripcion=COBROCONSUMO)
                estadocuenta.save()
                messages.add_message(request, messages.INFO, 'la vivienda se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

        except User.DoesNotExist:
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
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except usuario.DoesNotExist:
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
            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            tipousuario = datos.TipoUsuario
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)

            validarpro = Propietario.objects.filter(IdPropietario=idpropietario).exists()
            if validarpro == True:
                messages.add_message(request, messages.ERROR, 'El usuario ya existe')
                return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

            else:
                if int(idpropietario) <= 10000000 and int(idpropietario) >= 9999999999:
                   messages.add_message(request, messages.ERROR, 'El numero de identificacion del propietario no es valido')
                   return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

                else:
                    propietario = Propietario(IdPropietario=idpropietario, Nombres=nombres, Apellidos=apellidos, NoTelefono=notelefono,Email=email,IdPoblacion=poblacion)

                    if propietario is not None:
                        propietario.save()
                        informacion = str(idpropietario + ' ' + nombres + ' ' + apellidos + ' ' + notelefono + ' ' + email + ' ' + str(poblacion))
                        asunto = "se registra titular de servicio"
                        messages.add_message(request, messages.INFO, 'el propietario se agrego correctamente')
                        return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

                    else:
                        messages.add_message(request, messages.ERROR, 'El propietario no se pudo agregar')
                        return HttpResponseRedirect(reverse('usuarios:agregarpropietario'))

        except User.DoesNotExist:
            return render(request, "pages-404.html")

class ModificarPropietario(LoginRequiredMixin, View):
    login_url = '/'
    form_class = ModificaPropietario
    template_name = 'usuarios/modificarpropietario.html'

    def get(self, request, IdPropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=IdPropietario)
            form = self.form_class(instance=datospropietario)
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACMT').exists()
            if tipousuario is False:
                return render(request, self.template_name,{'form': form})
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdPropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=IdPropietario)
            form = self.form_class(request.user, request.POST, instance=datospropietario)

            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=dr.pk)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'la informacion del propietario se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:listapropietarios'))

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

class ModificarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    form_class = ModificaVivienda
    template_name = 'usuarios/modificarvivienda.html'

    def get(self, request, IdVivienda):
        try:
            idvivienda= str(IdVivienda)
            datosvivienda = Vivienda.objects.get(IdVivienda=idvivienda)
            form = self.form_class(instance=datosvivienda)
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACMP').exists()
            if tipousuario is False:
                return render(request, self.template_name,{'form': form, 'matricula': idvivienda})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            datosvivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            form = self.form_class(request.user, request.POST, instance=datosvivienda)
            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'la informacion de la vivienda se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

class VisualizarPropietario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verpropietario.html'

    def get(self, request, IdPropietario):
        try:
            datospropietario = Propietario.objects.get(IdPropietario=IdPropietario)
            viviendas = Vivienda.objects.filter(IdPropietario=IdPropietario)
            return render(request, self.template_name,
                          {
                              'viviendas':viviendas,
                              'IdPropietario': datospropietario.IdPropietario,
                              'Nombres': datospropietario.Nombres,
                              'Apellidos': datospropietario.Apellidos,
                              'NoTelefono': datospropietario.NoTelefono,
                              'Email': datospropietario.Email,
                              'IdPoblacion': datospropietario.IdPoblacion
                          })

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

class VisualizarVivienda(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/vervivienda.html'

    def get(self, request, IdVivienda):
        try:
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            viviendainfo = Vivienda.objects.filter(IdVivienda=IdVivienda)
            estados = EstadoCuenta.objects.filter(IdVivienda=IdVivienda)
            pagosrys = PagoOrdenes.objects.filter(IdVivienda=IdVivienda)
            cobromatricula = CobroMatricula.objects.filter(IdVivienda=IdVivienda, Estado=ESTCOBRO)
            pagos = Pagos.objects.filter(IdVivienda=IdVivienda)
            filtropagos = Pagos.objects.filter(IdVivienda=IdVivienda).order_by("-IdPago")[:1]
            fecha = datetime.today()
            verificarestado = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
            idestado = verificarestado.IdEstadoCuenta
            ordenesrs = CobroOrdenes.objects.filter(IdEstadoCuenta=idestado)
            resultado = verificarestado.Valor
            facturas = Factura.objects.filter(IdEstadoCuenta=idestado).order_by("-IdFactura")
            facturasemi = Factura.objects.filter(IdEstadoCuenta=idestado, Estado=FE)
            vafacemi = Factura.objects.filter(IdEstadoCuenta=idestado, Estado=FE).exists()
            matriculas = CobroMatricula.objects.filter(IdVivienda=IdVivienda)
            certificaciones = Certificaciones.objects.filter(IdVivienda=IdVivienda)
            medidores = Medidores.objects.filter(IdVivienda=IdVivienda)
            novedades = NovedadVivienda.objects.filter(IdVivienda=IdVivienda)
            reconexion = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestado)
            suspenciones = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestado)
            archivos = Archivos.objects.filter(IdVivienda=IdVivienda)
            contadorarchivos = Archivos.objects.filter(IdVivienda=IdVivienda).count()
            ordenessuspencion = CobroOrdenes.objects.filter(IdEstadoCuenta=idestado,Estado=ESTADO1,TipoOrden='Cobro por suspencion')
            ordenesreconexion = CobroOrdenes.objects.filter(IdEstadoCuenta=idestado, Estado=ESTADO1,TipoOrden='Cobro por reconexión')
            validarcobro = CobroMatricula.objects.filter(IdVivienda=IdVivienda, Estado=ESTCOBRO)
            reparaciones = 0
            matri = 0
            for i in validarcobro:
                valor = i.Cuota
                matri += int(valor)

            cor = 0
            for i in ordenesreconexion:
                valor = i.Valor
                cor += int(valor)

            cos = 0
            for i in ordenessuspencion:
                valor = i.Valor
                cos += int(valor)

            lista = []
            for k in facturas:
                idenfactura = k.IdFactura
                pago = Pagos.objects.filter(IdFactura=idenfactura).exists()
                if pago is True:
                    lista.append(idenfactura)

            print(lista)

            return render(request, self.template_name,{
                'lista':lista,'facturas': facturas,'cobromatricula': cobromatricula,'archivos': archivos,'contarchivos': contadorarchivos,'suspenciones': suspenciones,
                'reconexion': reconexion,'facturasemi': facturasemi,'medidores':medidores,'matriculas': matriculas,'certificaciones': certificaciones,
                'direccion': vivienda.Direccion,'casa' : vivienda.NumeroCasa,'piso': vivienda.Piso,'matricula': vivienda.IdVivienda,'tipo': vivienda.TipoInstalacion,
                'estrato': vivienda.Estrato,'estado': vivienda.EstadoServicio,'propietario': vivienda.IdPropietario,'fichacatastral': vivienda.FichaCastral,
                'estados': estados,'pagos':pagos,'fecha': fecha,'novedades':novedades,'ultimopago': filtropagos,'vafacemi': vafacemi,
                'viviendainfo': viviendainfo,'ordenesrs': ordenesrs,'pagosrys': pagosrys,
                'reconexion2': cor,'suspenciones2': cos,'aportes': resultado,'cobromatricula1':matri,'repaciones': reparaciones,
                'total': resultado + cor + cos + matri + reparaciones
            })

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class Facturacion(LoginRequiredMixin, View):
   login_url = '/'
   template_name = 'usuarios/facturacion.html'

   def get(self, request):
       try:
           listapqrs = Pqrs.objects.filter(Estado='Pendiente')
           contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
           contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
           totalnoti = contqrs + contsoli
           contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
           #operaciones de conteo
           es= EstadoCuenta.objects.all()
           operativos = EstadoCuenta.objects.filter(Estado='Operativo').count()
           mantenimiento = EstadoCuenta.objects.filter(Estado='Mantenimiento').count()
           retirados = EstadoCuenta.objects.filter(Estado='Retirado').count()
           suspendidos = EstadoCuenta.objects.filter(Estado='Suspendido').count()

           #operaciones de suma
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
           tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ACC').exists()
           if tipousuario is True:
               return render(request, self.template_name,
                             {
                                 'operativos': int(operativos), 'mantenimiento': int(mantenimiento), 'retirados': int(retirados),'suspendidos': int(suspendidos),
                                 'contoperativos': contoperativos,'contretirados':contretirado,'contmantenimiento': contmantenimiento,'contsuspendidos': contsuspendido,'totalcuentascobro': totalcuentas,
                                 'totalvalores':contoperativos + contmantenimiento + contretirado + contsuspendido,'notificaciones': contadorpen,
                                 'listapqrs': listapqrs,
                                 'totalnoti': totalnoti
                             })
           else:
               messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

       except Usuario.DoesNotExist:
           return render(request, "pages-404.html")

   def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            #Fechas
            ye = datetime.now()
            ano = ye.year
            # consultafacturasconestados"emitida"
            facturas = Factura.objects.filter(Estado=FE).count()
            #Consultadetarifaeusuario
            usuarios = Usuario.objects.get(usuid=request.user.pk)
            acueducto = usuarios.IdAcueducto
            acueductos = Acueducto.objects.get(IdAcueducto=acueducto)
            idtarifa = acueductos.IdTarifa
            tarifa1 = Tarifa.objects.get(IdTarifa=idtarifa)
            tarifaoperativos = tarifa1.Valor
            tarifamantenimiento = tarifa1.Mantenimiento
            operativos = EstadoCuenta.objects.filter(Estado='Operativo')
            mantenimientos = EstadoCuenta.objects.filter(Estado='Mantenimiento')
            estados = EstadoCuenta.objects.all()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ACC').exists()
            if tipousuario is True:
                if facturas >=1:
                    messages.add_message(request, messages.ERROR, 'No se puede generar cobros, hay facturacion con estado *emitida*', ano)
                    return HttpResponseRedirect(reverse('usuarios:facturacion'))

                else:
                    cont = 0
                    for k in estados:
                        if k.Estado == 'Operativo':
                            estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=k.pk)
                            estadoscu.Valor += int(tarifaoperativos)
                            estadoscu.save()
                            cont +=1
                        elif k.Estado == 'Mantenimiento':
                            estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=k.pk)
                            estadoscu.Valor += int(tarifamantenimiento)
                            estadoscu.save()
                            cont += 1
                        else:
                            pass
                    messages.add_message(request, messages.SUCCESS, 'Se generaron ',cont,' cobros')
                    return HttpResponseRedirect(reverse('usuarios:facturacion'))

            else:
               messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Acueducto.DoesNotExist:
            return render(request, "pages-404.html")

class Reporte(LoginRequiredMixin, View):
   login_url = '/'
   template_name = 'usuarios/reporte.html'

   def get(self, request):
       try:
           usuario = Usuario.objects.get(usuid=request.user.pk)
           concesion = open('static/serial/Consecion.txt', 'r')
           concesionv = concesion.read()
           poblacion = open('static/serial/Poblacion.txt', 'r')
           poblacion = poblacion.read()
           viviendas = Vivienda.objects.all().count()
           viviendasopera = Vivienda.objects.filter(EstadoServicio=E1).count()
           disponible = int(concesionv) - viviendasopera
           porcentaje = viviendas * 100 / int(concesionv)
           viviendasc = Vivienda.objects.all()
           personas = 0
           for i in viviendasc:
               valor = int(i.CantHabitantes)
               personas += valor

           estadoscuenta2 = EstadoCuenta.objects.all()
           valorcuentas = 0
           for i in estadoscuenta2:
               valor = int(i.Valor)
               valorcuentas += valor

           porcentajepoblacion = personas * 100 / int(poblacion)
           propietarios = Propietario.objects.all().count()

           #presupuesto anual
           s1 = Vivienda.objects.filter(Direccion=S1).count()
           s2 = Vivienda.objects.filter(Direccion=S2).count()
           s3 = Vivienda.objects.filter(Direccion=S3).count()
           s4 = Vivienda.objects.filter(Direccion=S4).count()
           s5 = Vivienda.objects.filter(Direccion=S5).count()
           e1 = Vivienda.objects.filter(EstadoServicio=E1).count()
           e2 = Vivienda.objects.filter(EstadoServicio=E2).count()
           e3 = Vivienda.objects.filter(EstadoServicio=E3).count()
           e4 = Vivienda.objects.filter(EstadoServicio='Mantenimiento').count()
           c1 = Vivienda.objects.filter(Ciclo=C1).count()
           c2 = Vivienda.objects.filter(Ciclo=C2).count()
           c3 = Vivienda.objects.filter(Ciclo=C3).count()
           c4 = Vivienda.objects.filter(Ciclo=C4).count()
           t1 = Vivienda.objects.filter(TipoInstalacion=T1).count()
           t2 = Vivienda.objects.filter(TipoInstalacion=T2).count()
           t3 = Vivienda.objects.filter(TipoInstalacion=T3).count()
           enpagar = EstadoCuenta.objects.filter(Estado=EC).count()
           pagos = EstadoCuenta.objects.filter(Estado='PAGO').count()
           totalcantp = enpagar + pagos

           ciclos = EstadoCuenta.objects.filter(Estado=EC)
           ciclos2 = EstadoCuenta.objects.filter(Estado=EC2)

           valor2 =0
           for ciclo in ciclos2:
               valor2 += ciclo.Valor

           valor = 0
           for ciclo in ciclos:
               valor += ciclo.Valor

           totalv = 0
           if valor and valor2 is not None:
                totalv= valor + valor2

           listapqrs = Pqrs.objects.filter(Estado='Pendiente')
           contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
           contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
           totalnoti = contqrs + contsoli
           contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

           tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AR').exists()
           if tipousuario is True:
               return render(request, self.template_name,{
                   'totalpropietarios': propietarios,
                   'totalviviendas': viviendas,
                   's1': s1 + s2, 's3': s3,
                   's4': s4, 's5': s5, 'e1': e1,
                   'e2': e2, 'e3': e3, 'e4': e4,
                   'c1': c1, 'c2': c2, 'c3': c3,
                   'c4': c4, 't1': t1, 't2': t2, 'notificaciones': contadorpen,
                   'listapqrs': listapqrs, 'totalnoti': totalnoti, 'porpoblacion': int(porcentajepoblacion),
                   't3': t3, 'enpagar': enpagar,'personas': personas, 'porcentaje': int(porcentaje),'poblacion':poblacion,
                   'pagos': pagos, 'totalcantp': totalcantp,'concesion': concesionv,
                   'valor': valor,'valorcuentas':valorcuentas, 'valor2':valor2, 'totalvc': totalv,'suscriptores': viviendasopera, 'disponible': disponible
               })
           else:
               messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

       except Usuario.DoesNotExist:
            return render(request, "pages-404.html")


class Reportepdfpropi(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
        propietarios = Propietario.objects.all()
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de titulares"
        ws['A1'] = 'IdPropietario'
        ws['B1'] = 'Nombres'
        ws['C1'] = 'Apellidos'
        ws['D1'] = 'NoTelefono'
        ws['E1'] = 'Email'
        ws['F1'] = 'TipoPoblacion'

        cont = 2

        for propietario in propietarios:
            ws.cell(row=cont, column=1).value = propietario.IdPropietario
            ws.cell(row=cont, column=2).value = propietario.Nombres
            ws.cell(row=cont, column=3).value = propietario.Apellidos
            ws.cell(row=cont, column=4).value = propietario.NoTelefono
            ws.cell(row=cont, column=5).value = propietario.Email
            ws.cell(row=cont, column=6).value = str(propietario.IdPoblacion)

            cont+=1

        archivo_propi = "ReporteTitulares" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type= "application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_propi)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class ReportePredios(LoginRequiredMixin, View):
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

        cont = 2

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

        archivo_predios = "ReportePredios" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class BancoArchivos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/banco.html'

    def get(self, request):
        try:
            elementos = os.listdir("media/Archivos/")
            archivos= ArchivosAcueducto.objects.all()

            return render(request, self.template_name,{
                'elementos': archivos
            })

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        idpropietario = request.POST.get("idpropietario")
        nombrearchivo = request.POST.get("nombre")
        archivo = request.FILES.get("file")
        propi = Propietario.objects.get(IdPropietario=idpropietario)
        propietario = Propietario.objects.filter(IdPropietario=idpropietario).exists()
        if propietario is True:
            archivo = Archivos(IdPropietario=propi, NombreArchivo=nombrearchivo, Archivo=archivo)
            archivo.save()
            messages.add_message(request, messages.INFO, 'El archivo se subio correspondientes')
            return HttpResponseRedirect(reverse('usuarios:banco'))

        else:
            messages.add_message(request, messages.ERROR, 'El archivo No se subio correspondientes')
            return HttpResponseRedirect(reverse('usuarios:banco'))

class ReporteSuspendido(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        try:
            sectores = Vivienda.objects.filter(EstadoServicio=REPORTESUSPEN)
            sfecha = (datetime.today())
            wb = Workbook()
            ws = wb.active
            ws.title ="Reporte predios suspendidos"
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

            cont = 2

            for vivienda in sectores:
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

            archivo_predios = "ReporteSuspendidos" + str(sfecha) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ReportesVarios(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request,*args, **kwargs):
        try:
            sector = request.GET.get("sector")
            centro = str(sector)
            viviendas = Vivienda.objects.filter(Direccion=centro)
            wb = Workbook()
            ws = wb.active
            sfecha = (datetime.today())
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

            cont = 2

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

            archivo_predios = "Reporte"+ str(sector) + str(sfecha) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ReportesEstado(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
        try:
            sector = request.GET.get("estado")
            centro = str(sector)
            viviendas = Vivienda.objects.filter(EstadoServicio=centro)
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

            archivo_predios = "ReportePredios.xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ReportesCiclo(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
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

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ReportesInfoinstal(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
        try:
            sector = request.GET.get("infoinstal")
            centro = str(sector)
            viviendas = Vivienda.objects.filter(TipoInstalacion=centro)
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

            archivo_predios = "ReportePorTipoInstalacion.xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except Vivienda.DoesNotExist:
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
                return render(request, self.template_name,{
                    'notificaciones': contadorpen,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti
                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipo = request.POST.get("tipo")
            identificacion = request.POST.get("identificacion")

            if tipo == "Cedula de ciudadania" and identificacion is not None:
                titular = Propietario.objects.filter(IdPropietario=identificacion).exists()
                if titular is True:
                    IdPropietario = identificacion
                    ver = self.propietario()
                    ejercutar = ver.get(request,IdPropietario)
                    return ejercutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del titular no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            elif tipo == "Numero de matricula" and identificacion is not None:
                predio = Vivienda.objects.filter(IdVivienda=identificacion).exists()
                if predio is True:
                    IdVivienda = identificacion
                    ver = self.predio()
                    ejecutar = ver.get(request, IdVivienda)
                    return ejecutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del predio no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            elif tipo == "Referencia" and identificacion is not None:
                estadocuenta = EstadoCuenta.objects.filter(IdEstadoCuenta=identificacion).exists()
                if estadocuenta is True:
                    estadocuentas = EstadoCuenta.objects.get(IdEstadoCuenta=identificacion)
                    IdVivienda = estadocuentas.IdVivienda.pk
                    ver = self.predio()
                    ejecutar = ver.get(request, IdVivienda)
                    return ejecutar

                else:
                    messages.add_message(request, messages.ERROR, 'Informacion del predio no encontrada')
                    return HttpResponseRedirect(reverse('usuarios:busquedas'))

            else:
                messages.add_message(request, messages.WARNING, 'Informacion incompleta')
                return HttpResponseRedirect(reverse('usuarios:busquedas'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class Certificacion(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        certificaciones = Certificaciones.objects.all()
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de certificaciones"
        ws['A1'] = 'IdCertificacion'
        ws['B1'] = 'Nit'
        ws['C1'] = 'NombreEmpresa'
        ws['D1'] = 'Estado'
        ws['E1'] = 'Soporte'
        ws['F1'] = 'Descripcion'
        ws['G1'] = 'IdVivienda'

        cont = 2

        for propietario in certificaciones:
            ws.cell(row=cont, column=1).value = propietario.IdCertificacion
            ws.cell(row=cont, column=2).value = propietario.Nit
            ws.cell(row=cont, column=3).value = propietario.NombreEmpresa
            ws.cell(row=cont, column=4).value = propietario.Estado
            ws.cell(row=cont, column=5).value = propietario.Soporte
            ws.cell(row=cont, column=6).value = propietario.Descripcion
            ws.cell(row=cont, column=7).value = str(propietario.IdVivienda)

            cont += 1

        sfecha = (datetime.today())
        archivo_propi = "ReporteCertificaciones" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_propi)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class Lmedidores(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        medidores = Medidores.objects.all()
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de certificaciones"
        ws['A1'] = 'IdMedidor'
        ws['B1'] = 'Marca'
        ws['C1'] = 'Tipo'
        ws['D1'] = 'LeturaInicial'
        ws['E1'] = 'AnoFabricacion'
        ws['F1'] = 'IdVivienda'

        cont = 2

        for propietario in medidores:
            ws.cell(row=cont, column=1).value = propietario.IdMedidor
            ws.cell(row=cont, column=2).value = propietario.Marca
            ws.cell(row=cont, column=3).value = propietario.Tipo
            ws.cell(row=cont, column=4).value = propietario.LecturaInicial
            ws.cell(row=cont, column=5).value = propietario.AnoFabricacion
            ws.cell(row=cont, column=6).value = str(propietario.IdVivienda)

            cont += 1

        sfecha = (datetime.today())
        archivo_propi = "ReporteMedidores" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_propi)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class ReporteCiclo(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
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
                estadocuenta = EstadoCuenta.objects.filter(Estado=tipo,ano=ano)
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

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ControlPresupuestal(LoginRequiredMixin, View):
    login_url = '/'
    form_class = GastosForm
    template_name = 'usuarios/gastos.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen1 = SolicitudGastos.objects.filter(Estado=ESTADO1)

            usuario = Usuario.objects.get(usuid=request.user.pk)
            solicitudesgastos = SolicitudGastos.objects.filter(Estado=ESTADO1)
            asignacionextera = AsignacionExterna.objects.all()
            form = self.form_class()
            contador = SolicitudGastos.objects.all().count()
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            contadorapro = SolicitudGastos.objects.filter(Estado=ESTADO2).count()
            contadoranu = SolicitudGastos.objects.filter(Estado=ESTADO3).count()
            contadorasig = AsignacionExterna.objects.all().count()
            sumaasigexter = AsignacionExterna.objects.all()
            aprobado = SolicitudGastos.objects.filter(Estado=ESTADO2)
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

            suma1 = 0
            for i in sumaasigexter:
                suma1 += int(i.Valor)

            suma2 = 0
            for i in aprobado:
                valor = int(i.Valor)
                suma2 += valor

            totalingresos = pago + suma1
            gastos = int(suma2)
            presupuesto = totalingresos - gastos
            #mensualidades:
            fechaexp = (datetime.today())
            ciclo = fechaexp.month
            ano1 = fechaexp.year
            #Los argumentos serán: Año, Mes, Día, Hora, Minutos, Segundos, Milisegundos.
            new_date = datetime(ano1, ciclo, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano1, ciclo, 30, 23, 59, 59, 00000)
            pagos2 = Pagos.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            pagosrys = PagoOrdenes.objects.filter(FechaPago__gte=new_date, FechaPago__lte=new_date2).all()
            gastosaprobados = SolicitudGastos.objects.filter(Fecha__gte=new_date,Fecha__lte=new_date2, Estado=ESTADO2).all()
            rys=0
            for i in pagosrys:
                valor = int(i.Valor)
                rys += valor

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
                    'asignacionexterna': asignacionextera,
                    'contador': contador,
                    'contadorp': contadorpen,
                    'contadora': contadorapro,
                    'contadoranu': contadoranu,
                    'contadorasig': contadorasig,
                    'gastos': gastos,
                    'pago': int(totalingresos),
                    'presupuesto': presupuesto,
                    'ingresomensual': pago0,
                    'gastosmensuales': gasto4,
                    'notificaciones': contadorpen1,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti,
                    'rys': rys
                })
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))


        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")



class GenerarGasto(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/generargasto.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            usuario = Usuario.objects.get(usuid=request.user.pk)
            return render(request, self.template_name, {
                'notificaciones': contadorpen,
                'listapqrs': listapqrs,
                'totalnoti': totalnoti
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            area = request.POST.get("areaencargada", "")
            tiposolicitud = request.POST.get("tiposolicitud", "")
            valor = request.POST.get("valor", "")
            numerofactura = request.POST.get("NumeroFactura", "")
            descripcion = request.POST.get("descripcion", "")
            usuario = Usuario.objects.get(usuid=request.user.pk)

            if area and numerofactura and tiposolicitud and valor and descripcion is not None:
                solicitud = SolicitudGastos(IdUsuario=usuario, Descripcion=descripcion,
                                            TipoSolicitud=tiposolicitud, Valor=valor,
                                            Estado=ESTADO1, AreaResponsable=area, NumeroFactura=numerofactura)
                solicitud.save()
                messages.add_message(request, messages.INFO, 'la solicitud se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.ERROR, 'Informacion incompleta')
                return HttpResponseRedirect(reverse('usuarios:generargasto'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class IngresoExterno(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/ingresoexterno.html'

    def get(self, request):
        try:
            return render(request, self.template_name)

        except LoginRequiredMixin.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            valor = request.POST.get("valor", "")
            descripcion = request.POST.get("descripcion", "")
            soporte = request.FILES.get("soporte", "")
            usuario = Usuario.objects.get(usuid=request.user.pk)

            if valor and descripcion is not None:
                externos = AsignacionExterna(Valor=valor, Descripcion=descripcion, Soporte=soporte, usuid=usuario)
                externos.save()
                messages.add_message(request, messages.INFO, 'Asignacion exitosa')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.WARNING, 'Informacion incompleta')
                return HttpResponseRedirect(reverse('usuarios:ingresoexterno'))

        except LoginRequiredMixin.DoesNotExist:
            return render(request, "pages-404.html")

class BuscarSolicitud(LoginRequiredMixin, View):
    login_url = '/'
    form_class = GastosForm
    template_name = 'usuarios/modificarestado.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            IdSolicitud = request.GET.get("IdSolicitud", "")
            solicitud = SolicitudGastos.objects.get(IdSoGa=IdSolicitud)
            form = self.form_class(instance=solicitud)
            return render(request, self.template_name,
                          {
                              'form': form,
                              'usuario': solicitud.IdUsuario,
                              'estado': solicitud.Estado,
                              'tipo': solicitud.TipoSolicitud,
                              'valor': solicitud.Valor,
                              'area': solicitud.AreaResponsable,
                              'numerofactura': solicitud.NumeroFactura,
                              'fecha': solicitud.Fecha,
                              'descripcion': solicitud.Descripcion,
                              'IdSoGa': solicitud.IdSoGa,
                              'notificaciones': contadorpen,
                              'listapqrs': listapqrs,
                              'totalnoti': totalnoti
                          })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            IdSolicitud = request.POST.get("IdSolicitud", "")
            solicitud = SolicitudGastos.objects.get(IdSoGa=IdSolicitud)
            form = self.form_class(request.user, request.POST, instance=solicitud)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'el estado se cambio correctamente')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar el estado')
                return HttpResponseRedirect(reverse('usuarios:controlpresupuestal'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ListasGastos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listasgastos.html'

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            solicitudesgastos = SolicitudGastos.objects.all()
            asignacionextera = AsignacionExterna.objects.all()
            cierre = Cierres.objects.all()
            contador = SolicitudGastos.objects.all().count()
            contadorasig = AsignacionExterna.objects.all().count()
            contcierre = Cierres.objects.all().count()

            return render(request, self.template_name, {
                'solicitudesgastos': solicitudesgastos,
                'asignacionexterna': asignacionextera,
                'contador': contador,
                'contadorasig': contadorasig,
                'cierres': cierre,
                'contcierre': contcierre,
                'notificaciones': contadorpen,
                'listapqrs': listapqrs,
                'totalnoti': totalnoti
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class InfoVivienda(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/infovivienda.html'

    def get(self, request, IdVivienda):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            vivienda = Vivienda.objects.filter(IdVivienda=IdVivienda)
            certificacion = Certificaciones.objects.filter(IdVivienda=IdVivienda)
            medidores = Medidores.objects.filter(IdVivienda=IdVivienda)
            return render(request, self.template_name, {
                'viviendas': vivienda,
                'certificaciones': certificacion,
                'medidores': medidores
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class RegistroMedidor(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registromedidor.html'
    form_class = MedidoresForm
    vervivienda = VisualizarVivienda

    def get(self, request, IdVivienda):
        try:

            matricula = Vivienda.objects.get(IdVivienda=IdVivienda)
            form = self.form_class(instance=matricula)
            return render(request, self.template_name, {
                'form': form,
                'matricula': matricula
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            idmedidor = request.POST.get("IdMedidor")
            marca = request.POST.get("Marca")
            tipo = request.POST.get("Tipo")
            lectura = request.POST.get("LecturaInicial")
            anof = request.POST.get("AnoFabricacion")

            buscarmedidor = Medidores.objects.filter(IdMedidor=idmedidor).exists()
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idvivienda = vivienda.IdVivienda

            if buscarmedidor is False:
                 registro = Medidores(IdMedidor=idmedidor, Marca=marca, Tipo=tipo, LecturaInicial=lectura, AnoFabricacion=anof,
                                      IdVivienda=vivienda)
                 registro.save()
                 messages.add_message(request, messages.INFO, 'el medidor se asigno correctamente')
                 ver = self.vervivienda()
                 ejercutar = ver.get(request, idvivienda)
                 return ejercutar

            else:
                messages.add_message(request, messages.INFO, 'el medidor ya esta asignado')
                return HttpResponseRedirect(reverse('usuarios:listaviviendas'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class Certificar(LoginRequiredMixin, View):
    login_url = '/'
    template_name = "usuarios/certificar.html"
    form_class = CertificarForm
    vervivienda = VisualizarVivienda

    def get(self, request, IdCertificacion):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            certificado = Certificaciones.objects.get(IdCertificacion=IdCertificacion)
            form = self.form_class(instance=certificado)

            return render(request, self.template_name,{
                'form': form,
                'idcertificacion': certificado.IdCertificacion,
                'nit': certificado.Nit,
                'empresa': certificado.NombreEmpresa,
                'estado': certificado.Estado,
                'soporte': certificado.Soporte,
                'descripcion': certificado.Descripcion,
                'matricula': certificado.IdVivienda
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdCertificacion):
        try:
            certificado1 = Certificaciones.objects.get(IdCertificacion=IdCertificacion)
            form = self.form_class(request.POST, instance=certificado1)
            idvivienda= request.POST.get("IdVivienda")
            usuario = Usuario.objects.get(usuid=request.user.pk)
            if form.is_valid():
                form.save()
                confirmacion = ConfirCerti(IdUsuario=usuario, IdCertificacion=certificado1)
                confirmacion.save()
                messages.add_message(request, messages.INFO, 'El predio se certifico correctamente')
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

            else:
                messages.add_message(request, messages.ERROR, 'El predio se No certifico correctamente')
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

        except User.DoesNotExist:
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
                                  { 'mispermisos': mispermisos,
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

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{
                    'form': form,'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            idpoblacion = request.POST.get("IdPoblacion")
            descripcion = request.POST.get("Descripcion")
            datos = Usuario.objects.get(usuid=request.user.pk)

            verificacion = Poblacion.objects.filter(IdPoblacion=idpoblacion).exists()

            if verificacion is False:
                poblacion = Poblacion(IdPoblacion=idpoblacion, Descripcion=descripcion)
                poblacion.save()
                messages.add_message(request, messages.INFO, 'El tipo de poblacion se creo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'Ese tipo de poblacion ya existe')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class RegistroCostoM(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registrocostomatricula.html'
    form_class = CostoMForm

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
                return render(request, self.template_name,{
                    'form': form, 'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti
                })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            valor = request.POST.get("Valor")

            if valor is not None:
                poblacion = ValorMatricula(Valor=valor)
                poblacion.save()
                datos = Usuario.objects.get(usuid=request.user.pk)
                tipousuario = datos.TipoUsuario
                idpo = poblacion.IdValor
                descripcion = valor
                informacion = 'Identificador: ' + str(idpo) + '  Valor: ' + descripcion
                asunto = "se registra nuevo valor para el cobro de matricula"
                messages.add_message(request, messages.INFO, 'El valor se agrego correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'Debe ingresar un valor al campo')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class RegistroTarifa(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registrotarifa.html'
    form_class = TarifasForm

    def get(self, request):
        try:
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            usuario = Usuario.objects.get(usuid=request.user.pk)
            form = self.form_class()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,{
                    'form': form, 'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti
                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            idtarifa = request.POST.get("IdTarifa")
            valor = request.POST.get("Valor")
            fechainicial = request.POST.get("FechaInicial")
            fechafinal= request.POST.get("FechaFinal")
            ano = request.POST.get("Ano")

            tarifas = Tarifa.objects.filter(IdTarifa=idtarifa).exists

            if tarifas is not None:
                tarifa = Tarifa(IdTarifa=idtarifa, Valor=valor, FechaInicial=fechainicial, FechaFinal=fechafinal, Ano=ano)
                tarifa.save()
                datos = Usuario.objects.get(usuid=request.user.pk)
                tipousuario = datos.TipoUsuario
                idpo = idtarifa
                descripcion = valor
                informacion = 'Identificador: ' + str(idpo) + '  Valor: ' + descripcion + 'Año:' + ano
                asunto = "se registra nuevo valor para el cobro de matricula"
                enviocorre = EnvioCorreo()
                confirmar = enviocorre.get(asunto, informacion, tipousuario)
                messages.add_message(request, messages.INFO, 'la tarifa se registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:perfil', confirmar))

            else:
                messages.add_message(request, messages.ERROR, 'Ya existe una tarifa con esa informacion')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ImprimirTiquet(LoginRequiredMixin):
    login_url = '/'

    def get(self, request, idpago, valorpagar, periododepago, referencia1):
        try:
            impresoras = ConectorV3.obtenerImpresoras()
            print("Las impresoras son:")
            print(impresoras)

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class VerFactura(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verfactura.html'
    imptiquet = ImprimirTiquet
    def get(self, request):
        try:
            numerofactura = request.GET.get("factura")
            usuario = Usuario.objects.get(usuid=request.user.pk)
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
                    return render(request, self.template_name,{
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
                        'pagos':pagos,
                        'ciclo': ciclo
                    })
                else:
                    messages.add_message(request, messages.ERROR, 'El numero de factura ingresado no existe')
                    return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Factura.DoesNotExist:
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
            format = "%Y"
            s = (datetime.today())
            ano = s.strftime(format)
            resta = int(estado.Valor) - int(valorpagar)
            devuelta = int(efectivo) - int(valorpagar)
            s = (datetime.today())
            l = s + timedelta(days=2)
            fecha = l
            if int(valorpagar) >= 2000:
                pago = Pagos(IdFactura=factura, Ano=ano, ValorPago=valorpagar,Descripcion=descripcion, Efectivo=efectivo, Devuelta=devuelta,
                                 IdUsuario=usuario, IdVivienda=idvivienda)
                pago.save()
                idpago = pago.IdPago
                estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=idestado.pk)
                estadoscu.Valor = resta
                estadoscu.save()
                cambiofactura = Factura.objects.get(IdFactura=numerofactura)
                cambiofactura.Estado = FP
                cambiofactura.save()
                periododepago = cambiofactura.IdCiclo
                referencia1 = estado.IdVivienda
                #tiquet2 = self.imptiquet()
                #ejecutar = tiquet2.get(request, idpago, valorpagar, periododepago, referencia1)
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

                messages.add_message(request, messages.INFO, 'Se registro el pago correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.INFO, 'el valor a pagar debe ser superior a $7000')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Factura.DoesNotExist:
            return render(request, "pages-404.html")

class RegistroPqr(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/registropqrs.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACFA').exists()
            if tipousuario is False:
                return render(request, self.template_name)
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))


        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            identificacion = request.POST.get("identificacion")
            nombrecompleto = request.POST.get("nombrecompleto")
            celular = request.POST.get("celular")
            email = request.POST.get("email")
            direccion = request.POST.get("direccion")
            tiposolicitud = request.POST.get("tiposolicitud")
            anonimo = request.POST.get("anonimo")
            soporte = request.FILES.get("soporte")
            descripcion = request.POST.get("descripcion")
            usuario = Usuario.objects.get(usuid=request.user.pk)

            if anonimo == "Si":
                pqr = Pqrs(Descripcion=descripcion,Estado=ESTADOPQR1,TipoSolicitud=tiposolicitud,Anonimo=anonimo,usuid=usuario,Correo=email)
                pqr.save()
                idpqr = pqr.IdPqrs
                messages.add_message(request, messages.INFO, 'la pqrs se registro correctamente, RADICADO No:' + str(idpqr))
                return HttpResponseRedirect(reverse('usuarios:listapqrs'))

            elif anonimo == "No":
                estado = Pqrs(Descripcion=descripcion,Soporte=soporte,CedulaNit=identificacion,
                              Estado=ESTADOPQR1,NombreCompleto=nombrecompleto,TipoSolicitud=tiposolicitud,
                              Telefono=celular, Anonimo=anonimo, Direccion=direccion, usuid=usuario,
                              Correo=email)
                estado.save()
                idpqr = estado.IdPqrs
                messages.add_message(request, messages.INFO, 'la tarifa se registro correctamente, RADICADO No:' + str(idpqr))
                return HttpResponseRedirect(reverse('usuarios:listapqrs'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ListaPqrs(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listapqrs.html'

    def get(self, request):
        try:
            lista = Pqrs.objects.filter(Estado='Pendiente')
            contcerrada = Pqrs.objects.filter(Estado='Cerrada').count()
            contpendiente = Pqrs.objects.filter(Estado='Pendiente').count()
            contpeticion = Pqrs.objects.filter(TipoSolicitud='Peticion').count()
            contquejas = Pqrs.objects.filter(TipoSolicitud='Queja').count()
            contsolicitud = Pqrs.objects.filter(TipoSolicitud='Solicitud').count()
            contreclamo = Pqrs.objects.filter(TipoSolicitud='Reclamo').count()
            contfelicitacion = Pqrs.objects.filter(TipoSolicitud='Felicitacion').count()
            usuario = Usuario.objects.get(usuid=request.user.pk)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='APQRS').exists()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            if tipousuario is True:
                return render(request, self.template_name,{
                    'lista': lista,
                    'contp': contpeticion,
                    'contq': contquejas,
                    'conts': contsolicitud,
                    'contr': contreclamo,
                    'contf': contfelicitacion,
                    'contpen': contpendiente,
                    'contcerrada': contcerrada,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti

                })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")
class VerPqr(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verpqr.html'

    def get(self, request):
        try:
            idpqr = request.GET.get("idpqr")
            pqr = Pqrs.objects.filter(IdPqrs=idpqr)
            respuesta = RespuestasPqrs.objects.filter(IdPqrs=idpqr)
            idsolicitud = Pqrs.objects.get(IdPqrs=idpqr)

            return render(request, self.template_name,{
                'pqr': pqr,
                'respuestas': respuesta,
                'idsolicitud': idsolicitud
            })

        except Pqrs.DoesNotExist:
            return render(request, "pages-404.html")

class ListadoPqrs(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listadopqrs.html'

    def get(self, request):
        try:
            listado = Pqrs.objects.all()

            return render(request, self.template_name,{
               'listado': listado
            })

        except Pqrs.DoesNotExist:
            return render(request, "pages-404.html")

class RespuestaPqrs(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/respuestapqr.html'
    form_class = RespuestPqrForm

    def get(self, request, idsolicitud):
        try:
            prq = Pqrs.objects.get(IdPqrs=idsolicitud)
            form = self.form_class(instance=prq)


            return render(request, self.template_name,{
               'form': form
            })

        except Pqrs.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, idsolicitud):
        try:
            idpqr = request.POST.get("idpqr")
            soporte = request.FILES.get("soporte")
            descripcion = request.POST.get("descripcion")
            pqr = Pqrs.objects.get(IdPqrs=idpqr)
            form = self.form_class(request.POST, instance=pqr)

            if idpqr == idsolicitud:
                if form.is_valid():
                    form.save()
                    respuesta = RespuestasPqrs(IdPqrs=pqr, Descripcion=descripcion, Soporte=soporte)
                    respuesta.save()
                    messages.add_message(request, messages.INFO, 'La solicitud se respondio correctamente')
                    return HttpResponseRedirect(reverse('usuarios:listapqrs'))

                else:
                    messages.add_message(request, messages.ERROR, 'No se pudo confirmar el origen del error')
                    return HttpResponseRedirect(reverse('usuarios:listapqrs'))

            else:
                messages.add_message(request, messages.WARNING, 'No se pudo confirmar el numero de radicado')
                return HttpResponseRedirect(reverse('usuarios:listapqrs'))

        except Pqrs.DoesNotExist:
            return render(request, "pages-404.html")

class GenerarCuentas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/respuestapqr.html'
    form_class = RespuestPqrForm

    def get(self, request, idsolicitud):
        try:
            prq = Pqrs.objects.get(IdPqrs=idsolicitud)
            form = self.form_class(instance=prq)


            return render(request, self.template_name,{
               'form': form
            })

        except Pqrs.DoesNotExist:
            return render(request, "pages-404.html")

class Facturas(LoginRequiredMixin, View):
   login_url = '/'
   template_name = 'usuarios/facturas.html'

   def get(self, request):
       try:
           listapqrs = Pqrs.objects.filter(Estado='Pendiente')
           contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
           contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
           totalnoti = contqrs + contsoli
           contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

           datos = Usuario.objects.get(usuid=request.user.pk)
           facturasemi = Factura.objects.filter(Estado=FE).count()
           facturasven = Factura.objects.filter(Estado=FV).count()
           usuario = Usuario.objects.get(usuid=request.user.pk)
           tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AMFV').exists()
           if tipousuario is True:
               return render(request, self.template_name,
                             {
                                 'facturasemi': facturasemi,
                                 'facturasven': facturasven,
                                 'notificaciones': contadorpen,
                                 'listapqrs': listapqrs,
                                 'totalnoti': totalnoti
                             })
           else:
               messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

       except Usuario.DoesNotExist:
           return render(request, "pages-404.html")

   def post(self, request):
        try:
            datos = Usuario.objects.get(usuid=request.user.pk)
            facturas = Factura.objects.filter(Estado=FE)
            verificacion = Factura.objects.filter(Estado=FE).count()
            if verificacion >= 1:
                for factura in facturas:
                    cambio = Factura.objects.get(IdFactura=factura.pk)
                    cambio.Estado = FV
                    cambio.save()
                messages.add_message(request, messages.INFO,'Se cambio el estado de las facturas emitidas a vencidas')
                return HttpResponseRedirect(reverse('usuarios:facturas'))
            else:
                messages.add_message(request, messages.ERROR, 'No hay facturacion emitida')
                return HttpResponseRedirect(reverse('usuarios:facturas'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class GeneradorFacturas(LoginRequiredMixin, View):
   login_url = '/'
   template_name = 'usuarios/generadorfacturas.html'

   def get(self, request):
       try:
           listapqrs = Pqrs.objects.filter(Estado='Pendiente')
           contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
           contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
           totalnoti = contqrs + contsoli
           contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
           usuario = Usuario.objects.get(usuid=request.user.pk)
           facturasven = Factura.objects.filter(Estado=FV).count()
           facturasemi = Factura.objects.all().count()
           facturasemitidas = Factura.objects.filter(Estado=FE)
           facturasemitidas2 = Factura.objects.filter(Estado=FE).count()
           facturaspg = Factura.objects.filter(Estado=FP).count()
           facturasanu = Factura.objects.filter(Estado=FA).count()
           suma = 0
           for i in facturasemitidas:
               valor = int(i.Total)
               suma +=valor

           tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AGF').exists()
           if tipousuario is True:
               return render(request, self.template_name,
                             {   'totalemitidas': facturasemitidas2,
                                 'facturasven': facturasven,
                                 'facturasemi': facturasemi,
                                 'facturaspg': facturaspg,
                                 'facturasanu': facturasanu,
                                 'suma': suma,
                                 'notificaciones': contadorpen,
                                 'listapqrs': listapqrs,
                                 'totalnoti': totalnoti
                             })
           else:
               messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

       except Usuario.DoesNotExist:
           return render(request, "pages-404.html")

   def post(self, request):
       try:
           #consulta de existencias
           usuario = Usuario.objects.get(usuid=request.user.pk)
           estadoscuenta = EstadoCuenta.objects.filter(Estado='Operativo').count()
           facturas = Factura.objects.filter(Estado=FE).count()
           #fechas
           fechaexp = (datetime.today())
           ciclo = fechaexp.month
           ciclos = Ciclo.objects.get(IdCiclo=ciclo)
           mes = ciclos.Nombre
           fechalimite = fechaexp + timedelta(days=DIASFACTURACION)
           estadosoperativos = EstadoCuenta.objects.filter(Estado='Operativo')|EstadoCuenta.objects.filter(Estado='Mantenimiento')|EstadoCuenta.objects.filter(Estado='Suspendido')
           tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='GF').exists()
           if tipousuario is True:
               if facturas >=1:
                   messages.add_message(request, messages.ERROR, 'No se puede generar facturas verifique nuevamente')
                   return HttpResponseRedirect(reverse('usuarios:generadorfacturas'))

               else:
                   if estadoscuenta >=1:
                       for i in estadosoperativos:
                           estadoc = EstadoCuenta.objects.get(IdEstadoCuenta=i.pk)
                           consumo = estadoc.Valor
                           idestadocuenta = estadoc.IdEstadoCuenta

                           #consulta orden suspencion
                           cobrosuspencion2 = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1,TipoOrden='Cobro por suspencion')
                           pos1 = 0
                           for i in cobrosuspencion2:
                               valor = i.Valor
                               pos1 += int(valor)

                           #consulta orden rexonecion
                           cobroreconexiones2 = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1,TipoOrden='Cobro por reconexión')
                           pos2 = 0
                           for i in cobroreconexiones2:
                               valor = i.Valor
                               pos2 += int(valor)

                           #consulta matricula
                           idvivienda = estadoc.IdVivienda
                           conceptoma = CobroMatricula.objects.get(IdVivienda=idvivienda.pk)
                           pendientematricula = conceptoma.IdValor.Valor
                           cuotaspendiente = conceptoma.CuotasPendientes
                           verificacion = CobroMatricula.objects.filter(IdVivienda=idvivienda, Estado='Pendiente')
                           cuotamatricula = 0
                           for i in verificacion:
                               valor = i.Cuota
                               cuotamatricula += int(valor)

                           #consulta vivienda
                           vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
                           propietario = str(vivienda.IdPropietario.Nombres +' '+ vivienda.IdPropietario.Apellidos)
                           estrato = vivienda.Estrato
                           direccion = vivienda.Direccion
                           casa = vivienda.NumeroCasa
                           piso = vivienda.Piso
                           conectado = vivienda.Ciclo
                           estadoservicio = vivienda.EstadoServicio
                           tiposervicio = vivienda.TipoInstalacion
                           #consulta facturas vencidas
                           consumo1 = estadoc.Valor
                           vencidas = -1
                           for i in range(1, consumo1, TARIFA):
                               if i != consumo:
                                   vencidas += 1

                           #ultimo pago
                           autorizacion = 1
                           if autorizacion >= 1:
                               final = int(consumo) + int(pos1) + int(pos2) + int(cuotamatricula)
                               factura = Factura(Matricula=idvivienda,Estado=EF,
                                                 referencia=idestadocuenta,nombretitular=propietario, ciclo=conectado,periodofacturado=mes,Estrato=estrato,direccion=direccion,casa=casa,
                                                 piso=piso,estadoservicio=estadoservicio,tiposerivio=tiposervicio, aporteporconsumo=consumo,conceptomatricula=cuotamatricula,
                                                 cuotasmatricula=cuotaspendiente, reconexion=pos2,suspencion=pos1, facturasvencidas=vencidas,
                                                 FechaExpe=fechaexp, FechaLimite=fechalimite, Total=final,
                                                 IdCiclo=ciclos,
                                                 IdEstadoCuenta=estadoc, TotalConsumo=consumo, OtrosCobros=0)
                               factura.save()
                           else:
                               factura = Factura(Estado=EF, FechaExpe=fechaexp, FechaLimite=fechalimite, Total=consumo,
                                                 IdCiclo=ciclos,
                                                 IdEstadoCuenta=estadoc,TotalConsumo=consumo, OtrosCobros=0)
                               factura.save()

                       messages.add_message(request, messages.INFO, 'Se generaron las facturas correspondientes')
                       return HttpResponseRedirect(reverse('usuarios:generadorfacturas'))
                   else:
                       messages.add_message(request, messages.ERROR, 'No hay estados de cuenta disponibles para generar facturacion')
                       return HttpResponseRedirect(reverse('usuarios:generadorfacturas'))
           else:
               messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permisos de acceso a esta seccion')
               return HttpResponseRedirect(reverse('usuarios:inicio'))

       except Usuario.DoesNotExist:
           return render(request, "pages-404.html")

class Suspenciones(LoginRequiredMixin,View):
    login_url = '/'
    template_name = 'usuarios/generadorsuspenciones.html'
    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            cantanuladas = OrdenesSuspencion.objects.filter(Estado=SA).count()
            cantejecutadas= OrdenesSuspencion.objects.filter(Estado=SJ).count()
            cantpendientes = OrdenesSuspencion.objects.filter(Estado=SP).count()
            ordenessuspenciones = OrdenesSuspencion.objects.filter(Estado=SP)
            ordenesreconexion = OrdenesReconexion.objects.filter(Estado=SP)
            contreeje = OrdenesReconexion.objects.filter(Estado=SJ).count()
            contrepen = OrdenesReconexion.objects.filter(Estado=SP).count()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='ASR').exists()

            if tipousuario is True:
                return render(request, self.template_name,{
                    'anuladas': cantanuladas,
                    'pendientes': cantpendientes,
                    'ejecutadas': cantejecutadas,
                    'ordsus': ordenessuspenciones,
                    'ordrec': ordenesreconexion,
                    'rependientes': contrepen,
                    'reejecutadas': contreeje,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti

                })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            predios = Vivienda.objects.filter(EstadoServicio=E1)
            s = (datetime.today())
            l = s + timedelta(days=DIASPARASUSPENCION)
            fecha = l
            estadoscuenta = EstadoCuenta.objects.filter(Estado='Operativo')|EstadoCuenta.objects.filter(Estado='Mantenimiento')

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
            return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class Reconexiones(LoginRequiredMixin,View):
    login_url = '/'
    template_name = 'usuarios/generadorreconexiones.html'
    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
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
                return render(request, self.template_name,{
                    'ordrec': ordenesreconexion,
                    'rependientes': contrepen,
                    'reejecutadas': contreeje,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti

                })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ListasOrdenes(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listasordenes.html'

    def get(self, request):
        try:
            ordenessuspenciones = OrdenesSuspencion.objects.all()
            ordenesreconexion = OrdenesReconexion.objects.all()
            return render(request, self.template_name,
                          {'ordsus':ordenessuspenciones,
                           'ordrec': ordenesreconexion})

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class VerOrdenSuspencion(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verordensuspencion.html'

    def get(self, request, IdOrden):
        try:
            ordenessuspencion = OrdenesSuspencion.objects.get(IdOrden=IdOrden)
            idorden = ordenessuspencion.IdOrden
            deuda = ordenessuspencion.Deuda
            fechaexpe = ordenessuspencion.FechaExpe
            fechaejecucion = ordenessuspencion.FechaEjecucion
            generado = ordenessuspencion.Generado
            estado = ordenessuspencion.Estado
            usuarioejecuta = ordenessuspencion.UsuarioEjecuta
            referencia = ordenessuspencion.IdEstadoCuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=referencia.pk)
            vivienda = estadocuenta.IdVivienda
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            return render(request, self.template_name,
                          {'idorden': idorden,
                           'deuda': deuda,
                           'fechaexpe':fechaexpe,
                           'fechaejecucion': fechaejecucion,
                           'generado': generado,
                           'estado': estado,
                           'usuarioejecuta': usuarioejecuta,
                           'referencia': referencia,
                           'vivienda': vivienda,
                           'notificaciones': contadorpen,
                           'listapqrs': drilistapqrs,
                           'totalnoti': totalnoti
                           })

        except Usuario.DoesNotExist:
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
            descripcion = 'Cobro por suspención'
            estado = ESTADO1
            format = "%d %m %Y"
            s = (datetime.today())
            fecha = s.strftime(format)
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
                cobroorden = CobroOrdenes(IdEstadoCuenta=idestadocuenta, Estado=estado, Valor=valorsuspencion,IdOrdenT=idorden, TipoOrden=descripcion)
                cobroorden.save()
                messages.add_message(request, messages.INFO, 'La orden se cerro correctamente')
                return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{
                    'notificaciones': contadorpen,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti
                })
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permisos de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Factura.DoesNotExist:
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

        except Factura.DoesNotExist:
            return render(request, "pages-404.html")

class DescargarFactura(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request,IdFactura,*args, **kwargs):
        try:
            #identificador de factura
            factura = Factura.objects.get(IdFactura=IdFactura)
            idestadocuenta = factura.IdEstadoCuenta
            idciclo = factura.IdCiclo
            estadofac = factura.Estado
            valortotal = factura.Total
            total = valortotal
            fechaexpe = factura.FechaExpe
            fechalimite = factura.FechaLimite
            #identificador del ciclo
            ciclo = Ciclo.objects.get(IdCiclo=idciclo.pk)
            nombreciclo = ciclo.Nombre
            #identificador del estado de cuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=idestadocuenta.pk)
            referencia = estadocuenta.IdEstadoCuenta
            matricula = estadocuenta.IdVivienda
            descripcion = estadocuenta.Descripcion
            aporte = estadocuenta.Valor
            valor = estadocuenta.Valor
            consultarpago = Pagos.objects.filter(IdVivienda=matricula).exists()

            valor1 = estadocuenta.Valor - 500
            cont = -1
            for i in range(1, valor1, TARIFA):
                if i != valor1:
                    cont += 1

            #identificador de vivienda
            vivienda = Vivienda.objects.get(IdVivienda=matricula.pk)
            idmatricula = vivienda.IdVivienda
            idtitular = vivienda.IdPropietario
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            piso = vivienda.Piso
            estrato = vivienda.Estrato
            tipoinstalacion = vivienda.TipoInstalacion
            estadoservicio = vivienda.EstadoServicio
            ciclo = vivienda.Ciclo
            #cobromatricula
            cobromatricula = CobroMatricula.objects.filter(IdVivienda=idmatricula, Estado=ESTCOBRO).exists()

            #identificador de propietario
            titular = Propietario.objects.get(IdPropietario=idtitular.pk)
            nombretitular = titular.Nombres
            apellidotitular = titular.Apellidos
            nombrecompleto = nombretitular + ' ' + apellidotitular
            numerofactura = factura.IdFactura
            #suspencion
            suspencion = OrdenesSuspencion.objects.filter(IdEstadoCuenta=referencia, Estado=SP).exists()
            #codigoqr
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=11,
                border=0,
            )
            qr.add_data(numerofactura)
            qr.make(fit=True)

            imga = qr.make_image(fill_color="black", back_color="white")
            imga.save('static/ModeloFactura/output.png')
            #libro excel
            wb = openpyxl.load_workbook('static/ModeloFactura/001-044-78055.xlsx')
            ws = wb.active
            img = openpyxl.drawing.image.Image('static/ModeloFactura/output.png')
            ws.add_image(img, 'AN10')
            if suspencion is True:
                imagen = openpyxl.drawing.image.Image('static/ModeloFactura/corte2.png')
                ws.add_image(imagen, 'B25')

            else:
                pass

            #factura matricula estado
            ws['AW4'] = numerofactura
            ws['AW6'] = idmatricula
            ws['AW8'] = estadofac
            #suscriptor
            ws['A15'] = referencia
            ws['L15'] = nombrecompleto
            ws['A18'] = sector
            ws['O18'] = casa
            ws['T18'] = piso
            ws['AG15'] = estrato
            ws['AB13'] = tipoinstalacion
            ws['R13'] = estadoservicio
            ws['AA15'] = ciclo
            #Periodo facturado
            ws['AM25'] = nombreciclo
            #Conceptos acueducto
            ws['A23'] = descripcion
            ws['K23'] = valor
            ws['AC23'] = valor

            #fechas de procedimiento
            ws['AI56'] = fechaexpe
            if suspencion is True:
                ws['AI58'] = 'Inmediato'
                suspencion2 = OrdenesSuspencion.objects.get(IdEstadoCuenta=referencia, Estado=SP)
                fechasus = suspencion2.FechaEjecucion
                ws['AI60'] = fechasus
            else:
                ws['AI58'] = fechalimite

            if cont <0:
                ws['W55'] = 0
            else:
                ws['W55'] = cont
            #Concepto de matricula
            if cobromatricula is True:
                cobromatri = CobroMatricula.objects.get(IdVivienda=idmatricula)
                descripcionmatri = cobromatri.Descripcion
                cuotaspendientes = cobromatri.CuotasPendientes
                saldopendiente = cobromatri.ValorPendiente
                cuota = cobromatri.Cuota
                ws['A24'] = descripcionmatri
                ws['T24'] = str(cuotaspendientes)
                ws['K24'] = int(saldopendiente)
                ws['AC24'] = int(cuota)

            if consultarpago is True:
                filtropagos = Pagos.objects.filter(IdVivienda=matricula).order_by("-IdPago")[:1]
                consultarp = Pagos.objects.get(IdPago=filtropagos)
                ws['AM39'] = consultarp.IdPago
                ws['AR39'] = consultarp.FechaPago
                ws['AY39'] = int(consultarp.ValorPago)
            else:
                mensaje = "No Registra"
                ws['AM39'] = mensaje
                ws['AR39'] = mensaje
                ws['AY39'] = mensaje

            # cobro suspencion
            cobrosuspencion = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1,TipoOrden='Cobro por suspencion').exists()
            if cobrosuspencion is True:
                cobrosus = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1, TipoOrden='Cobro por suspencion').order_by("-IdOrden")[:1]
                cobrosusp = CobroOrdenes.objects.get(IdOrden=cobrosus)
                descripcions = cobrosusp.TipoOrden
                valor = cobrosusp.Valor
                ws['A25'] = descripcions
                ws['K25'] = int(valor)
                ws['T25'] = 0
                ws['AC25'] = int(valor)

            # cobro reconexion
            cobroreconexion = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1,TipoOrden='Cobro por reconexión').exists()
            if cobroreconexion is True:
                cobrore = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1, TipoOrden='Cobro por reconexión').order_by("-IdOrden")[:1]
                cobrorep = CobroOrdenes.objects.get(IdOrden=cobrore)
                descripcions = cobrorep.TipoOrden
                valor = cobrorep.Valor
                ws['A26'] = descripcions
                ws['K26'] = int(valor)
                ws['T26'] = 0
                ws['AC26'] = int(valor)

            cobrosuspencion2 = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1,TipoOrden='Cobro por suspencion')
            pos1 = 0
            for i in cobrosuspencion2:
                valor = i.Valor
                pos1 += int(valor)

            cobroreconexiones2 = CobroOrdenes.objects.filter(IdEstadoCuenta=idestadocuenta, Estado=ESTADO1, TipoOrden='Cobro por reconexión')
            pos2 = 0
            for i in cobroreconexiones2:
                valor = i.Valor
                pos2 += int(valor)

            cobromatricula2 = CobroMatricula.objects.filter(IdVivienda=idmatricula, Estado=ESTCOBRO)
            matri = 0
            for i in cobromatricula2:
                valor = i.Cuota
                matri += int(valor)

            supremo = int(aporte) + int(pos1) + int(pos2) + int(matri)

            #total a pagar condional 0
            if int(supremo) <=0:
                ws['AU62'] = 0
            else:
                ws['AU62'] = int(supremo)

            ws['AC29'] = int(supremo)
            ws.title = IdFactura
            archivo_predios = "Factura " + str(IdFactura) + ".xlsx"
            response = HttpResponse(content_type="application/ms-excel")
            content = "attachment; filename = {0}".format(archivo_predios)
            response['Content-Disposition'] = content
            wb.save(response)
            return response

        except Factura.DoesNotExist:
            return render(request, "pages-404.html")

class VerOrdenReconexion(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/verordenreconexion.html'

    def get(self, request, IdOrden):
        try:
            ordenesreconexicion= OrdenesReconexion.objects.get(IdOrden=IdOrden)
            idorden = ordenesreconexicion.IdOrden
            deuda = ordenesreconexicion.Deuda
            fechaexpe = ordenesreconexicion.FechaExpe
            fechaejecucion = ordenesreconexicion.FechaEjecucion
            generado = ordenesreconexicion.Generado
            estado = ordenesreconexicion.Estado
            usuarioejecuta = ordenesreconexicion.UsuarioEjecuta
            referencia = ordenesreconexicion.IdEstadoCuenta
            estadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=referencia.pk)
            vivienda = estadocuenta.IdVivienda
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            return render(request, self.template_name,
                          {'idorden': idorden,
                           'deuda': deuda,
                           'fechaexpe':fechaexpe,
                           'fechaejecucion': fechaejecucion,
                           'generado': generado,
                           'estado': estado,
                           'usuarioejecuta': usuarioejecuta,
                           'referencia': referencia,
                           'vivienda': vivienda,
                           'notificaciones': contadorpen,
                           'listapqrs': drilistapqrs,
                           'totalnoti': totalnoti
                           })

        except Usuario.DoesNotExist:
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
            descripcion = 'Cobro por reconexión'
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
                estadoscuenta.Estado = EC
                estadoscuenta.save()
                idvivienda = estadoscuenta.IdVivienda
                vivienda = Vivienda.objects.get(IdVivienda=idvivienda.pk)
                vivienda.EstadoServicio = E1
                vivienda.save()
                cobroorden = CobroOrdenes(IdEstadoCuenta=idestadocuenta, Estado=estado, Valor=valorreconexion,
                                          IdOrdenT=idorden, TipoOrden=descripcion)
                cobroorden.save()
                messages.add_message(request, messages.INFO, 'La orden se cerro correctamente y el predio cambio de estado suspendido a operativo')
                return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except Usuario.DoesNotExist:
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

       except Usuario.DoesNotExist:
           return render(request, "pages-404.html")

   def post(self, request, IdVivienda):
       try:
           fechaexp = (datetime.today())
           ciclo = fechaexp.month
           ciclos = Ciclo.objects.get(IdCiclo=ciclo)
           fechalimite = fechaexp + timedelta(days=DIASFACTURACION)
           usuarios = Usuario.objects.get(usuid=request.user.pk)
           estadoc = EstadoCuenta.objects.get(IdVivienda=IdVivienda)
           total = estadoc.Valor
           facturas = Factura.objects.filter(IdEstadoCuenta=estadoc, Estado=EF).count()
           if facturas >=1:
               messages.add_message(request, messages.WARNING,'Ya existe una factura pendiente de pago')
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
                    factura = Factura(Estado=EF, FechaExpe=fechaexp,FechaLimite=fechalimite,
                                     Total=total,IdCiclo=ciclos,IdEstadoCuenta=estadoc, TotalConsumo=total, OtrosCobros=0)
                    factura.save()
                    messages.add_message(request, messages.INFO,'La factura se creo correctamente')
                    return HttpResponseRedirect(reverse('usuarios:inicio'))

       except EstadoCuenta.DoesNotExist:
           return render(request, "pages-404.html")

class DescargaMasivaFacturas(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listamasivafacturas.html'

    def get(self, request):
        try:
            facturas = Factura.objects.filter(Estado=EF).order_by('IdFactura')
            return render(request, self.template_name,{
                'facturas': facturas
            })

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class SubirArchivos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/subirarchivo.html'
    vervivienda = VisualizarVivienda

    def get(self, request, IdVivienda):
        try:
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            matricula = vivienda.IdVivienda
            return render(request, self.template_name,{
                'matricula': matricula
            })
        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idvivienda= vivienda.IdVivienda
            archivo = request.FILES.get("archivo")
            base = os.path.basename(str(archivo))
            print(base)
            if archivo is not None:
                subir = Archivos(NombreArchivo=base,usuid=usuario, IdVivienda=vivienda, Archivo=archivo, Carpeta=str(idvivienda))
                subir.save()
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

            else:
                messages.add_message(request, messages.ERROR, 'Error al subir el archivo, compruebe nuevamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class EliminarArchivos(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda
    template_name = 'usuarios/eliminararchivos.html'

    def get(self, request, IdArchivo):
        try:
            archivo = Archivos.objects.filter(IdArchivo=IdArchivo)
            none = Archivos.objects.get(IdArchivo=IdArchivo)
            matricula = none.IdVivienda
            return render(request, self.template_name,{
                'matricula': matricula,
                'archivos': archivo
            })
        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdArchivo):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            if usuario is not None:
                archivo = Archivos.objects.get(IdArchivo=IdArchivo)
                archivo.delete()
                messages.add_message(request, messages.INFO, 'El archivo se elimino correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, 'Error al subir el archivo, compruebe nuevamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ReportePdfPagos(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
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

            cont+=1

        archivo_propi = "ReportePagos" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type= "application/ms-excel")
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
            ws.cell(row=cont, column=23).value = (estadocuenta.Valor)
            ws.cell(row=cont, column=24).value = (estadocuenta.Estado)
            ws.cell(row=cont, column=25).value = (estadocuenta.FechaActualizacion)
            ws.cell(row=cont, column=26).value = vivienda.FichaCastral

            cont += 1

        archivo_predios = "ReporteCompleto" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class ReportePagoFechas(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        fechainicial = str(request.GET.get("fechainicial"))
        fechafinal = str(request.GET.get("fechafinal"))
        fecha_ini = datetime.strptime(fechainicial, '%m/%d/%Y')
        fecha_fi = datetime.strptime(fechafinal, '%m/%d/%Y')
        pagos = Pagos.objects.filter(FechaPago__gte=fecha_ini, FechaPago__lte=fecha_fi).all()
        sfecha = (datetime.today())
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte pagos"
        ws['A1'] = 'Referencia pago'
        ws['B1'] = 'Fecha de pago'
        ws['C1'] = 'Numero factura'
        ws['D1'] = 'Año'
        ws['E1'] = 'Valor pago'
        ws['F1'] = 'Efectivo'
        ws['G1'] = 'Cambio'
        ws['H1'] = 'Usuario registro'
        ws['I1'] = 'Matricula'

        cont = 2

        for vivienda in pagos:
            ws.cell(row=cont, column=1).value = vivienda.IdPago
            ws.cell(row=cont, column=2).value = vivienda.FechaPago
            ws.cell(row=cont, column=3).value = str(vivienda.IdFactura)
            ws.cell(row=cont, column=4).value = vivienda.Ano
            ws.cell(row=cont, column=5).value = vivienda.ValorPago
            ws.cell(row=cont, column=6).value = vivienda.Efectivo
            ws.cell(row=cont, column=7).value = vivienda.Devuelta
            ws.cell(row=cont, column=8).value = str(vivienda.IdUsuario)
            ws.cell(row=cont, column=9).value = str(vivienda.IdVivienda)

            cont += 1

        archivo_predios = "ReportePagos" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type="application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_predios)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

class ReporteSuspenciones(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):

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
    def get(self, request):

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

class ReporteCierresAno(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
        ano = request.GET.get("ano")
        pagos2 = Cierres.objects.filter(Ano=ano).exists()
        if pagos2 is False:
            messages.add_message(request, messages.ERROR, 'No existen reportes del año ingresado')
            return HttpResponseRedirect(reverse('usuarios:reporte'))

        else:
            pagos = Cierres.objects.filter(Ano=ano)
            sfecha = (datetime.today())
            wb = Workbook()
            ws = wb.active
            ws.title = "ReporteCierres"
            ws['A1'] = 'Id Cierre'
            ws['B1'] = 'Ingresos'
            ws['C1'] = 'Gastos'
            ws['D1'] = 'Presupuesto'
            ws['E1'] = 'Ciclo'
            ws['F1'] = 'Año'
            ws['G1'] = 'Fecha generacion'
            ws['H1'] = 'Usuario'
            ws['I1'] = '% recaudado'

            cont = 2
            for suspencion in pagos:
                ws.cell(row=cont, column=1).value = suspencion.IdCierre
                ws.cell(row=cont, column=2).value = suspencion.Ingresos
                ws.cell(row=cont, column=3).value = suspencion.Gastos
                ws.cell(row=cont, column=4).value = suspencion.Presupuesto
                ws.cell(row=cont, column=5).value = suspencion.Ciclo
                ws.cell(row=cont, column=6).value = suspencion.Ano
                ws.cell(row=cont, column=7).value = suspencion.Fecha
                ws.cell(row=cont, column=8).value = suspencion.NoRecaudo
                ws.cell(row=cont, column=9).value = suspencion.Recaudado
                cont += 1

            archivo_predios = "ReporteCierres" + str(sfecha) + ".xlsx"
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
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            matricula = CobroMatricula.objects.filter(IdVivienda=IdVivienda,Estado=ESTCOBRO)

            return render(request, self.template_name,{
                'matriculas': matricula
            })

        except Vivienda.DoesNotExist:
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
                messages.add_message(request, messages.INFO, 'Las cuotas deben ser diferentes a las asignadad inicialmente')
                ver = self.vervivienda()
                ejercutar = ver.get(request, idvivienda)
                return ejercutar

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class EnvioCorreo(LoginRequiredMixin):
    login_url = '/'
    def get(self, asunto, informacion, tipousuario):
        now = datetime.now()
        context = {'asunto':asunto, 'fecha': now, 'informacion': informacion, 'usuario': tipousuario}
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

class ReporteEstadoCuenta(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
        pagos = EstadoCuenta.objects.all()
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de estados cuenta"
        ws['A1'] = 'Referencia'
        ws['B1'] = 'Valor'
        ws['C1'] = 'Vivienda'
        ws['D1'] = 'Estado'
        ws['E1'] = 'Fecha Actualizacion'
        ws['F1'] = 'Descripcion'

        sfecha = (datetime.today())
        cont = 2

        for pago in pagos:
            ws.cell(row=cont, column=1).value = pago.IdEstadoCuenta
            ws.cell(row=cont, column=2).value = pago.Valor
            ws.cell(row=cont, column=3).value = str(pago.IdVivienda)
            ws.cell(row=cont, column=4).value = pago.Estado
            ws.cell(row=cont, column=5).value = pago.FechaActualizacion
            ws.cell(row=cont, column=6).value = pago.Descripcion
            cont+=1
        archivo_propi = "ReporteEstadosCuenta" + str(sfecha) + ".xlsx"
        response = HttpResponse(content_type= "application/ms-excel")
        content = "attachment; filename = {0}".format(archivo_propi)
        response['Content-Disposition'] = content
        wb.save(response)
        return response

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
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='NOACFA').exists()
            if tipousuario is False:
                return render(request, self.template_name, {'propietario': propietario, 'matricula': matricula,
                                                    'informacion': infovivienda,'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti})
        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, IdVivienda):
        try:
            idpropietario = request.POST.get("idpropietario")
            propietario = Propietario.objects.filter(IdPropietario=idpropietario).exists()
            vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
            idpropi = vivienda.IdPropietario.pk
            if idpropi == idpropietario:
                ver = self.predio()
                messages.add_message(request, messages.ERROR, 'el documento del titular ingresado es el mismo que tiene asignado actualmente el predio, modifique la informacion del titular directamente')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

            else:
                if propietario is True:
                    usuario = Usuario.objects.get(usuid=request.user.pk)
                    vivienda = Vivienda.objects.get(IdVivienda=IdVivienda)
                    propie = Propietario.objects.get(IdPropietario=idpropietario)
                    vivienda.IdPropietario = propie
                    vivienda.save()
                    tiponovedad = 'Cambio titular'
                    descripcion = 'se cambia titular de servicio de ' + idpropi + ' por ' + str(propie) + ' por solicitud escrita '
                    novedad = NovedadesGenerales(Descripcion=descripcion, TipoNovedad=tiponovedad, usuario=usuario, matricula=str(vivienda.pk))
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

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti
                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{'form': form,'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            datosacueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            form = self.form_class(request.user, request.POST, instance=datosacueducto)

            datos = Usuario.objects.get(usuid=request.user.pk)
            dr = datos.IdAcueducto
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'La información se modifico correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.ERROR, 'No se puedo modificar la informacion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Propietario.DoesNotExist:
            return render(request, "pages-404.html")

class AsignarPermisos(LoginRequiredMixin, View):
    login_url = '/'
    form_class = PermisosForm
    template_name = 'usuarios/asignacionpermisos.html'
    def get(self, request,usuid):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            usuario2 = Usuario.objects.filter(usuid=usuid)
            consultar = Usuario.objects.get(usuid=usuid)
            permisos = Permisos.objects.filter(usuid=consultar)
            form = self.form_class(instance=usuario)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,{'form': form, 'usuario': usuario2, 'permisos': permisos})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
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

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class EliminarPermisos(LoginRequiredMixin, View):
    login_url = '/'
    form_class = PermisosForm
    template_name = 'usuarios/eliminarpermisos.html'
    def get(self, request,usuid):
        try:
            usuario1 = Usuario.objects.get(usuid=request.user.pk)
            usuario = Usuario.objects.get(usuid=usuid)
            form = self.form_class(instance=usuario)
            permisos = Permisos.objects.filter(usuid=usuid)
            tipousuario = Permisos.objects.filter(usuid=usuario1, TipoPermiso='SUPERADMIN').exists()
            if tipousuario is False:
                return render(request, self.template_name,{'form': form, 'permisos': permisos})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
        try:
            tipopermiso = request.POST.get("TipoPermiso")
            usuid = request.POST.get("usuid")
            usuario = Usuario.objects.get(usuid=usuid)
            permisos = Permisos.objects.filter(usuid=usuid)
            verificacion = Permisos.objects.filter(usuid=usuid, TipoPermiso=tipopermiso).exists()
            nu = 1
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
                messages.add_message(request, messages.ERROR, 'El codigo de permiso seleccionado no esta asignado al usuario')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{'form': form, 'form2': form2, 'notificaciones': contadorpen,'listapqrs': listapqrs,'totalnoti': totalnoti
                     })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            nombres = request.POST.get("first_name")
            apellidos = request.POST.get("last_name")

            foto = request.FILES.get("fotoUsuario")
            tipousuario = request.POST.get("TipoUsuario")
            telefono = request.POST.get("celular")
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            validarusu = User.objects.filter(username=username).exists()
            if validarusu == True:
                messages.add_message(request, messages.ERROR, 'El usuario ya existe')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=nombres, last_name=apellidos)
                usuario = Usuario(fotoUsuario=foto, TipoUsuario=tipousuario, celular=telefono, usuid=user, IdAcueducto=idacueducto)
                user.save()
                usuario.save()
                messages.add_message(request, messages.INFO, 'El usuario se creo correctamente')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except Usuario.DoesNotExist:
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
                return render(request, self.template_name,{'usuario': usuario, 'estado': estado})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
        try:
            user = User.objects.get(id=usuid)
            estado = user.is_active
            if estado is True:
                user.is_active = False
                user.save()
                messages.add_message(request, messages.INFO,'El usuario se desactivo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                user.is_active = True
                user.save()
                messages.add_message(request, messages.INFO,'El usuario se activo correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
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
                    messages.add_message(request, messages.INFO,'Tipo de poblacion eliminado correctamente')
                    return HttpResponseRedirect(reverse('usuarios:perfil'))
                else:
                    messages.add_message(request, messages.ERROR,'El tipo de poblacion no EXISTE')
                    return HttpResponseRedirect(reverse('usuarios:perfil'))

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:perfil'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class CambiarContraUsuario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/cambiarcontrasena.html'
    def get(self, request, usuid):
        try:
            print(usuid)
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            usuario = Usuario.objects.filter(usuid=usuid)
            user = User.objects.get(id=usuid)

            tipousuario = Permisos.objects.filter(usuid=usuario2, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,{'usuario': usuario})

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request, usuid):
        try:
            contrasena = request.POST.get("contrasena")
            recontrasena = request.POST.get("recontrasena")

            if contrasena == recontrasena:
                user = User.objects.get(id=usuid)
                user.set_password(contrasena)
                user.save()
                messages.add_message(request, messages.INFO,'la conseña se cambio correctamente')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

            else:
                messages.add_message(request, messages.INFO,'Las contraseñas no coinciden')
                return HttpResponseRedirect(reverse('usuarios:paneladmin'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ReporteCobroMatricula(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request):
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
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
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
                messages.add_message(request, messages.ERROR,'se modificaron los estados correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
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
                                                    'informacion': infovivienda, 'form':form})
            else:
                messages.add_message(request, messages.ERROR, 'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
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
                messages.add_message(request, messages.INFO,'El estado del servicio se modifico correctamente a OPERATIVO')
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
                messages.add_message(request, messages.INFO,'El estado del servicio se modifico correctamente a SUSPENDIDO')
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
                messages.add_message(request, messages.INFO,'El estado del servicio se modifico correctamente a RETIRADO')
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
                messages.add_message(request, messages.INFO, 'El estado del servicio se modifico correctamente a MANTENIMIENTO')
                ejecutar = ver.get(request, IdVivienda)
                return ejecutar

        except Usuario.DoesNotExist:
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
            viviendasope = Vivienda.objects.filter(EstadoServicio=E1).count()
            new_date = datetime(ano1, 1, 1, 1, 00, 00, 00000)
            new_date2 = datetime(ano2, 12, 30, 23, 59, 59, 00000)
            periodos= Cierres.objects.filter(Fecha__gte=new_date, Fecha__lte=new_date2).all()
            periodos2 = Cierres.objects.filter(Ano=ano1)
            nit = usuario2.IdAcueducto
            acueducto = Acueducto.objects.get(IdAcueducto=nit)
            tarifa = acueducto.IdTarifa.Valor
            totalpormes = int(int(viviendasope) * int(tarifa))
            listapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            sumatoria = Cierres.objects.all()

            ingresotip = 0
            for i in sumatoria:
                ingresotip += int(i.Ingresos)

            gastotip = 0
            for i in sumatoria:
                gastotip += int(i.Gastos)

            ingresos = 0
            for i in periodos:
                ingresos += int(i.Ingresos)

            gastos = 0
            for i in periodos:
                gastos += int(i.Gastos)

            resta = ingresotip - gastotip

            anual = totalpormes * 12
            porcentaje = ingresos / anual * 100

            estadocuentas = EstadoCuenta.objects.filter(Estado=E2)
            sumestado =0
            for i in estadocuentas:
                sumestado += i.Valor

            porcenperdidas = sumestado / anual * 100

            tipousuario = Permisos.objects.filter(usuid=usuario2, TipoPermiso='ACF').exists()
            if tipousuario is True:
                return render(request, self.template_name,{
                    'cierres': periodos,
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'saldo': resta,
                    'porcentaje': int(porcentaje),
                    'perdidas': int(porcenperdidas),
                    'cont': sumestado,
                    'notificaciones': contadorpen,
                    'listapqrs': listapqrs,
                    'totalnoti': totalnoti

                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario2 = Usuario.objects.get(usuid=request.user.pk)
            #entradas de la vista
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
            gastosaprobados = SolicitudGastos.objects.filter(Fecha__gte=new_date, Fecha__lte=new_date2,Estado=ESTADO2).all()
            gasto4 = 0
            for i in gastosaprobados:
                valor = int(i.Valor)
                gasto4 += valor

            pago0 = 0
            for i in pagos2:
                valor = i.ValorPago
                pago0 += int(valor)
                
            filtro = Cierres.objects.filter(Ciclo=periodo,Ano=ano).exists()
            usuario = auth.authenticate(username=username1, password=password1)
            if usuario is not None and usuario.is_active:
                print(pago0,gasto4)
                print(ingresos,egresos)
                if filtro is False:
                    if pago0 == int(ingresos) and gasto4 == int(egresos):
                        cierre = Cierres(Ingresos=ingresos,Gastos=egresos,Presupuesto=presupuesto,Ciclo=periodo,Ano=ano,NoRecaudo=usuario2)
                        cierre.save()
                        messages.add_message(request, messages.INFO, 'El cierre se efectuo correctamente')
                        return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

                    else:
                        messages.add_message(request, messages.ERROR, 'Los valores no coinciden con los valores calculados por el sistema')
                        return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

                else:
                    messages.add_message(request, messages.ERROR, 'El periodo ingresado ya esta registrado')
                    return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

            else:
                messages.add_message(request, messages.ERROR,'Credenciales incorrectas')
                return HttpResponseRedirect(reverse('usuarios:cierrefinanciero'))

        except Usuario.DoesNotExist:
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

        except Cierres.DoesNotExist:
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

        except Cierres.DoesNotExist:
            return render(request, "pages-404.html")


class V3(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/base_usuario2.html'

    def get(self, request):
        try:

            return render(request, self.template_name
            )

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ListaCierre(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/listadecierres.html'

    def get(self, request):
        try:
            cierres = Cierres.objects.all()
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)

            return render(request, self.template_name,{
                'cierres': cierres,
                'notificaciones': contadorpen,
                'listapqrs': drilistapqrs,
                'totalnoti': totalnoti
            }
            )

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class PanelAdmin(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/paneladmin.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            nit = usuario.IdAcueducto
            ye = datetime.now()
            ano = ye.year
            usuarios = Usuario.objects.all()
            tarifas = Tarifa.objects.all().order_by('-IdTarifa')
            poblaciones = Poblacion.objects.all()
            matriculas = ValorMatricula.objects.all()
            acueducto = Acueducto.objects.get(IdAcueducto=nit)
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            usuario = Usuario.objects.get(usuid=request.user.pk)

            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,{
                    'notificaciones': contadorpen,
                    'ano': str(ano),
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti,
                    'logo': acueducto.logo,
                    'razonsocial': acueducto.Nombre,
                    'nit': acueducto.IdAcueducto,
                    'direccion': acueducto.DirOficina,
                    'email': acueducto.Email,
                    'legal': acueducto.Relegal,
                    'telefono': acueducto.Telefono,
                    'estado': acueducto.Estado,
                    'tarifa': acueducto.IdTarifa.Valor,
                    'usuarios': usuarios,
                    'tarifas': tarifas,
                    'matriculas': matriculas,
                    'poblacion': poblaciones

                }
                )
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class PerfilUsuario(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/perfilusuario.html'

    def get(self, request, IdUsuario):
        try:
            idusuario=IdUsuario
            usuario = Usuario.objects.get(usuid=request.user.pk)
            drilistapqrs = Pqrs.objects.filter(Estado='Pendiente')
            contqrs = Pqrs.objects.filter(Estado='Pendiente').count()
            contsoli = SolicitudGastos.objects.filter(Estado=ESTADO1).count()
            totalnoti = contqrs + contsoli
            contadorpen = SolicitudGastos.objects.filter(Estado=ESTADO1)
            #inicio consultas
            infousuario = Usuario.objects.get(IdUsuario=idusuario)
            user = User.objects.get(username=infousuario.usuid)
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:

                return render(request, self.template_name,{
                    'cedula': infousuario.usuid_id,
                    'notificaciones': contadorpen,
                    'listapqrs': drilistapqrs,
                    'totalnoti': totalnoti,
                    'foto': infousuario.fotoUsuario,
                    'usuario': user.username,
                    'nombres': user.first_name,
                    'apellidos': user.last_name,
                    'celular': infousuario.celular,
                    'email': user.email,
                    'cargo': infousuario.TipoUsuario,
                    'fechac': infousuario.FechaCreacion,
                    'ultimo': user.last_login,
                    'departamento': infousuario.Departamento

                }
                )
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class AnularSuspenciones(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/anularsuspenciones.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            ordenesuspencion = OrdenesSuspencion.objects.filter(Estado="Pendiente").count()
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessPanel').exists()
            if tipousuario is True:
                return render(request, self.template_name,{'cantidad': ordenesuspencion})
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            ordensus = OrdenesSuspencion.objects.filter(Estado="Pendiente")
            verificacion = OrdenesSuspencion.objects.filter(Estado="Pendiente").count()
            facturas = Factura.objects.filter(Estado=FE).count()
            if facturas >=1:
                messages.add_message(request, messages.ERROR, 'Toda la facturacion debe estar Anulada o Vencida')
                return HttpResponseRedirect(reverse('usuarios:suspenciones'))

            else:
                if verificacion >= 1:
                    for orden in ordensus:
                        cambio = OrdenesSuspencion.objects.get(IdOrden=orden.pk)
                        cambio.Estado = "Anulada"
                        cambio.UsuarioEjecuta = "Sistema"
                        cambio.save()
                    messages.add_message(request, messages.INFO, 'Se cambio el estado de las ordenes')
                    return HttpResponseRedirect(reverse('usuarios:suspenciones'))
                else:
                    messages.add_message(request, messages.ERROR, 'No hay ordenes disponibles para anular')
                    return HttpResponseRedirect(reverse('usuarios:suspenciones'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class Consumos(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/consumos.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idacueducto = usuario.IdAcueducto
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AC').exists()
            acueducto = Acueducto.objects.get(IdAcueducto=idacueducto)
            # consultas de tarifas
            tarifa = acueducto.IdTarifa.Valor
            idtarifa = acueducto.IdTarifa
            tarifas = Tarifa.objects.get(IdTarifa=idtarifa)
            #consulta de medidas en m3
            consumomin = tarifas.consumomin
            contipo1 = consumomin + 1
            consumotipo1 = tarifas.consumotipo1
            contipo2 = consumotipo1 + 1
            consumotipo2 = tarifas.consumotipo2
            consumotipo3 = consumotipo2 + 1
            #porcentajes de aumento
            porcentajetipo1 = float(tarifas.Potipo1)
            porcentajetipo2 = tarifas.Potipo2
            #tarifas por tipo de consumo
            valormetro = int(tarifa)
            portipo1 = int(valormetro * porcentajetipo1) / 100
            portipo2 = int(valormetro * tarifas.Potipo2) / 100

            medidores = Medidores.objects.all().count()
            viviendas = Vivienda.objects.filter(EstadoServicio='Operativo').count()
            sinmedidor= viviendas - medidores
            if tipousuario is True:
                return render(request, self.template_name,{
                    'medidoresregistrados': medidores, 'porcentipo1': porcentajetipo1,'porcentipo2': porcentajetipo2,
                    'sinmedidor': sinmedidor,'valormetro': int(valormetro),
                    'tarifa': tarifa,'consumomin': consumomin,'contipo1':contipo1,'consumotipo1': consumotipo1,'contipo2': contipo2,
                    'consumotipo2': consumotipo2,'consumotipo3': consumotipo3, 'portipo1': int(portipo1), 'portipo2': int(portipo2)
                })

            else:
                messages.add_message(request, messages.ERROR,'Su usuario tiene permisos de acceso a este modulo')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class ImprimirSoporteP(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, IdPago):
        try:
            pago = Pagos.objects.filter(IdPago=IdPago).exists()
            impresoras = ConectorV3.obtenerImpresoras()
            nombreImpresora = "termica3"  # Nota: esta impresora debe existir y estar compartida como se indica en https://parzibyte.me/blog/2017/12/11/instalar-impresora-termica-generica/

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
            conector.EscribirTexto("Fecha:")
            conector.EscribirTexto("20/10/2022\n")
            conector.EscribirTexto("Hora:")
            conector.EscribirTexto("23:05\n")
            conector.Feed(1)
            conector.EscribirTexto("Referencia:\n")
            conector.EscribirTexto("PNV002 - Sector no 3\n")
            conector.EscribirTexto("Ultimo periodo pagado:\n")
            conector.EscribirTexto("Septiembre\n")
            conector.EscribirTexto("Numero de transaccion:\n")
            conector.EscribirTexto("8500\n")
            conector.Feed(1)
            conector.EscribirTexto("Aportes:")
            conector.EscribirTexto("$8.000\n")
            conector.EscribirTexto("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n")
            conector.EscribirTexto("TOTAL A PAGAR: $8.000\n")
            conector.EscribirTexto("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n")
            conector.EstablecerAlineacion(ALINEACION_CENTRO)
            conector.Corte(1)
            conector.Pulso(48, 60, 120)
            respuesta = conector.imprimirEn(nombreImpresora)
            if respuesta == True:
                messages.add_message(request, messages.INFO, 'impreso correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.ERROR, respuesta)
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class PazSalvo(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda

    def get(self, request, *args, **kwargs):
        try:
            tipo = request.GET.get("pys", "")
            matricula = request.GET.get("matricula")
            vivienda = Vivienda.objects.get(IdVivienda=matricula)
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

            if tipo == 'Aportes':
                estadocuenta = EstadoCuenta.objects.get(IdVivienda=matricula)
                valor = estadocuenta.Valor
                if valor <=0:
                    wb = openpyxl.load_workbook('static/Formatos/E8CPS.xlsx')
                    ws = wb.active
                    # primer mensaje
                    ws['U9'] = matricula
                    ws['A10'] = nombrecompleto
                    ws['A11'] = direccion
                    ws['A16'] = 'Con la Presente se certifica que el predio ubicado en la dirección: ' + sector + ' casa No ' + casa + ' con matrícula ' + matricula +', se encuentra a Paz y Salvo por concepto de Pagos de acueducto.'
                    ws['A22'] = 'El presente certificado se expide por solicitud del interesado a los '+ str(dia) +' días del mes '+ str(mes) + ' del año ' + str(anio)
                    if estado == 'Operativo':
                        ws['A26'] = 'Como el predio tiene la matricula activa, el presente certificado solo es valido por 30 dias a partir de la fecha de expedicion.'
                    else:
                        ws['A26'] = ' '
                    ws.title = matricula
                    archivo_predios = "paz y salvo " + str(matricula) + ".xlsx"
                    response = HttpResponse(content_type="application/ms-excel")
                    content = "attachment; filename = {0}".format(archivo_predios)
                    response['Content-Disposition'] = content
                    wb.save(response)
                    return response
                else:
                    messages.add_message(request, messages.ERROR, 'El predio no se encuentra a paz y salvo por conceptos de acueducto')
                    ver = self.vervivienda()
                    ejercutar = ver.get(request, matricula)
                    return ejercutar

            elif tipo == 'Matricula':
                concepto = CobroMatricula.objects.get(IdVivienda=matricula)
                valor = int(concepto.ValorPendiente)
                if valor <=0:
                    wb = openpyxl.load_workbook('static/Formatos/E8CPS.xlsx')
                    ws = wb.active
                    # primer mensaje
                    ws['U9'] = matricula
                    ws['A10'] = nombrecompleto
                    ws['A11'] = direccion
                    ws['A16'] = 'Con la Presente se certifica que el predio ubicado en la dirección: ' + sector + ' casa No ' + casa + ' con matrícula ' + matricula +', se encuentra a Paz y Salvo por concepto de Pagos de matricula.'
                    ws['A22'] = 'El presente certificado se expide por solicitud del interesado a los '+ str(dia) +' días del mes '+ str(mes) + ' del año ' + str(anio)
                    if estado == 'Operativo':
                        ws['A26'] = 'Apreciado titular, este certificado solo hace referencia al estado de cuenta de la matricula, si necesita consultar su estado de cuenta referente a las mensualidades solicite un certificado de aportes.'
                    else:
                        ws['A26'] = ' '
                    ws.title = matricula
                    archivo_predios = "paz y salvo " + str(matricula) + ".xlsx"
                    response = HttpResponse(content_type="application/ms-excel")
                    content = "attachment; filename = {0}".format(archivo_predios)
                    response['Content-Disposition'] = content
                    wb.save(response)
                    return response
                else:
                    messages.add_message(request, messages.ERROR, 'El predio no se encuentra a paz y salvo por concepto de matricula')
                    ver = self.vervivienda()
                    ejercutar = ver.get(request, matricula)
                    return ejercutar

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class CertificadoGral(LoginRequiredMixin, View):
    login_url = '/'
    vervivienda = VisualizarVivienda

    def get(self, request, *args, **kwargs):
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

                #Estado de cuenta
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

                #ordenes de trabajo
                suspencionespen = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,Estado='Pendiente').count()
                suspencioneseje = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,Estado='Ejecutada').count()
                suspencionesanu = OrdenesSuspencion.objects.filter(IdEstadoCuenta=idestadocuenta,Estado='Anulada').count()
                ws['S42'] = suspencioneseje
                ws['U42'] = suspencionesanu
                ws['W42'] = suspencionespen
                reconexionespen = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestadocuenta,Estado='Pendiente').count()
                reconexioneseje = OrdenesReconexion.objects.filter(IdEstadoCuenta=idestadocuenta,Estado='Ejecutada').count()
                ws['Y42'] = reconexioneseje
                ws['AA42'] = reconexionespen

                #ultimo pago
                filtropagos = Pagos.objects.filter(IdVivienda=matricula).order_by("-IdPago")[:1]
                idpago = Pagos.objects.get(IdPago=filtropagos)
                ws['S49'] = str(idpago)
                ws['Y49'] = 'Registrado'
                ws['S51'] = idpago.FechaPago
                ws['Y51'] = idpago.ValorPago

                #certificado
                certificacion = Certificaciones.objects.get(IdVivienda=matricula)
                estado = certificacion.Estado
                ws['S45'] = estado

                #fechas de procedimiento
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

        except Vivienda.DoesNotExist:
            return render(request, "pages-404.html")

class ImprimirSoRyS(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, IdOrden):
        try:
            orden = PagoOrdenes.objects.get(IdOrden=IdOrden)
            cobro = CobroOrdenes.objects.get(IdOrden=IdOrden)
            tipoorden = cobro.TipoOrden
            fecha = orden.FechaPago
            valorpago = orden.Valor
            referencia1 = orden.IdVivienda
            respuesta = True
            if respuesta == True:
                messages.add_message(request, messages.INFO, 'El pago registro correctamente')
                return HttpResponseRedirect(reverse('usuarios:inicio'))
            else:
                messages.add_message(request, messages.INFO,'No se pudo imprimri correctamente el soporte')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

class PagarRyS(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/pagarorden.html'
    imprimirtiquet = ImprimirSoRyS
    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idorden = request.GET.get("orden")
            cobroordenes = CobroOrdenes.objects.get(IdOrden=idorden)
            ordenes = CobroOrdenes.objects.filter(IdOrden=idorden)
            verificacion = CobroOrdenes.objects.filter(IdOrden=idorden,Estado=FP).exists()
            idestadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=cobroordenes.IdEstadoCuenta.pk)
            vivienda = Vivienda.objects.get(IdVivienda=idestadocuenta.IdVivienda.pk)
            matricula = vivienda.IdVivienda
            sector = vivienda.Direccion
            casa = vivienda.NumeroCasa
            piso = vivienda.Piso
            tipousuario = Permisos.objects.filter(usuid=usuario, TipoPermiso='AccessVFac').exists()
            if tipousuario is True:
                return render(request, self.template_name,{'orden': idorden, 'fecha': cobroordenes.Fecha,'estado': cobroordenes.Estado, 'ordenes': ordenes,'total': cobroordenes.Valor,
                                                           'sector': sector, 'casa': casa, 'piso':piso, 'matricula': matricula, 'ciclo': cobroordenes.TipoOrden,
                                                           'verificacion':verificacion})
            else:
                messages.add_message(request, messages.ERROR,'Su usuario no tiene los permiso de acceso a esta seccion')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")

    def post(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            idorden = request.POST.get("orden", "")
            valorpagar = request.POST.get("valorp", "")
            orden = CobroOrdenes.objects.get(IdOrden=idorden)
            idestadocuenta = EstadoCuenta.objects.get(IdEstadoCuenta=orden.IdEstadoCuenta.pk)
            vivienda = Vivienda.objects.get(IdVivienda=idestadocuenta.IdVivienda.pk)
            idvivienda = vivienda.IdVivienda
            valor = orden.Valor
            if valorpagar == valor:
                orden = CobroOrdenes.objects.get(IdOrden=idorden)
                orden.Estado = FP
                orden.save()
                ordensave = PagoOrdenes(Valor=valorpagar, IdVivienda=vivienda, IdOrden=orden)
                ordensave.save()
                tiquet2 = self.imprimirtiquet()
                ejecutar = tiquet2.get(request, idorden)
                return ejecutar

            else:
                messages.add_message(request, messages.ERROR, 'No fue posible registrar el pago, verifique el valor digitado')
                return HttpResponseRedirect(reverse('usuarios:inicio'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")


class CobroRecargo(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'usuarios/cobrorecargo.html'

    def get(self, request):
        try:
            usuario = Usuario.objects.get(usuid=request.user.pk)
            estadoscuenta = EstadoCuenta.objects.all()
            cont = 0
            for i in estadoscuenta:
                valor = int(i.Valor)
                if valor >= 9500:
                    cont +=1

            return render(request, self.template_name,{
                'cont':cont})

        except Usuario.DoesNotExist:
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
                if valor >=9500:
                    cont +=1
                    estadoscu = EstadoCuenta.objects.get(IdEstadoCuenta=i.pk)
                    estadoscu.Valor += int(recargo)
                    estadoscu.save()

            messages.add_message(request, messages.INFO, 'Se genero el cobro de los recargos correctamente')
            return HttpResponseRedirect(reverse('usuarios:facturacion'))

        except Usuario.DoesNotExist:
            return render(request, "pages-404.html")