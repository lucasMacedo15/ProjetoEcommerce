from django.template import Library
from utils import utils

register = Library()


@register.filter
def formata_preco(val):
    return utils.formata_preco(val)


@register.filter
def qtd_total_carrinho(carrinho):

    return utils.qtd_total_carrinho(carrinho)


@register.filter
def total_carrinho(carrinho):

    return utils.total_carrinho(carrinho)
