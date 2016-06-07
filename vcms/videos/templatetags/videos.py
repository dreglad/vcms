from django import template

register = template.Library()

@register.filter(name='duration')
def duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = td.seconds

    duration = u''

    if minutes > 50:
        minutes = 0
        hours+= 1
    if seconds > 25:
        seconds = 0
        minutes+= 1

    if hours == 1: duration += u'1 hora '
    elif hours > 1: duration += u'%d horas ' % hours

    if minutes == 1: duration += u'1 min '
    elif minutes > 1: duration += u'%d mins ' % minutes

    if duration: return duration.strip()
    else: return '< 1 min'