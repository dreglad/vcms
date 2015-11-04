# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import clips.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('orden', models.IntegerField()),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['orden'],
                'verbose_name': 'categor\xeda',
                'verbose_name_plural': 'categor\xedas',
            },
        ),
        migrations.CreateModel(
            name='Clip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Identificador para la URL del clip, sin espacios ni caracteres especiales', max_length=100, null=True, blank=True)),
                ('origen', models.IntegerField(default=1, choices=[(0, b'Video propio'), (1, b'Externo: TouTube'), (2, b'Externo: Dailymotion')])),
                ('publicado', models.BooleanField(default=False)),
                ('transferido', models.BooleanField(default=False, verbose_name='procesado')),
                ('seleccionado', models.BooleanField(default=False, help_text='selecci\xf3n del editor')),
                ('fecha', models.DateTimeField()),
                ('titulo', models.CharField(max_length=70, null=True, verbose_name='t\xedtulo', blank=True)),
                ('descripcion', models.TextField(null=True, verbose_name='descripci\xf3n', blank=True)),
                ('archivo', models.FileField(null=True, upload_to=clips.models.upload_clip_archivo_to, blank=True)),
                ('imagen', sorl.thumbnail.fields.ImageField(help_text='Opcional. Si se omite se obtendr\xe1 autom\xe1ticamente', null=True, upload_to=clips.models.upload_clip_imagen_to, blank=True)),
                ('audio', models.FileField(upload_to=clips.models.upload_clip_audio_to, null=True, editable=False, blank=True)),
                ('duracion', models.TimeField(default=b'00:00', verbose_name='duraci\xf3n', editable=False)),
                ('resolucion', models.IntegerField(default=0, null=True, editable=False)),
                ('sprites', models.IntegerField(default=0, null=True, editable=False)),
                ('fps', models.FloatField(default=0, null=True, editable=False, blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario_creacion', models.CharField(max_length=50, null=True, editable=False, blank=True)),
                ('fecha_redaccion', models.DateTimeField(null=True, editable=False, blank=True)),
                ('usuario_redaccion', models.CharField(max_length=50, null=True, editable=False, blank=True)),
                ('fecha_publicacion', models.DateTimeField(null=True, editable=False, blank=True)),
                ('usuario_publicacion', models.CharField(max_length=50, null=True, editable=False, blank=True)),
                ('fecha_modificacion', models.DateTimeField(null=True, editable=False, blank=True)),
                ('usuario_modificacion', models.CharField(max_length=50, null=True, editable=False, blank=True)),
                ('ciudad', models.CharField(max_length=50, null=True, blank=True)),
                ('geotag', models.CharField(max_length=255, null=True, editable=False, blank=True)),
                ('hashtags', models.CharField(help_text='Hashtags para Twitter, incluir # y espacios entre cada uno, tal como en Twitter', max_length=255, null=True, blank=True)),
                ('capitulo', models.IntegerField(help_text='N\xfamero de cap\xedtulo (1, 2, 3, ...)', null=True, verbose_name='cap\xedtulo', blank=True)),
                ('observaciones', models.TextField(null=True, blank=True)),
                ('vistas', models.IntegerField(default=0, verbose_name=b'vistas', null=True, editable=False, blank=True)),
                ('categoria', models.ForeignKey(blank=True, to='clips.Categoria', null=True)),
            ],
            options={
                'ordering': ('-fecha', '-fecha_creacion'),
                'verbose_name': 'clip de video',
                'verbose_name_plural': 'clips de video',
            },
        ),
        migrations.CreateModel(
            name='Corresponsal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('orden', models.IntegerField(null=True, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('email', models.CharField(help_text='Opcional para notificaciones. No ser\xe1 publicado', max_length=255, null=True, blank=True)),
                ('twitter', models.CharField(help_text=b'Nombre de usuario en Twitter, sin prefijo "@"', max_length=30, null=True, blank=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['orden', 'nombre'],
                'verbose_name_plural': 'corresponsales',
            },
        ),
        migrations.CreateModel(
            name='Distribucion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=255, verbose_name='nombre/descripci\xf3n')),
                ('activo', models.BooleanField(default=True)),
                ('fecha_desde', models.DateTimeField(help_text='Realizar distribuci\xf3n a partir la fecha seleccionada', null=True, blank=True)),
                ('fecha_hasta', models.DateTimeField(help_text='Realizar distribuci\xf3n hasta la fecha seleccionada', null=True, blank=True)),
                ('configuracion', models.TextField(null=True, verbose_name='configuraci\xf3n', blank=True)),
                ('email', models.CharField(help_text='Uno o varios emails separados por comas con el formato:  Nombre Primer Destinatario &lt;usuario@dominio.com&gt;, Nombre Segundo Destinatario &lt;otro@dominio.com&gt;, ...', max_length=255, null=True, blank=True)),
                ('email_template', models.CharField(choices=[(b'notificacion-ficha-tecnica', b'Notificaci\xc3\xb3n con ficha t\xc3\xa9cnica'), (b'notificacion-sencilla', b'Notificaci\xc3\xb3n snecilla')], max_length=255, blank=True, help_text='Plantilla a usar para dar formato a los mensajes', null=True, verbose_name='Plantilla e-mail')),
                ('ftp_host', models.CharField(max_length=255, null=True, verbose_name='Host FTP', blank=True)),
                ('ftp_port', models.CharField(max_length=255, null=True, verbose_name='Puerto FTP', blank=True)),
                ('ftp_dir', models.CharField(max_length=255, null=True, verbose_name='Directorio FTP', blank=True)),
                ('ftp_user', models.CharField(max_length=255, null=True, verbose_name='Usuario FTP', blank=True)),
                ('ftp_pass', models.CharField(max_length=255, null=True, verbose_name='Contrase\xf1a FTP', blank=True)),
                ('texto', models.CharField(help_text='Clips que contengan el texto especificado en el t\xedtulo o descripci\xf3n', max_length=255, null=True, blank=True)),
                ('con_corresponsal', models.BooleanField(default=False, help_text='Elegur unicamente clips que tengan corresponsal asociado')),
                ('categorias', models.ManyToManyField(to='clips.Categoria', blank=True)),
                ('corresponsales', models.ManyToManyField(to='clips.Corresponsal', blank=True)),
            ],
            options={
                'verbose_name': 'notificaci\xf3n/distribuci\xf3n',
                'verbose_name_plural': 'notificaciones/distribuciones',
            },
        ),
        migrations.CreateModel(
            name='Distribuido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Instrucci\xc3\xb3n recibida'), (2, b'Iniciado'), (3, b'Completado'), (4, b'Error')])),
                ('clip', models.ForeignKey(to='clips.Clip')),
                ('distribucion', models.ForeignKey(related_name='distribuidos', to='clips.Distribucion')),
            ],
            options={
                'ordering': ['-fecha'],
                'verbose_name': 'clip notificado/distribu\xeddo',
                'verbose_name_plural': 'clips notificados/distribu\xeddos',
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.CharField(max_length=2)),
                ('geotag', models.CharField(max_length=255, null=True, blank=True)),
                ('ubicacion', models.IntegerField(verbose_name='ubicaci\xf3n', choices=[(0, 'Am\xe9rica Latina'), (1, 'Am\xe9rica'), (2, 'Europa'), (3, 'Asia'), (4, 'Ocean\xeda'), (5, '\xc1frica')])),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name': 'pa\xeds',
                'verbose_name_plural': 'pa\xedses',
            },
        ),
        migrations.CreateModel(
            name='Programa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('orden', models.IntegerField(null=True, blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('imagen', sorl.thumbnail.fields.ImageField(null=True, upload_to=clips.models.upload_programa_imagen_to, blank=True)),
                ('descripcion', models.TextField(null=True, verbose_name='descripci\xf3n', blank=True)),
                ('playlist', models.CharField(max_length=100, null=True, blank=True)),
                ('horario', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Serie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('descripcion', models.TextField(null=True, verbose_name='descripci\xf3n', blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('nombre', models.CharField(max_length=100)),
                ('activo', models.BooleanField(default=True)),
                ('usuario', models.CharField(max_length=100, null=True, blank=True)),
                ('contrasena', models.CharField(max_length=100, null=True, verbose_name='contrase\xf1a', blank=True)),
            ],
            options={
                'verbose_name': 'servicio externo',
                'verbose_name_plural': 'servicios externos',
            },
        ),
        migrations.CreateModel(
            name='ServicioClip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estado', models.IntegerField(choices=[(0, 'Procesando'), (1, 'Completo'), (2, 'Error')])),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('clip', models.ForeignKey(to='clips.Clip')),
                ('servicio', models.ForeignKey(to='clips.Servicio')),
            ],
            options={
                'verbose_name': 'clip cargado a servicio externo',
                'verbose_name_plural': 'clips cargados a servicios externos',
            },
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('orden', models.IntegerField(null=True, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('descripcion', models.TextField(null=True, verbose_name='descripci\xf3n', blank=True)),
                ('link', models.URLField(null=True, editable=False, blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-orden', '-id'],
            },
        ),
        migrations.CreateModel(
            name='TipoClip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('orden', models.IntegerField()),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
                ('nombre_plural', models.CharField(max_length=100, null=True, blank=True)),
                ('descripcion', models.TextField(null=True, verbose_name='descripci\xf3n', blank=True)),
                ('descargable', models.BooleanField(default=True)),
                ('servicios', models.ManyToManyField(to='clips.Servicio')),
            ],
            options={
                'ordering': ['orden'],
                'verbose_name': 'tipo de clip',
                'verbose_name_plural': 'tipos de clip',
            },
        ),
        migrations.CreateModel(
            name='TipoPrograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=100, null=True, editable=False, blank=True)),
                ('orden', models.IntegerField(null=True, blank=True)),
                ('nombre', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
                'ordering': ['orden', 'nombre'],
                'verbose_name': 'tipo de programa',
                'verbose_name_plural': 'tipos de programa',
            },
        ),
        migrations.AddField(
            model_name='servicio',
            name='clips',
            field=models.ManyToManyField(to='clips.Clip', through='clips.ServicioClip'),
        ),
        migrations.AddField(
            model_name='programa',
            name='excluir_servicios',
            field=models.ManyToManyField(help_text='Servicios a excluir en caso de que haya servicios habilitados para todos los clips tipo programa pero que no se desean aplicar a este programa en particular', related_name='programas_excluidos', to='clips.Servicio'),
        ),
        migrations.AddField(
            model_name='programa',
            name='servicios',
            field=models.ManyToManyField(help_text='Sericios a definir para este programa', to='clips.Servicio'),
        ),
        migrations.AddField(
            model_name='programa',
            name='tipo',
            field=models.ForeignKey(to='clips.TipoPrograma'),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='paises',
            field=models.ManyToManyField(to='clips.Pais', verbose_name='pa\xedses', blank=True),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='programas',
            field=models.ManyToManyField(to='clips.Programa', blank=True),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='series',
            field=models.ManyToManyField(to='clips.Serie', blank=True),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='temas',
            field=models.ManyToManyField(to='clips.Tema', blank=True),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='tipos',
            field=models.ManyToManyField(to='clips.TipoClip', blank=True),
        ),
        migrations.AddField(
            model_name='distribucion',
            name='tipos_programa',
            field=models.ManyToManyField(to='clips.TipoPrograma', blank=True),
        ),
        migrations.AddField(
            model_name='corresponsal',
            name='pais',
            field=models.ForeignKey(to='clips.Pais'),
        ),
        migrations.AddField(
            model_name='clip',
            name='corresponsal',
            field=models.ForeignKey(blank=True, to='clips.Corresponsal', null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='pais',
            field=models.ForeignKey(blank=True, to='clips.Pais', null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='programa',
            field=models.ForeignKey(blank=True, to='clips.Programa', null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='serie',
            field=models.ForeignKey(blank=True, to='clips.Serie', null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='tema',
            field=models.ForeignKey(blank=True, to='clips.Tema', null=True),
        ),
        migrations.AddField(
            model_name='clip',
            name='tipo',
            field=models.ForeignKey(to='clips.TipoClip'),
        ),
    ]
