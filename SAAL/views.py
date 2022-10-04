# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib import auth
from django.contrib import messages
from SAAL.models import Usuario
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render


class Login(View):

    def get(self, request):
        nombre = open('static/serial/NombreProyecto.txt', 'r')
        proyectov = nombre.read()
        version = open('static/serial/Version.txt', 'r')
        versionp = version.read()
        return render(request, 'index.html', {'proyecto': proyectov,
                                              'version': versionp})
    def post(self, request):
        username1 = request.POST.get("username", "")
        password1 = request.POST.get("password", "")
        usuario = auth.authenticate(username=username1, password=password1)

        if usuario is not None and usuario.is_active:
            auth.login(request, usuario)
            listuser = Usuario.objects.filter(usuid=usuario.pk)
            if len(listuser) > 0:
                return HttpResponseRedirect(reverse('usuarios:inicio'))

            else:
                messages.add_message(request, messages.ERROR, "Las credenciales de acceso son incorrectas")
                return HttpResponseRedirect(reverse('login'))

        else:
            messages.add_message(request, messages.ERROR, "Las credenciales de acceso son incorrectas")
            return HttpResponseRedirect(reverse('login'))

class Logout(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse('login'))