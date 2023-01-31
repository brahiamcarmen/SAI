from django.conf.urls import url
from usuarios.views import Inicio, Busquedas, CobroRecargo, ControlPresupuestal, VerFactura, PagarMatricula
from usuarios.views import V3, ImprimirSoporteP, PagarRyS
from usuarios.views import ListaViviendas, ListaPropietarios, Certificar, ReportePdfPagos
from usuarios.views import ReporteCierresAno, PazSalvo, CertificadoGral
from usuarios.views import AgregarVivienda, AgregarPropietario, PerfilUsuario, ReporteCompleto
from usuarios.views import ReporteSuspenciones, ReporteReconexion, ModificarPropietario, ModificarVivienda
from usuarios.views import EliminarPermisos, ReporteCiclo, Mapa, EliminarPoblacion
from usuarios.views import VisualizarPropietario, CambioEstado, Facturacion, AgregarUsuarios, Reporte, RegistroCostoM
from usuarios.views import RegistroTarifa, ReporteEstadoCuenta, Reportepdfpropi, ReporteGastos, ListasGastos
from usuarios.views import Suspenciones, VerOrdenSuspencion, VerOrdenReconexion, CambioTitular
from usuarios.views import ReportePredios, CierreFinanciero, ReporteSuspendido, ReportesEstado
from usuarios.views import ReportesCiclo, CambiosMasivos, Facturas, GenerarGasto
from usuarios.views import ListaCierre, InfoVivienda, GeneradorFacturas, DesactivarUsuarios, AnularFactura
from usuarios.views import DescargarFactura, DescargaMasivaFacturas, VisualizarVivienda, BuscarSolicitud
from usuarios.views import Reconexiones, Perfil, ModificarAcueducto, ListaPqrs, RegistroPqr, VerPqr, ListadoPqrs
from usuarios.views import RespuestaPqrs, PanelAdmin, ReporteCierre, AnularSuspenciones
from usuarios.views import RegistroMedidor, ReporteCobroMatricula, AsignarPermisos
from usuarios.views import RegistroPoblacion, CambiarContraUsuario, ListasOrdenes, GeneradorFacturasIndividual

