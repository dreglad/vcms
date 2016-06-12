import os
from math import ceil, floor
import random

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='breaksentence')
def breaksentence(text, thresshold=4):
    def balance(words, addition=0):
        cutpoint = (len(words)/2) + addition
        halfs = (words[:cutpoint], words[cutpoint:])
        lengths = map(lambda x: len(''.join(x)), halfs)
        recommended_addition = 1 if lengths[0] < lengths[1] else -1
        return (
            [' '.join(words) for words in halfs],
            abs(lengths[0]-lengths[1])/float(lengths[0]),
            recommended_addition
        )
    words = text.split()
    if len(words) < thresshold:
        parts = [text]
    else:
        parts, ratio, recomended = balance(words, 0)
        if ratio > 0.3:
            parts, second_ratio, second_recomended = balance(words, recomended)
            if second_ratio > ratio:
                parts, r, c = balance(words, second_recomended)

    return mark_safe('<span class="broken">%s</span>' % \
                ' '.join(['<span class="by-%d">%s</span>' % (len(parts), part)
                     for part in parts]).replace(' ...', '...'))


@register.filter(name='duration')
def duration(timedelta):
    if not timedelta: return timedelta
    hours, remainder = divmod(timedelta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    if minutes > 50: minutes = 0; hours += 1
    if seconds > 50: seconds = 0; minutes += 1
    if minutes and minutes < 10 and hours: minutes = 0; hours -= 1
    if seconds and seconds < 10 and minutes: seconds = 0; minutes -= 1
    if seconds in range(26, 34): seconds = 30
    if minutes in range(26, 34): minutes = 30

    duration = []
    if hours: duration.append(u'%d hr' % hours)
    if minutes: duration.append(u'%d min' % minutes)
    if seconds and not (hours and minutes): duration.append(u'%d seg' % seconds)
    return ', '.join(duration)


@register.tag(name="randomgen")
def randomgen(parser, token):
    items = []
    bits =  token.split_contents()
    for item in bits:
        items.append(item)
    return RandomgenNode(items[1:])

class RandomgenNode(template.Node):
    def __init__(self, items):
        self.items = []
        for item in items:
            self.items.append(item)
    
    def render(self, context):
        arg1 = self.items[0]
        arg2 = self.items[1]
        if "hash" in self.items:
            result = os.urandom(16).encode('hex')
        elif "float" in self.items:
            result = random.uniform(int(arg1), int(arg2))
        elif not self.items:
            result = random.random()
        else:
            result = random.randint(int(arg1), int(arg2))
        return result