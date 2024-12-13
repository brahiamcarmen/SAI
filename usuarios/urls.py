from django.conf.urls import url
from usuarios.views import Inicio, Busquedas, CobroRecargo, ControlPresupuestal, VerFactura
from usuarios.views import ImprimirSoporteP, AnularPago, AsignarCargo, VerCredito
from usuarios.views import ListaViviendas, ListaPropietarios, ReportePdfPagos, Creditos, RegistroCredito
from usuarios.views import RegistroProveedor, Consumo,AsignarMedidor, RegistrarConsumo
from usuarios.views import PazSalvo, ReporteConceptos, MapaMedidores
from usuarios.views import AgregarVivienda, AgregarPropietario, ReporteCompleto
from usuarios.views import ReporteOrdenesT, ModificarPropietario, ModificarVivienda
from usuarios.views import RegMenCon, EliminarPoblacion, AcuerdoPago
from usuarios.views import VisualizarPropietario, CambioEstado, Estadoscuenta, RegistroCostoM
from usuarios.views import RegistroTarifa,ReporteGastos, ListasGastos
from usuarios.views import OrdenesdeTrabajo, VerOrdenSuspencion, CambioTitular
from usuarios.views import CierreFinanciero, VerConsumo, GeneradorConceptos, Varias
from usuarios.views import GenerarGasto
from usuarios.views import GeneradorFacturas, DesactivarUsuarios, AnularFactura
from usuarios.views import DescargarFactura, DescargaMasivaFacturas, VisualizarVivienda, BuscarSolicitud
from usuarios.views import ModificarAcueducto, ListaPqrs, RegistroPqr, VerPqr
from usuarios.views import RespuestaPqrs, ReporteCierre, ReporteConsumos, PlantillaMedicion
from usuarios.views import RegistroMedidor
from usuarios.views import CambiarContraUsuario, GeneradorFacturasIndividual,ReporteRetiro

