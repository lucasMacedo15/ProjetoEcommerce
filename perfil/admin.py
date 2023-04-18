from django.contrib import admin
from .models import Perfil, Endereco
# Register your models here.


class InlineEndereco(admin.TabularInline):
    model = Endereco
    extra = 1


class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'idade', 'cpf', )
    inlines = [InlineEndereco]


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Endereco)
