# Generated by Django 4.1.7 on 2023-03-14 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0002_remove_perfil_endereco_endereco_perfil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endereco',
            name='perfil',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='perfil.perfil'),
        ),
    ]
