import re
import types

from django.template import Library
from django.utils.http import urlquote_plus
from django.conf import settings
from django.forms import BaseForm

from elsearch import utils

numeric_test = re.compile("^\d+$")
register = Library()

@register.filter
def quote_plus(string):
    return urlquote_plus(string)

@register.filter
def facet_render(fclass, value):
    return fclass.render(value)

@register.filter
def facet_param(fclass, value):
    return fclass.format_param(value)

@register.filter
def format_param_kv(key, value):
    return "%s=%s" % (key, value) # TODO encode?

@register.filter
def addparam(url, param):
    """Appends or removes a param from an URL"""
    if "?" in url:
        return "%s&%s" % (url, param)
    return "%s?%s" % (url, param)

@register.filter
def removeparam(url, param):
    """Removes a param from an URL, taking care of
    the ? or & parts."""
    print("Removing: %s from %s" % (param, url))
    urlstr = url.replace(param, "").replace("&&", "&")
    if urlstr.endswith(("?", "&")):
        urlstr = urlstr[:-1]
    return urlstr

@register.filter
def stripparam(url, paramnames):
    """Removes a param AND its value from an URL, taking care of
    the ? or & parts."""
    params = paramnames.split(",")
    for param in params:
        url = re.sub("&" + param + "=(?:[^\?&]+)?", "", url)
        url = re.sub("\?" + param + "=(?:[^\?&]+)?", "?", url)\
                .replace("&&", "&")\
                .replace("?&", "?")
    if url.endswith(("?", "&")):
        url = url[:-1]
    return url
    
@register.filter
def langcode2name(code):
    return utils.language_name_from_code(code)

@register.filter
def scriptcode2name(code):
    return utils.script_name_from_code(code)

@register.filter
def countrycode2name(code):
    return utils.country_name_from_code(code)

@register.filter
def us2title(value):
    """Formats an object's nested attribute for display"""
    value = value.split(".")[-1]
    return " ".join([p.capitalize() for p in value.split("_")])

@register.filter
def getattribute(value, argstr):
    """Gets an attribute of an object dynamically from a string name"""
    args = argstr.split(".")
    leads = args[:-1]
    arg = args[-1]
    for lead in leads:
        value = getattr(value, lead)
    if hasattr(value, str(arg)):
        val = getattr(value, arg)
        if isinstance(val, types.MethodType):
            return val()
        return val
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID

@register.filter
def getitem(value, key):
    """Gets an item in a dictionary-like object."""
    return value[key]

@register.filter
def hasitem(value, key):
    """Checks if an item is in a dictionary-like object."""
    return value.get(key) is not None

@register.filter
def pagination_range(page, window=3):
    return utils.pagination_range(page.number, page.paginator.num_pages, window)


