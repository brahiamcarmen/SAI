from django.conf.urls import url
from usuarios.views import Inicio, Busquedas, CobroRecargo, ControlPresupuestal, VerFactura, PagarMatricula
from usuarios.views import ImprimirSoporteP, PagarRyS, AnularPago, AsignarCargo, Bloque, VerCredito
from usuarios.views import ListaViviendas, ListaPropietarios, ReportePdfPagos, Creditos, RegistroCredito
from usuarios.views import RegistroProveedor
from usuarios.views import PazSalvo, CertificadoGral, Matriculas
from usuarios.views import AgregarVivienda, AgregarPropietario, PerfilUsuario, ReporteCompleto
from usuarios.views import ReporteSuspenciones, ReporteReconexion, ModificarPropietario, ModificarVivienda
from usuarios.views import EliminarPermisos, ReporteCiclo, Mapa, EliminarPoblacion
from usuarios.views import VisualizarPropietario, CambioEstado, Estadoscuenta, AgregarUsuarios, RegistroCostoM
from usuarios.views import RegistroTarifa,ReporteGastos, ListasGastos
from usuarios.views import Suspenciones, VerOrdenSuspencion, VerOrdenReconexion, CambioTitular
from usuarios.views import CierreFinanciero
from usuarios.views import ReportesCiclo, CambiosMasivos, CambioEstadoFacturas, GenerarGasto
from usuarios.views import GeneradorFacturas, DesactivarUsuarios, AnularFactura, PagoParcial
from usuarios.views import DescargarFactura, DescargaMasivaFacturas, VisualizarVivienda, BuscarSolicitud
from usuarios.views import Reconexiones, Perfil, ModificarAcueducto, ListaPqrs, RegistroPqr, VerPqr
from usuarios.views import RespuestaPqrs, PanelAdmin, ReporteCierre, GenerarCobros
from usuarios.views import RegistroMedidor, ReporteCobroMatricula, AsignarPermisos
from usuarios.views import RegistroPoblacion, CambiarContraUsuario, ListasOrdenes, GeneradorFacturasIndividual,ReporteRetiro

urlpatterns = [
    url(r'^inicio/', Inicio.as_view(), name='inicio'),
    url(r'^listaviviendas/', ListaViviendas.as_view(), name='listaviviendas'),
    url(r'^listapropietarios/', ListaPropietarios.as_view(), name='listapropietarios'),
    url(r'^agregarvivienda/(?P<idbloque>\w+)', AgregarVivienda.as_view(), name='agregarvivienda'),
    url(r'^agregarpropietario/', AgregarPropietario.as_view(), name='agregarpropietario'),
    url(r'^modificarpropietario/(?P<IdPropietario>\w+)', ModificarPropietario.as_view(), name='modificarpropietario'),
    url(r'^modificarvivienda/(?P<idvivienda>\w+)', ModificarVivienda.as_view(), name='modificarvivienda'),
    url(r'^verpropiedario/(?P<idpropietario>\w+)', VisualizarPropietario.as_view(), name='verpropietario'),
    url(r'^estadoscuenta/', Estadoscuenta.as_view(), name='estadoscuenta'),
    url(r'^anularfacturas/', CambioEstadoFacturas.as_view(), name='anularfacturas'),
    url(r'^reportecompleto/', ReporteCompleto.as_view(), name='reportecompleto'),
    url(r'^vervivienda/(?P<idvivienda>\w+)', VisualizarVivienda.as_view(), name='vervivienda'),
    url(r'^reporteciclo/', ReportesCiclo.as_view(), name='reporteciclo'),
    url(r'^reportepagos/', ReportePdfPagos.as_view(), name='reportepagos'),
    url(r'^busquedas/', Busquedas.as_view(), name='busquedas'),
    url(r'^reporteciclos/', ReporteCiclo.as_view(), name='reporteciclos'),
    url(r'^controlpresupuestal/', ControlPresupuestal.as_view(), name='controlpresupuestal'),
    url(r'^generargasto/', GenerarGasto.as_view(), name='generargasto'),
    url(r'^cambio/(?P<IdSoGa>\w+)', BuscarSolicitud.as_view(), name='cambio'),
    url(r'^listadogastos/', ListasGastos.as_view(), name='listadogastos'),
    url(r'^registromedidor/(?P<IdVivienda>\w+)', RegistroMedidor.as_view(), name='registromedidor'),
    url(r'^perfil/', Perfil.as_view(), name='perfil'),
    url(r'^registropoblacion/', RegistroPoblacion.as_view(), name='registropoblacion'),
    url(r'^registrocostomatricula/', RegistroCostoM.as_view(), name='registrocostomatricula'),
    url(r'^registrotarifa/', RegistroTarifa.as_view(), name='registrotarifa'),
    url(r'^verfactura/', VerFactura.as_view(), name='verfactura'),
    url(r'^registropqrs/', RegistroPqr.as_view(), name='registropqrs'),
    url(r'^listapqrs/', ListaPqrs.as_view(), name='listapqrs'),
    url(r'^verpqr/(?P<idpqr>\w+)', VerPqr.as_view(), name='verpqr'),
    url(r'^generadorfacturas/', GeneradorFacturas.as_view(), name='generadorfacturas'),
    url(r'^generarcobros/', GenerarCobros.as_view(), name='generarcobros'),
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
    url(r'^reconexiones', Reconexiones.as_view(), name='reconexiones'),
    url(r'^paneladmin', PanelAdmin.as_view(), name='paneladmin'),
    url(r'^perfilusuario/(?P<IdUsuario>\w+)', PerfilUsuario.as_view(), name='perfilusuario'),
    url(r'^imprimirpago/(?P<IdPago>\w+)', ImprimirSoporteP.as_view(), name='imprimirpago'),
    url(r'^pazysalvo/(?P<matricula>\w+)', PazSalvo.as_view(), name='pazysalvo'),
    url(r'^certificadogral', CertificadoGral.as_view(), name='certificadogral'),
    url(r'^pagarrys', PagarRyS.as_view(), name='pagarrys'),
    url(r'^cobrorecargo', CobroRecargo.as_view(), name='cobrorecargo'),
    url(r'^anularpago', AnularPago.as_view(), name='anularpago'),
    url(r'^asignarcargo/(?P<matricula>\w+)', AsignarCargo.as_view(), name='asignarcargo'),
    url(r'^matriculas', Matriculas.as_view(), name='matriculas'),
    url(r'^Bloque', Bloque.as_view(), name='bloque'),
    url(r'^credito', Creditos.as_view(), name='credito'),
    url(r'^registrocredito', RegistroCredito.as_view(), name='registrocredito'),
    url(r'^registroproveedor', RegistroProveedor.as_view(), name='registroproveedor'),
    url(r'^vercredito/(?P<idcredito>\w+)', VerCredito.as_view(), name='vercredito'),
    url(r'^pagoparcial', PagoParcial.as_view(), name='pagoparcial'),
    url(r'^novedadretiro/(?P<matricula>\w+)', ReporteRetiro.as_view(), name='novedadretiro')
]
