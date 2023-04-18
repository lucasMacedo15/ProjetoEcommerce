from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, View, DetailView
from . import models
from perfil.models import Perfil, Endereco
from django.contrib import messages
from django.db.models import Q


class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 5
    ordering = ['-id']

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search')
        if not search:
            return qs
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(descricao_curta__iexact=search)
        )
        if not qs:
            messages.warning(
                self.request, 'Desculpe, não encontramos nenhum produto com este nome :(')

        return qs


class DetalhesProduto(DetailView):

    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AdicionarCarrinho(View):
    def get(self, request, *args, **kwargs):

        http_referer = self.request.META.get(
            'HTTP_REFERER', reverse('produto:lista'))
        variacao_id = self.request.GET.get('variacao-id')

        # SE NÃO PASSAR NENHUM PARÂMETRO PARA VARIACAO-ID, GERA UMA MENSAGEM DE ERRO
        # E REDIRECIONA PARA A PÁGINA ANTERIOR
        if not variacao_id:
            messages.error(
                self.request, 'Produto não existe'
            )
            return redirect(http_referer)
        # RETORNA OBJETO VARIAÇÃO OU ERRO 404 CASO NAO EXISTA
        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.produto

        # DEFINIÇÃO DOS VALORES DO CARRINHO
        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        int_variacao_id = variacao.id
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        # VERIFICA SE TEM IMAGEM DO PRODUTO
        if imagem:
            imagem = imagem.name
        else:
            imagem = ''
        # VERIFICA SE TEM NO ESTOQUE
        if variacao_estoque < 1:
            messages.error(
                self.request, 'Produto indisponível no momento'
            )
            return redirect(http_referer)

        # SE NAO TIVER UM SESSÃO CARRINHO, CRIA UMA NOVA
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']
        # SE TIVER VARIAÇÃO ID DO TIPO STR NO DICIONÁRIO DO CARRINHO, ADICIONA A QUANTIDADE EM 1
        estoque_vazio = False
        if variacao_id in carrinho:

            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request, f'Estoque insuficiente para {quantidade_carrinho}x no produto {produto_nome}.'
                    f'Adicionamos {variacao_estoque}x no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque
                estoque_vazio = True

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * \
                quantidade_carrinho
        # CASO CONTRÁRIO, INSERE NOVOS PRODUTOS NO CARRINHO
        else:
            carrinho[variacao_id] = {

                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': 1,
                'slug': slug,
                'imagem': imagem,

            }

        self.request.session.save()

        if not estoque_vazio:
            messages.success(
                self.request, f'Produto {produto.nome} {variacao.nome} adicionado com sucesso')

        return redirect(http_referer)


class RemoverCarrinho(View):
    # SE O PRODUTO ESTIVER EM PROMOÇÃO, RETORNA TOTAL COM PRODUTO EM PROMOÇÃO,
    # CASO CONTRÁRIO, RETORNARÁ PREÇO NORMAL
    def total(self, session, id):
        if session:
            qtd_carrinho = session[id]['quantidade']
            preco_sem_promo = session[id]['preco_unitario']
            preco_com_promo = session[id]['preco_unitario_promocional']
            session[id]['preco_quantitativo'] = qtd_carrinho * \
                preco_sem_promo
            session[id]['preco_quantitativo_promocional'] = qtd_carrinho * \
                preco_com_promo
            if preco_com_promo:
                return qtd_carrinho*preco_com_promo
            return qtd_carrinho*preco_sem_promo

    def get(self, request, *args, **kwargs) -> HttpResponse:
        item_id_var = self.request.GET.get('delet-all')
        item_id_remove = self.request.GET.get('remove-item')
        item_id_add = self.request.GET.get('add-item')
        http_referer = self.request.META.get(
            'HTTP_REFERER', reverse('produto:lista'))

        # VERIFICA QUAIS KEYS FORAM GERADAS PELO GET
        for k in self.request.GET.keys():

            # VERIFICA SE O VALOR VINDO DO GET(ADD,REMOVE,VAR) EXISTE
            if not item_id_var and item_id_remove and item_id_add:

                return redirect(http_referer)
            # VERIFICA SE EXISTE UM CARRINHO
            if not self.request.session.get('carrinho'):

                return redirect(http_referer)
            # VERIFICA SE NAO EXISTE O ID_VAR NO CARRINHO
            '''
            if item_id_var not in self.request.session['carrinho']:
                print('CAI NO 3')
                return redirect(http_referer)
            '''

            # SE A CHAVE DO METODO GET FOR ADD-ITEM, ADICIONA +1 NA QUANTIDADE DO PRODUTO
            if 'add-item' in k:
                self.request.session['carrinho'][item_id_add]['quantidade'] += 1
                self.total(
                    self.request.session['carrinho'], item_id_add)

                self.request.session.save()
                break
            # SE A CHAVE DO METODO GET FOR REMOVE-ITEM, REMOVE 1 NA QUANTIDADE DO PRODUTO
            elif 'remove-item' in k:
                self.request.session['carrinho'][item_id_remove]['quantidade'] -= 1

                self.total(self.request.session['carrinho'], item_id_remove)

                if self.request.session['carrinho'][item_id_remove]['quantidade'] < 1:
                    produto = self.request.session["carrinho"][item_id_remove]
                    messages.success(
                        self.request, f'Produto {produto["produto_nome"]} removido do seu carrinho'
                    )
                    del self.request.session['carrinho'][item_id_remove]

                self.request.session.save()
                break
            # SE A CHAVE DO METODO GET FOR DELET-ALL, REMOVE TODOO PRODUTO
            elif 'delet-all' in k:
                produto = self.request.session['carrinho'][item_id_var]

                messages.success(
                    self.request, f'Produto {produto["produto_nome"]} removido do seu carrinho'
                )
                del self.request.session['carrinho'][item_id_var]
                self.request.session.save()
                break

        return redirect(http_referer)


class Carrinho(View):

    def get(self, request, *args, **kwargs):
        contexto = self.request.session.get('carrinho', {})
        print(type(contexto.get('7')))
        return render(self.request, 'produto/carrinho.html', contexto)


class ResumoDaCompra(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        perfil = Perfil.objects.filter(usuario=self.request.user).first()

        endereco = Endereco.objects.filter(perfil=perfil).first()

        if not endereco or not perfil:
            messages.warning(
                self.request, 'Por favor, preencha o restante dos dados antes de finalizar sua compra.')
            return redirect('perfil:criar')
        if not self.request.session.get('carrinho'):
            messages.error(self.request, 'Carrinho vazio')
            return redirect('produto:lista')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
            'perfil': perfil,
            'endereco': endereco,

        }

        return render(self.request, 'produto/resumo-da-compra.html', contexto)
