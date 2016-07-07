from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def site_name():
    return settings.SITE_NAME


@register.simple_tag
def get_video_admin_tabs(admin, video):
    return admin.get_video_tabs(video)
