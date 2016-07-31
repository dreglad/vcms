from django.contrib.sitemaps import Sitemap

from videos.models import Video

class SeccionSitemap(Sitemap):
    changefreq = "never"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Pagina.objects.filter(activo=True)

    def lastmod(self, obj):
        return obj.fecha_modificacion or obj.fecha_creacion

    def location(self, obj):
        return obj.get_absolute_url(absolute=False)


class VideoSitemap(Sitemap):
    changefreq = "never"
    protocol = 'https'
    priority = 0.5
    limit = 100

    def items(self):
        return Video.objects.publicos()

    def lastmod(self, obj):
        return obj.fecha_modificacion or obj.fecha_creacion

    def location(self, obj):
        return obj.get_absolute_url(absolute=False)
