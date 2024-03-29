# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-28 04:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_auto_20160719_0617'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='link',
            options={'get_latest_by': 'fecha_creacion', 'verbose_name': 'link', 'verbose_name_plural': 'links'},
        ),
        migrations.AlterField(
            model_name='listaenpagina',
            name='mostrar_paginacion',
            field=models.NullBooleanField(choices=[(None, 'Autom\xe1tico'), (True, 'S\xed'), (False, 'No')], verbose_name='mostrar m\xe1s'),
        ),
        migrations.AlterField(
            model_name='pagina',
            name='mostrar_paginacion',
            field=models.NullBooleanField(choices=[(None, 'Autom\xe1tico'), (True, 'S\xed'), (False, 'No')], verbose_name='mostrar m\xe1s'),
        ),
        migrations.AlterField(
            model_name='plataforma',
            name='mostrar_paginacion',
            field=models.NullBooleanField(choices=[(None, 'Autom\xe1tico'), (True, 'S\xed'), (False, 'No')], verbose_name='mostrar m\xe1s'),
        ),
        migrations.AlterField(
            model_name='video',
            name='fps',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='FPS'),
        ),
        migrations.AlterField(
            model_name='video',
            name='mostrar_paginacion',
            field=models.NullBooleanField(choices=[(None, 'Autom\xe1tico'), (True, 'S\xed'), (False, 'No')], verbose_name='mostrar m\xe1s'),
        ),
        migrations.AlterField(
            model_name='video',
            name='sprites',
            field=models.FileField(blank=True, null=True, upload_to='sprites', verbose_name='sprites'),
        ),
        migrations.AlterField(
            model_name='videoenpagina',
            name='mostrar_paginacion',
            field=models.NullBooleanField(choices=[(None, 'Autom\xe1tico'), (True, 'S\xed'), (False, 'No')], verbose_name='mostrar m\xe1s'),
        ),
    ]
