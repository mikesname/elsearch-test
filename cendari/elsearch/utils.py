import json
import datetime
from types import MethodType  
import babel

from django.core.paginator import Paginator, Page, InvalidPage, EmptyPage
from django.utils import translation

import data

# 
# Functions that convert from an ISO code into
# the (localised) name. 
# TODO: Possible optimisation to be had by
# caching the language code, although I'm 
# not sure it's a very expensive operation.
#
def language_name_from_code(code, locale=None):
    """Get lang display name."""
    if locale is None:
        locale = translation.get_language().split("-")[0]
    return babel.Locale(locale).languages.get(code, code)


def country_name_from_code(code, locale=None):
    """Get the country name from a 2 letter code
    defined in ISO 3166."""
    if locale is None:
        locale = translation.get_language().split("-")[0]
    return babel.Locale(locale).territories.get(code.upper(), code)


def script_name_from_code(code, locale=None):
    """Get the script name from a 4 letter code
    defined in ISO 15924."""
    if locale is None:
        locale = translation.get_language().split("-")[0]
    return babel.Locale(locale).scripts.get(code, code)


def language_choices(lang=None):
    if lang is None:
        lang = translation.get_language().split("-")[0]
    for code, name in data.LANGUAGE_CODES:
        yield (code, language_name_from_code(code, locale=lang) or name) 


def script_choices(lang=None):
    if lang is None:
        lang = translation.get_language().split("-")[0]
    for code, name in data.SCRIPT_CODES:
        yield (code, script_name_from_code(code, locale=lang) or name) 


def country_choices(lang=None):
    if lang is None:
        lang = translation.get_language().split("-")[0]
    for code, name in data.COUNTRY_CODES:
        yield (code, country_name_from_code(code, locale=lang) or name) 

class SearchPaginator(Paginator):    
    def __init__(self, hits):
        self.hits = hits

    @property
    def num_pages(self):
        found = len(self.hits)
        if found:
            rem = self.hits.total % len(self.hits)
            div = self.hits.total / len(self.hits)
            return div if rem == 0 else div + 1
        else:
            return 0

    @property
    def page_range(self):
        return range(1, self.num_pages + 1)

    def has_next(self):
        return self.page < self.num_pages

    def has_previous(self):
        return self.page > 1

    def start_index(self):
        return self.page_range[0]

    def end_index(self):
        return self.page_range[-1]

    def next_page_number(self):
        if self.page >= self.num_pages:
            raise InvalidPage()

    def page(self, page):
        return Page(self.hits, page, self)    


