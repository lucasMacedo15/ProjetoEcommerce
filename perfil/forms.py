from django import forms
from django.contrib.auth.models import User
from . import models

# MEXA AQUI CASO DESEJE ALTERAR OS CAMPOS DOS FORMS


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = models.Endereco
        fields = '__all__'
        exclude = ('perfil',)


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=None, widget=forms.PasswordInput(), label='Senha')
    # ADIÇÃO DE NOVO CAMPO NO FORMS
    password2 = forms.CharField(
        required=None, widget=forms.PasswordInput(), label='Confirmação Senha')

    # ADIÇÃO DE ATRIBUTO USUÁRIO
    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    class Meta:

        model = User

        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    # metodo para validação do formulario
    def clean(self):

        # QueryDict
        data = self.data
        # Dicionário
        cleaned = self.cleaned_data

        # Capturando alguns valores do dicionário
        usuario_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        email_data = cleaned.get('email')

        # Consultando usuario/email na base de dados o que foi enviado pelo forms
        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()
        # Mensagens de erro
        error_msg_user_exists = 'Usuário já existe'
        error_msg_email_exists = 'Email já existe'
        error_msg_password_match = 'Senhas não conferem'
        error_msg_short_password = 'Sua senha precisa de pelo menos 6 caracteres'
        error_msg_required_field = 'Este campo deve ser obrigatório'
        validation_error_messages = {

        }
        # Para usuários já logados e não anônimos

        if self.usuario and not self.usuario.is_anonymous:

            # nome de usuário enviado pelo forms diferente do resultado da consulta na
            # base de dados

            if usuario_data != usuario_db.username:
                if usuario_db:
                    validation_error_messages['username'] = error_msg_user_exists

            if not email_db or (email_data != email_db.email):
                validation_error_messages['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_messages['password'] = error_msg_password_match
                    validation_error_messages['password2'] = error_msg_password_match
                if len(password_data) < 6:
                    validation_error_messages['password'] = error_msg_short_password
        else:

            if usuario_db:
                validation_error_messages['username'] = error_msg_user_exists

            if email_db:
                validation_error_messages['email'] = error_msg_email_exists

            if password_data != password2_data:
                validation_error_messages['password'] = error_msg_password_match
                validation_error_messages['password2'] = error_msg_password_match
            if len(password_data) < 6:

                validation_error_messages['password'] = error_msg_short_password

        if validation_error_messages:
            raise (forms.ValidationError(validation_error_messages))
