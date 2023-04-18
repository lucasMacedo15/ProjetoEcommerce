from django.contrib import messages
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from . import models
from . import forms
from .models import Perfil
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import copy
# Create your views here.


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.perfil = None

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        # Caso usuario esteja autenticado, efetua filtro do perfil e endereco
        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user).first()
            self.endereco = models.Endereco.objects.filter(
                perfil=self.perfil).first()

           # PARA USUÁRIOS LOGADOS, GERA CONTEXTO COM CAMPOS JÁ PREENCHIDOS NO FORMS
            self.contexto = \
                {'end_form': forms.EnderecoForm(data=self.request.POST or None, instance=self.endereco),
                 'perfil_form': forms.PerfilForm(data=self.request.POST or None, instance=self.perfil),
                 'user_form': forms.UserForm(data=self.request.POST or None, usuario=self.request.user, instance=self.request.user)
                 }

        else:
            # PARA USUÁRIOS NÃO LOGADOS, GERA O CONTEXTO COM CAMPOS VAZIOS NO FORMS
            self.contexto = \
                {'end_form': forms.EnderecoForm(data=self.request.POST or None),
                 'perfil_form': forms.PerfilForm(data=self.request.POST or None),
                 'user_form': forms.UserForm(data=self.request.POST or None, usuario=self.request.user)
                 }
        # SE USUÁRIO ESTIVER AUTENTICADO, TEMPLATE SERÁ DE ATUALIZAR PERFIL
        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'
        # RENDERIZAÇÃO DA PÁGINA
        self.renderizar = render(
            self.request, self.template_name, self.contexto)

        self.endereco = models.Endereco.objects.filter(
            perfil=self.perfil).first()
        self.end_form = self.contexto.get('end_form')
        self.perfil_form = self.contexto.get('perfil_form')
        self.user_form = self.contexto['user_form']

        return self.renderizar

    def get(self, *args, **kwargs):

        return self.renderizar


class Criar(BasePerfil):

    def post(self, *args, **kwargs):

        # Verificando se os formulários são válidos
        if not self.end_form.is_valid() or not self.perfil_form.is_valid() \
                or not self.user_form.is_valid():
            messages.error(
                self.request, 'Existem erros no seu formulário de cadastro. Verifique se todos os campos foram preenchidos corretamente.')

            return self.renderizar
        # captura do username e senha do forms através do cleaner data
        username = self.user_form.cleaned_data.get('username')
        password = self.user_form.cleaned_data.get('password')
        email = self.user_form.cleaned_data.get('email')
        first_name = self.user_form.cleaned_data.get('first_name')
        last_name = self.user_form.cleaned_data.get('last_name')

        # Usuário logado
        if self.request.user.is_authenticated:

            usuario = get_object_or_404(
                User, username=self.request.user.username)

            # TROCA A SENHA CASO INFORME
            if password:

                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:

                self.perfil_form.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfil_form.cleaned_data)
                endereco = models.Endereco(
                    **self.end_form.cleaned_data, perfil=perfil)
                perfil.save()
                endereco.save()

            else:
                print('CAI AQUI')
                perfil = self.perfil_form.save(commit=False)
                perfil.usuario = usuario
                endereco = self.end_form.save(commit=False)

                endereco.perfil = perfil

                perfil.save()
                endereco.save()

        # Usuario nao logado(novo)
        else:

            # salva o forms sem armazenar dna base de dados
            usuario = self.user_form.save(commit=False)
            # seta a senha a qual foi armazenada antes
            usuario.set_password(password)
            # Salva o usuário na base de dados
            usuario.save()
            perfil = self.perfil_form.save(commit=False)
            # atribui ao perfil o usuário salvo anteriormente na base de dados
            perfil.usuario = usuario
            # salva o perfil
            perfil.save()
            endereco = self.end_form.save(commit=False)
            # atribui ao endereco o perfil salvo anteriormente na base de dados
            endereco.perfil = perfil
            endereco.save()

        # EM CASO DE TROCA DE SENHA OU CRIAÇÃO DE NOVO USUÁRIO
        # EFETUA AUTENTICAÇÃO E LOGIN
        if password:

            autentica = authenticate(
                self.request, username=usuario, password=password)

            if autentica:
                login(self.request, user=usuario)
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()
        messages.success(self.request, 'Seu cadastro foi criado com sucesso.')
        return redirect('perfil:criar')


class Atualizar(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return HttpResponse('Atualizando')


class Login(View):

    def post(self, request, *args, **kwargs) -> HttpResponse:

        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        print(username, password)
        if not username or not password:
            messages.error(self.request, 'Por favor preencha o Usuário/Senha')
            return redirect('perfil:criar')

        usuario = authenticate(
            self.request, username=username, password=password)
        if not usuario:
            messages.error(self.request, 'Usuário e/ou Senha inválidos')
            return redirect('perfil:criar')

        login(self.request, user=usuario)
        messages.success(self.request, 'Logado com sucesso')
        return redirect('produto:carrinho')


class Logout(View):

    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Salva o carrinho para a próxima sessão.
        # Mesmo que seja efetuado o logout, o carrinho permanece intacto
        carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        logout(self.request)
        self.request.session['carrinho'] = carrinho
        return redirect('produto:lista')