urlpatterns = [
    url(r'^inicio/', Inicio.as_view(), name='inicio'),
    url(r'^listaviviendas/', ListaViviendas.as_view(), name='listaviviendas'),
    url(r'^listapropietarios/', ListaPropietarios.as_view(), name='listapropietarios'),
    url(r'^agregarvivienda', AgregarVivienda.as_view(), name='agregarvivienda'),
    url(r'^agregarpropietario/', AgregarPropietario.as_view(), name='agregarpropietario'),
    url(r'^modificarpropietario/(?P<IdPropietario>\w+)', ModificarPropietario.as_view(), name='modificarpropietario'),
    url(r'^modificarvivienda/(?P<idvivienda>\w+)', ModificarVivienda.as_view(), name='modificarvivienda'),
    url(r'^verpropiedario/(?P<idpropietario>\w+)', VisualizarPropietario.as_view(), name='verpropietario'),
    url(r'^vervivienda/(?P<idvivienda>\w+)', VisualizarVivienda.as_view(), name='vervivienda'),
    url(r'^estadoscuenta/', Estadoscuenta.as_view(), name='estadoscuenta'),
    url(r'^reportecompleto/', ReporteCompleto.as_view(), name='reportecompleto'),
    url(r'^reportepagos/', ReportePdfPagos.as_view(), name='reportepagos'),
    url(r'^busquedas/', Busquedas.as_view(), name='busquedas'),
    url(r'^controlpresupuestal/', ControlPresupuestal.as_view(), name='controlpresupuestal'),
    url(r'^generargasto/', GenerarGasto.as_view(), name='generargasto'),
    url(r'^cambio/(?P<IdSoGa>\w+)', BuscarSolicitud.as_view(), name='cambio'),
    url(r'^listadogastos/', ListasGastos.as_view(), name='listadogastos'),
    url(r'^registromedidor/', RegistroMedidor.as_view(), name='registromedidor'),
    url(r'^registrocostomatricula/', RegistroCostoM.as_view(), name='registrocostomatricula'),
    url(r'^registrotarifa/', RegistroTarifa.as_view(), name='registrotarifa'),
    url(r'^verfactura/', VerFactura.as_view(), name='verfactura'),
    url(r'^registropqrs/', RegistroPqr.as_view(), name='registropqrs'),
    url(r'^listapqrs/', ListaPqrs.as_view(), name='listapqrs'),
    url(r'^verpqr/(?P<idpqr>\w+)', VerPqr.as_view(), name='verpqr'),
    url(r'^generadorfacturas/', GeneradorFacturas.as_view(), name='generadorfacturas'),
    url(r'^ordenestrabajo/', OrdenesdeTrabajo.as_view(), name='ordenestrabajo'),
    url(r'^anularfactura/', AnularFactura.as_view(), name='anularfactura'),
    url(r'^respuestapqr/(?P<idsolicitud>\w+)', RespuestaPqrs.as_view(), name='respuestapqr'),
    url(r'^verordensus/(?P<IdOrden>\w+)', VerOrdenSuspencion.as_view(), name='verordensus'),
    url(r'^descargarfactura/(?P<IdFactura>\w+)', DescargarFactura.as_view(), name='descargarfactura'),
    url(r'^facturaindividual/(?P<IdVivienda>\w+)', GeneradorFacturasIndividual.as_view(), name='facturaindividual'),
    url(r'^facturamasiva/', DescargaMasivaFacturas.as_view(), name='facturamasiva'),
    url(r'^reporteordenes', ReporteOrdenesT.as_view(), name='reporteordenes'),
    url(r'^cambiotitular/(?P<IdVivienda>\w+)', CambioTitular.as_view(), name='cambiotitular'),
    url(r'^modificarempresa', ModificarAcueducto.as_view(), name='modificarempresa'),
    url(r'^desacusuario/(?P<usuid>\w+)', DesactivarUsuarios.as_view(), name='desacusuario'),
    url(r'^elipoblacion', EliminarPoblacion.as_view(), name='elipoblacion'),
    url(r'^cambiarcontrasena/(?P<usuid>\w+)', CambiarContraUsuario.as_view(), name='cambiarcontrasena'),
    url(r'^cambioestado/(?P<IdVivienda>\w+)', CambioEstado.as_view(), name='cambioestado'),
    url(r'^cierrefinanciero', CierreFinanciero.as_view(), name='cierrefinanciero'),
    url(r'^reportecierre', ReporteCierre.as_view(), name='reportecierre'),
    url(r'^reportegastos', ReporteGastos.as_view(), name='reportegastos'),
    url(r'^imprimirpago/(?P<IdPago>\w+)', ImprimirSoporteP.as_view(), name='imprimirpago'),
    url(r'^pazysalvo/(?P<matricula>\w+)', PazSalvo.as_view(), name='pazysalvo'),
    url(r'^cobrorecargo', CobroRecargo.as_view(), name='cobrorecargo'),
    url(r'^anularpago', AnularPago.as_view(), name='anularpago'),
    url(r'^asignarcargo/(?P<matricula>\w+)', AsignarCargo.as_view(), name='asignarcargo'),
    url(r'^credito', Creditos.as_view(), name='credito'),
    url(r'^registrocredito', RegistroCredito.as_view(), name='registrocredito'),
    url(r'^registroproveedor', RegistroProveedor.as_view(), name='registroproveedor'),
    url(r'^vercredito/(?P<idcredito>\w+)', VerCredito.as_view(), name='vercredito'),
    url(r'^novedadretiro/(?P<matricula>\w+)', ReporteRetiro.as_view(), name='novedadretiro'),
    url(r'^consumos', Consumo.as_view(), name='consumos'),
    url(r'^asignarmedidor/(?P<IdMedidor>\w+)', AsignarMedidor.as_view(), name='asignarmedidor'),
    url(r'^registrarconsumo', RegistrarConsumo.as_view(), name='registrarconsumo'),
    url(r'^verconsumo/(?P<matricula>\w+)', VerConsumo.as_view(), name='verconsumo'),
    url(r'^crearconceptos', GeneradorConceptos.as_view(), name='crearconceptos'),
    url(r'^varias/', Varias.as_view(), name='varias'),
    url(r'^rconsumos/', ReporteConsumos.as_view(), name='rconsumos'),
    url(r'^reporteconceptos', ReporteConceptos.as_view(), name='reporteconceptos'),
    url(r'^pmedicion/', PlantillaMedicion.as_view(), name='pmedicion'),
    url(r'^regmencon/', RegMenCon.as_view(), name='regmencon'),
    url(r'^mapamedidores/', MapaMedidores.as_view(), name='mapamedidores'),
    url(r'^acuerdosdepago/', AcuerdoPago.as_view(), name='acuerdosdepago'),
]
