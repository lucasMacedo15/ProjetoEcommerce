from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import ListView, View, DetailView
from django.contrib import messages
from utils import utils
from produto.models import Produto, Variacao
from .models import Pedido, ItemPedido
from django.urls import reverse

# Create your views here.


# CLASSE CRIADA PARA EVITAR QUE USUÁRIOS ACESSEM PÁGINAS DE OUTROS USUÁRIOS ATRAVÉS DE ABAS ANONIMAS
class DispatchLoginRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):

        # SOMENTE USUÁRIOS LOGADOS
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(request, *args, **kwargs)
    # SERÁ RETORNANDO APENAS OS OBJETOS DE DO USUÁRIO QUE ESTÁ LOGADO

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        print(qs)
        return qs


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'


class SalvarPedido(View):

    def get(self, request, *args, **kwargs) -> HttpResponse:
        carrinho = self.request.session.get('carrinho')

        # USUARIO DEVE ESTAR AUTENTICADO
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Voce precisa fazer login')
            return redirect('perfil:criar')
        # DEVE HAVER UM CARRINHO
        if not self.request.session.get('carrinho'):
            messages.error(self.request, 'Carrinho Vazio')
        # ATRIBUIÇÃO DAS ID'S DE VARIACAO A UMA LISTA
        carrinho_variacao_ids = [variacao for variacao in carrinho.keys()]
        # CONSULTA DAS VARIAÇÕES EM FUNÇÃO DA LISTA ANTERIR
        bd_variacoes = list(
            Variacao.objects.select_related('produto').filter(
                id__in=carrinho_variacao_ids)
        )
        # PARA CADA VARIACAO, É CHECADO O ESTOQUE
        # CASO NAO HAJA ESTOQUE SUFICIENTE, É REDUZIDO PARA A QUANTIDADE RESTANTE DO ESTOQUE E ADICIONADO AO CARRINHO
        for variacao in bd_variacoes:
            var_id = str(variacao.id)
            estoque = variacao.estoque
            qtd_carrinho = carrinho[var_id]['quantidade']
            preco_unt = carrinho[var_id]['preco_unitario']
            preco_unt_promo = carrinho[var_id]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[var_id]['quantidade'] = estoque
                carrinho[var_id]['preco_unitario_promocional'] = estoque*preco_unt
                carrinho[var_id]['preco_quantitativo_promocional'] = estoque * \
                    preco_unt_promo

                error_msg_estoque = f'Produto {variacao.produto.nome} indisponível. Reduzimos a quantidade destes produtos em seu carrinho.'
                if error_msg_estoque:
                    messages.error(
                        self.request, error_msg_estoque)
                    self.request.session.save()

                return redirect('produto:carrinho')
        # REAPROVEITAMENTO DA FUNÇÃO PARA SOMA D OCARRINHO E QUANTIDADE TOTAL DE PRODUTOS NO CARRINHO
        qtd_total_carrinho = utils.qtd_total_carrinho(carrinho)
        valor_total_carrinho = utils.total_carrinho(carrinho)
        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C'

        )
        # APÓS CRIAÇÃO DO PEDIDO, O MESMO É SALVO COM STATUS DE 'C'
        pedido.save()
        # PARA CADA ITEM NA SESSAO CARRINHO, É CRIADO UM PEDIDO COM AS INFORMAÇÕES DA SESSÃO DO CARRINHO
        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_id'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],

                ) for v in carrinho.values()
            ]
        )
        # CARRINHO LIMPO APÓS CRIAR O PEDIDO
        del self.request.session['carrinho']

        return redirect(
            reverse('pedido:pagar', kwargs={
                'pk': pedido.pk
            })
        )


class DetalhesPedido(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhes.html'
    pk_url_kwarg = 'pk'


class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'

    ordering = ['-id']
