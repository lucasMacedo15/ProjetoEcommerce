def formata_preco(val):
    return f'R$ {val:.2f}'.replace('.', ',')


def qtd_total_carrinho(carrinho):

    return sum([item['quantidade'] for item in carrinho.values()])


# def total_carrinho(carrinho):
#     total_do_carrinho = 0
#     for item in carrinho.values():
#         if item['preco_unitario_promocional']:
#             total_promo = item['preco_quantitativo_promocional']
#             total_do_carrinho += total_promo
#         elif item['preco_unitario'] and not item['preco_unitario_promocional']:
#             total_sem_promo = item['preco_quantitativo']
#             total_do_carrinho += total_sem_promo
#     return formata_preco(total_do_carrinho)


def total_carrinho(carrinho):
    total_do_carrinho = sum(
        [item['preco_quantitativo_promocional'] if item['preco_unitario_promocional']
         else item['preco_quantitativo'] if item['preco_unitario'] and not item['preco_unitario_promocional']
         else 0 for item in carrinho.values()])
    return total_do_carrinho
