from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from SAAL.models import Vivienda, SolicitudGastos, Certificaciones, Medidores, Poblacion
from SAAL.models import Propietario, CobroMatricula, ValorMatricula, Usuario
from SAAL.models import Acueducto, Tarifa, Permisos, Pqrs


class RegistroVivienda(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = "__all__"
        labels = {
            'IdVivienda': _(u'Numero de matricula'),
            'Direccion': _(u'Direccion Completa'),
            'NumeroCasa': _(u'Numero de la casa'),
            'Piso': _(u'Piso'),
            'Ciclo': _('Seleccione ciclo'),
            'TipoInstalacion': _('Seleccione tipo de instalacion'),
            'EstadoServicio': _(u'Seleccione estado del servicio'),
            'Estrato': _(u'Seleccione el estrato'),
            'IdPropietario': _(u'Seleccione el propietario'),
            'MatriculaAnt': _(u'Digite la matricula anterior'),
            'InfoInstalacion': _(u'Seleccione tipo de predio'),
            'ProfAcometida': _(u'Profundidad acometida'),
            'CantHabitantes': _(u'Cantidad de habitantes'),
            'FichaCastral': _(u'Ficha catastral'),
            'Diametro': _(u'Seleccione el diametro de tuberia'),
            'IdAcueducto': _(u''),
            'usuid': _(u''),
        }
        widgets = {
            'IdAcueducto': forms.HiddenInput(),
            'usuid': forms.HiddenInput(),
        }

    def __init__(self, vivienda=None, *args, **kwargs):
        super(RegistroVivienda, self).__init__(*args, **kwargs)
        if vivienda is not None:
            self.fields['IdAcueducto'].widget = forms.HiddenInput()
            self.fields['usuid'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ModificaVivienda(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = "__all__"
        labels = {
            'IdVivienda': _(u''),
            'Direccion': _(u'Direccion Completa'),
            'NumeroCasa': _(u'Numero de la casa'),
            'TipoInstalacion': _('seleccione tipo de instalacion'),
            'EstadoServicio': _(u'Seleccione estado del servicio'),
            'Estrato': _(u'Seleccione el estrato'),
            'IdPropietario': _(u''),
            'IdAcueducto': _(u''),
            'usuid': _(u''),
            'FichaCastral': _(u'Ficha catastral'),
        }
        widgets = {
            'IdVivienda': forms.HiddenInput(),
            'IdAcueducto': forms.HiddenInput(),
            'usuid': forms.HiddenInput(),
            'IdPropietario': forms.HiddenInput()
        }

    def __init__(self, vivienda=None, *args, **kwargs):
        super(ModificaVivienda, self).__init__(*args, **kwargs)
        if vivienda is not None:
            self.fields['IdAcueducto'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RegistroPropietario(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = "__all__"
        labels = {
            'IdPropietario': _(u'Numero de Identificacion'),
            'Nombres': _(u'Nombres'),
            'Apellidos': _(u'Apellidos'),
            'NoTelefono': _('Telefono o Celular'),
            'Email': _(u'Correo electronico'),
            'Direccion': _(u'Direccion'),
            'IdPoblacion': _(u'Tipo de población'),
        }

    def __init__(self, propietario=None, *args, **kwargs):
        super(RegistroPropietario, self).__init__(*args, **kwargs)
        if propietario is not None:
            self.fields['IdPropietario'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ModificaPropietario(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = "__all__"
        labels = {
            'IdPropietario': _(u''),
            'Nombres': _(u'Nombres'),
            'Apellidos': _(u'Apellidos'),
            'NoTelefono': _('Telefono o Celular'),
            'Email': _(u'Correo electronico'),
        }
        widgets = {
            'IdPropietario': forms.HiddenInput(),
        }

    def __init__(self, propietario=None, *args, **kwargs):
        super(ModificaPropietario, self).__init__(*args, **kwargs)
        if propietario is not None:
            self.fields['IdPropietario'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AcueductoForm(forms.ModelForm):
    class Meta:
        model = Acueducto
        fields = [
            'Estado'
        ]
        labels = {
            'Estado': _(u'Estado Actual')
        }

    def __init__(self, *args, **kwargs):
        super(AcueductoForm, self).__init__(*args, **kwargs)
        self.fields['Estado'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class GastosForm(forms.ModelForm):
    class Meta:
        model = SolicitudGastos
        fields = [
            'Estado'
        ]
        labels = {
            'Estado': _(u'Modificar el estado de orden')
        }

    def __init__(self, *args, **kwargs):
        super(GastosForm, self).__init__(*args, **kwargs)
        self.fields['Estado'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class MedidoresForm(forms.ModelForm):
    class Meta:
        model = Medidores
        fields = "__all__"
        labels = {
            'IdMedidor': _(u'Numero del medidor'),
            'Marca': _(u'Marca o referencia'),
            'Tipo': _(u'Tipo de medidor'),
            'LecturaInicial': _(u'Lectura inicial'),
            'AnoFabricacion': _(u'Año de fabricacion'),
            'IdVivienda': _(u''),
        }
        widgets = {
            'IdVivienda': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(MedidoresForm, self).__init__(*args, **kwargs)
        self.fields['IdMedidor'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CertificarForm(forms.ModelForm):
    class Meta:
        model = Certificaciones
        fields = [
            'Estado',
            'Descripcion',
            'Soporte',
            'IdVivienda'
        ]
        labels = {
            'Estado': _(u'Modificar estado'),
            'Descripcion': _(u'Descripcion'),
            'Soporte': _(u'Cumple los requisitos minimos de certificacion'),
            'IdVivienda': _(u''),
        }
        widgets = {
            'IdVivienda': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(CertificarForm, self).__init__(*args, **kwargs)
        self.fields['Estado'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CobroMatriculaForm(forms.ModelForm):
    class Meta:
        model = CobroMatricula
        fields = [
            'IdValor',
            'CantCuotas'
        ]
        labels = {
            'IdValor': _(u'Seleccione el valor de la matricula'),
            'CantCuotas': _(u'Cantidad de cuotas')
        }

    def __init__(self, *args, **kwargs):
        super(CobroMatriculaForm, self).__init__(*args, **kwargs)
        self.fields['IdValor'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PoblacionForm(forms.ModelForm):
    class Meta:
        model = Poblacion
        fields = [
            'IdPoblacion',
            'Descripcion'
        ]
        labels = {
            'IdPoblacion': _(u'Identificador de la poblacion'),
            'Descripcion': _(u'Descripcion de la poblacion')
        }

    def __init__(self, *args, **kwargs):
        super(PoblacionForm, self).__init__(*args, **kwargs)
        self.fields['IdPoblacion'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CostoMForm(forms.ModelForm):
    class Meta:
        model = ValorMatricula
        fields = [
            'Valor'
        ]
        labels = {
            'Valor': _(u'Ingrese el valor'),
        }

    def __init__(self, *args, **kwargs):
        super(CostoMForm, self).__init__(*args, **kwargs)
        self.fields['Valor'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class TarifasForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = [
            'IdTarifa',
            'Valor',
            'Mantenimiento',
            'Recargo',
            'TarifaReconexion',
            'TarifaSuspencion',
            'bifamiliar',
            'multifamiliar',
            'especial',
            'Ano',
        ]
        labels = {
            'IdTarifa': _(u'Identificador de la tarifa'),
            'Valor': _(u'Aporte unifamiliar'),
            'Mantenimiento': _(u'Aporte de mantenimiento'),
            'Recargo': _(u'Aporte por mora'),
            'TarifaReconexion': _(u'Aporte por reconexion'),
            'TarifaSuspencion': _(u'Aporte por Suspencion'),
            'bifamiliar': _(u'Aporte bifamiliar'),
            'multifamiliar': _(u'Aporte multifamiliar'),
            'especial': _(u'Aporte especial'),
            'Ano': _(u'Año de vigencia'),
        }

    def __init__(self, *args, **kwargs):
        super(TarifasForm, self).__init__(*args, **kwargs)
        self.fields['Valor'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RespuestPqrForm(forms.ModelForm):
    class Meta:
        model = Pqrs
        fields = [
            'Estado'
        ]
        labels = {
            'Estado': _(u'Cambio de estado'),
        }

    def __init__(self, *args, **kwargs):
        super(RespuestPqrForm, self).__init__(*args, **kwargs)
        self.fields['Estado'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AcueductoAForm(forms.ModelForm):
    class Meta:
        model = Acueducto
        fields = "__all__"
        labels = {
            'IdAcueducto': _(u''),
            'Nombre': _(u'Razon social'),
            'DirOficina': _(u'Direccion oficina'),
            'Relegal': _(u'Representante legal'),
            'Telefono': _(u'Telefono coorporativo'),
            'IdTarifa': _(u'Tarifa actual'),
            'Email': _(u'Email coorporativo')
        }
        widgets = {
            'IdAcueducto': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(AcueductoAForm, self).__init__(*args, **kwargs)
        self.fields['IdAcueducto'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PermisosForm(forms.ModelForm):
    class Meta:
        model = Permisos
        fields = [
            'TipoPermiso',
            'usuid',
        ]
        labels = {
            'TipoPermiso': _(u'Seleccione el tipo de permiso que desea asignar'),
            'usuid': _(u''),
        }
        widgets = {
            'usuid': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PermisosForm, self).__init__(*args, **kwargs)
        self.fields['usuid'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RegistroUsuario(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email'
        ]
        labels = {
            'username': _(u'Nombre de usuario'),
            'password': _(u'Contraseña'),
            'first_name': _(u'Nombres'),
            'last_name': _(u'Apellidos'),
            'email': _(u'Correo electrónico')
        }
        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput()
        }

    def __init__(self, *args, **kwargs):
        super(RegistroUsuario, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['password'].required = True
        self.fields['email'].required = True

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RegistroUsuario2(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        labels = {
            'IdUsuario': _(u''),
            'fotoUsuario': _(u'Foto de usuario'),
            'TipoUsuario': _(u'Tipo de usuario'),
            'FechaCreacion': _(u''),
            'celular': _(u'Numero de celular'),
            'usuid': _(u''),
            'IdAcueducto': _(u'Seleccionar empresa')
        }
        widgets = {
            'usuid': forms.HiddenInput(),
            'FechaCreacion': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(RegistroUsuario2, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CambioFormEstado(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = [
            'EstadoServicio'
        ]
        labels = {
            'EstadoServicio': _(u'Seleccione el estado del servicio'),
        }

    def __init__(self, vivienda=None, *args, **kwargs):
        super(CambioFormEstado, self).__init__(*args, **kwargs)
        if vivienda is not None:
            self.fields['IdAcueducto'].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class FormRegistroPqrs(forms.ModelForm):
    class Meta:
        model = Pqrs
        fields = "__all__"
        labels = {
            'Nombre': _(u'Nombre completo'),
            'Telefono': _(u'Telefono o Celular'),
            'Email': _(u'Correo electronico'),
            'Direccion': _(u'Direccion'),
            'TipoSolicitud': _(u'Tipo de solicitud'),
            'Clasificacion': _(u'Clasificacion'),
            'Descripcion': _(u'Descripcion de la solicitud'),
            'usuid': _(u''),
            'Estado': _(u''),
        }
        widgets = {
            'usuid': forms.HiddenInput(),
            'Estado': forms.HiddenInput(),
        }

    def __init__(self, propietario=None, *args, **kwargs):
        super(FormRegistroPqrs, self).__init__(*args, **kwargs)
        if propietario is not None:
            self.fields[''].widget = forms.HiddenInput()

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
