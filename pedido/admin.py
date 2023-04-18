from django.contrib import admin

# Register your models here.

from .models import Pedido, ItemPedido


class InlineItemPedido(admin.TabularInline):
    model = ItemPedido
    extra = 1


class PedidoAdmin(admin.ModelAdmin):

    inlines = [InlineItemPedido]


admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemPedido)
