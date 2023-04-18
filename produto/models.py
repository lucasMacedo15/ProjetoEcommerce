from django.db import models
from PIL import Image
from django.conf import settings
import os
from django.utils.text import slugify
from utils import utils
# Create your models here.


class Produto(models.Model):

    nome = models.CharField(max_length=255, verbose_name='Produto')
    descricao_curta = models.TextField(
        max_length=255, verbose_name='descrição curta')
    descricao_longa = models.TextField(verbose_name='descrição longa')
    imagem = models.ImageField(
        blank=True, upload_to='fotos/%Y/%m/%d', verbose_name='imagem')
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='Preço Promo')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples'),

        )
    )

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)

    get_preco_formatado.short_description = 'Preço'

    def get_preco_promo_formatado(self):
        return utils.formata_preco(self.preco_marketing_promocional)

    get_preco_promo_formatado.short_description = 'Preço Promo'

    def __str__(self) -> str:
        return self.nome

    @staticmethod
    def resize_image(img, new_width=800):
        image_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pillow = Image.open(image_path)
        original_width, original_heigth = img_pillow.size

        if original_width <= new_width:
            img_pillow.close()
            return
        new_heigth = round((new_width * original_heigth) / original_width)
        new_img = img_pillow.resize((new_width, new_heigth), Image.LANCZOS)
        new_img.save(

            image_path,
            optimize=True,
            quality=60


        )

    def save(self, *args, **kwargs):

        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)
        max_image_size = 800
        if self.imagem:
            self.resize_image(self.imagem, max_image_size)


class Variacao(models.Model):

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveBigIntegerField(default=1)

    def __str__(self) -> str:
        return self.nome or self.produto.nome
