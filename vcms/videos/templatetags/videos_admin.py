from django import template

register = template.Library()

@register.simple_tag
def get_video_admin_tabs(admin, video):
    return admin.get_video_tabs(video)
