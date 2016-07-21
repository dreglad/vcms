# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from django.contrib.admin.widgets import AdminFileWidget
from django.forms import FileInput
from django.forms import TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sorl.thumbnail import get_thumbnail

class FilestackWidget(TextInput):
    """Django form widget that sets up Uploadcare Widget.

    It adds js and hidden input with basic Widget's params, e.g.
    *data-public-key*.

    """

    input_type = 'hidden'
    is_hidden = False

    class Media:
        js = (
            'vcms/form_upload.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {
            'role': 'fileslack-uploader',
            #'data-public-key': conf.pub_key,
        }

        if attrs is not None:
            default_attrs.update(attrs)

        super(FilestackWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs):
        return super(FilestackWidget, self).render(name, value, attrs)


class AdminImageWidget(FileInput):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_path = value.path.replace('.vtt', '.jpg')
            image_url = value.url
            file_name = str(value)
            vtt = False
            if (file_name.endswith('.vtt')):
                vtt = True
                image_path = value.path.replace('.vtt', '.jpg')
                image_url = value.url.replace('.vtt', '.jpg')
                file_name = file_name.replace('.vtt', '.jpg')

            if name == 'icono':
                size = '30'
            else:
                size = '360'
            thumb = get_thumbnail(image_path, size, crop='center', quality=99)
            output.append(u'<a href="%s" target="_blank">' \
                          u'<img style="margin-top:1em; margin-right:1em;" class="responsive" src="%s" alt="%s" /></a>' % (
                              image_url, thumb.url, file_name))
            if not vtt:
                output.append('<br>Para modificar elija un nuevo archivo: <br/>')
                output.append(super(FileInput, self).render(name, value, attrs))
        else:
            output.append(super(FileInput, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
