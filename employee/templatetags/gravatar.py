from django import template
import hashlib

register = template.Library()


@register.filter(name='gravatar_url')
def gravatar_url(email, size=150):
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode("UTF-8")).hexdigest() + "?"
    gravatar_url += 's={}'.format(str(size))
    return gravatar_url