urlpatterns = [
    url(r'^inicio/', Inicio.as_view(), name='inicio'),
    url(r'^listaviviendas/', ListaViviendas.as_view(), name='listaviviendas'),
    url(r'^listapropietarios/', ListaPropietarios.as_view(), name='listapropietarios'),
    url(r'^agregarvivienda/', AgregarVivienda.as_view(), name='agregarvivienda'),
    url(r'^agregarpropietario/', AgregarPropietario.as_view(), name='agregarpropietario'),
    url(r'^modificarpropietario/(?P<IdPropietario>\w+)', ModificarPropietario.as_view(), name='modificarpropietario'),
    url(r'^modificarvivienda/(?P<IdVivienda>\w+)', ModificarVivienda.as_view(), name='modificarvivienda'),
    url(r'^verpropiedario/(?P<IdPropietario>\w+)', VisualizarPropietario.as_view(), name='verpropietario'),
    url(r'^facturacion/', Facturacion.as_view(), name='facturacion'),
    url(r'^facturas/', Facturas.as_view(), name='facturas'),
    url(r'^reporte/', Reporte.as_view(), name='reporte'),
    url(r'^reportepdf/', Reportepdfpropi.as_view(), name='reportepdf'),
    url(r'^reportepdfv/', ReportePredios.as_view(), name='reportepdfv'),
    url(r'^reportecompleto/', ReporteCompleto.as_view(), name='reportecompleto'),
    url(r'^vervivienda/(?P<IdVivienda>\w+)', VisualizarVivienda.as_view(), name='vervivienda'),
    url(r'^reportesuspendido/', ReporteSuspendido.as_view(), name='reportesuspendido'),
    url(r'^reporteestados/', ReportesEstado.as_view(), name='reporteestados'),
    url(r'^reporteciclo/', ReportesCiclo.as_view(), name='reporteciclo'),
    url(r'^reportepagos/', ReportePdfPagos.as_view(), name='reportepagos'),
    url(r'^busquedas/', Busquedas.as_view(), name='busquedas'),
    url(r'^reporteciclos/', ReporteCiclo.as_view(), name='reporteciclos'),
    url(r'^controlpresupuestal/', ControlPresupuestal.as_view(), name='controlpresupuestal'),
    url(r'^generargasto/', GenerarGasto.as_view(), name='generargasto'),
    url(r'^cambio/', BuscarSolicitud.as_view(), name='cambio'),
    url(r'^listadogastos/', ListasGastos.as_view(), name='listadogastos'),
    url(r'^infovivienda/(?P<IdVivienda>\w+)', InfoVivienda.as_view(), name='infovivienda'),
    url(r'^registromedidor/(?P<IdVivienda>\w+)', RegistroMedidor.as_view(), name='registromedidor'),
    url(r'^certificar/(?P<IdCertificacion>\w+)', Certificar.as_view(), name='certificar'),
    url(r'^perfil/', Perfil.as_view(), name='perfil'),
    url(r'^registropoblacion/', RegistroPoblacion.as_view(), name='registropoblacion'),
    url(r'^registrocostomatricula/', RegistroCostoM.as_view(), name='registrocostomatricula'),
    url(r'^registrotarifa/', RegistroTarifa.as_view(), name='registrotarifa'),
    url(r'^verfactura/', VerFactura.as_view(), name='verfactura'),
    url(r'^registropqrs/', RegistroPqr.as_view(), name='registropqrs'),
    url(r'^listapqrs/', ListaPqrs.as_view(), name='listapqrs'),
    url(r'^verpqr/', VerPqr.as_view(), name='verpqr'),
    url(r'^listadopqrs/', ListadoPqrs.as_view(), name='listadopqrs'),
    url(r'^generadorfacturas/', GeneradorFacturas.as_view(), name='generadorfacturas'),
    url(r'^suspenciones/', Suspenciones.as_view(), name='suspenciones'),
    url(r'^anularfactura/', AnularFactura.as_view(), name='anularfactura'),
    url(r'^respuestapqr/(?P<idsolicitud>\w+)', RespuestaPqrs.as_view(), name='respuestapqr'),
    url(r'^listasordenes/', ListasOrdenes.as_view(), name='listasordenes'),
    url(r'^verordensus/(?P<IdOrden>\w+)', VerOrdenSuspencion.as_view(), name='verordensus'),
    url(r'^verordenre/(?P<IdOrden>\w+)', VerOrdenReconexion.as_view(), name='verordenre'),
    url(r'^descargarfactura/(?P<IdFactura>\w+)', DescargarFactura.as_view(), name='descargarfactura'),
    url(r'^facturaindividual/(?P<IdVivienda>\w+)', GeneradorFacturasIndividual.as_view(), name='facturaindividual'),
    url(r'^facturamasiva/', DescargaMasivaFacturas.as_view(), name='facturamasiva'),
    url(r'^reportesuspenciones', ReporteSuspenciones.as_view(), name='reportesuspenciones'),
    url(r'^reportereconexiones', ReporteReconexion.as_view(), name='reportereconexiones'),
    url(r'^reportecierresano', ReporteCierresAno.as_view(), name='reportecierresano'),
    url(r'^reporteestadoscuenta', ReporteEstadoCuenta.as_view(), name='reporteestadoscuenta'),
    url(r'^pagarmatricula/(?P<IdVivienda>\w+)', PagarMatricula.as_view(), name='pagarmatricula'),
    url(r'^cambiotitular/(?P<IdVivienda>\w+)', CambioTitular.as_view(), name='cambiotitular'),
    url(r'^mapa', Mapa.as_view(), name='mapa'),
    url(r'^modificarempresa', ModificarAcueducto.as_view(), name='modificarempresa'),
    url(r'^asignarpermisos/(?P<usuid>\w+)', AsignarPermisos.as_view(), name='asignarpermisos'),
    url(r'^eliminarpermisos/(?P<usuid>\w+)', EliminarPermisos.as_view(), name='eliminarpermisos'),
    url(r'^agregarusuarios', AgregarUsuarios.as_view(), name='agregarusuarios'),
    url(r'^desacusuario/(?P<usuid>\w+)', DesactivarUsuarios.as_view(), name='desacusuario'),
    url(r'^elipoblacion', EliminarPoblacion.as_view(), name='elipoblacion'),
    url(r'^cambiarcontrasena/(?P<usuid>\w+)', CambiarContraUsuario.as_view(), name='cambiarcontrasena'),
    url(r'^reportecobromatricula', ReporteCobroMatricula.as_view(), name='reportecobromatricula'),
    url(r'^masivos', CambiosMasivos.as_view(), name='masivos'),
    url(r'^cambioestado/(?P<IdVivienda>\w+)', CambioEstado.as_view(), name='cambioestado'),
    url(r'^cierrefinanciero', CierreFinanciero.as_view(), name='cierrefinanciero'),
    url(r'^reportecierre', ReporteCierre.as_view(), name='reportecierre'),
    url(r'^reportegastos', ReporteGastos.as_view(), name='reportegastos'),
    url(r'^V', V3.as_view(), name='V'),
    url(r'^listacierres', ListaCierre.as_view(), name='listacierres'),
    url(r'^reconexiones', Reconexiones.as_view(), name='reconexiones'),
    url(r'^paneladmin', PanelAdmin.as_view(), name='paneladmin'),
    url(r'^perfilusuario/(?P<IdUsuario>\w+)', PerfilUsuario.as_view(), name='perfilusuario'),
    url(r'^anularsuspenciones', AnularSuspenciones.as_view(), name='anularsuspenciones'),
    url(r'^imprimirpago/(?P<IdPago>\w+)', ImprimirSoporteP.as_view(), name='imprimirpago'),
    url(r'^pazysalvo', PazSalvo.as_view(), name='pazysalvo'),
    url(r'^certificadogral', CertificadoGral.as_view(), name='certificadogral'),
    url(r'^pagarrys', PagarRyS.as_view(), name='pagarrys'),
    url(r'^cobrorecargo', CobroRecargo.as_view(), name='cobrorecargo'),
]
