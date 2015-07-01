from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger

from models import Document, DocumentManager

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from django import forms

from utils import SearchPaginator, language_name_from_code

class SearchForm(forms.Form):
    q = forms.CharField(label="Search", required=False)

class FacetClass(object):
    def __init__(self, param, tag, render=lambda s: s):
        self.tag = tag
        self.param = param
        self.render = render

    def format_param(self, value):
        return "%s=%s" % (self.param, value)

class Facet(object):
    def __init__(self, value, count, applied, fclass):
        self.value = value
        self.count = count
        self.applied = applied
        self.fclass = fclass

    def as_param_kv(self):
        return "%s=%s" % (self.fclass.param, self.value)

    def render(self):
        return self.fclass.render(self.value)

FACETS = [
    FacetClass("lang", "languages", language_name_from_code)
]


def get_facets(request, search):
    """Apply term facets and filtering to the search"""
    fdict = {}
    for fclass in FACETS:
        fdict[fclass.tag] = {"terms": {"field": fclass.tag}}

    # Apply filtering based on the incoming request params
    filters = {}
    for fclass in FACETS:
        for value in request.GET.getlist(fclass.param):
            filters[fclass.tag] = value
    if filters:
        search = search.filter("term", **filters)
    return search.extra(facets=fdict)

def parse_facets(request, data):
    """Return a list of facet-class/value tuples"""
    facets = []
    for fclass in FACETS:
        fdata = getattr(data, fclass.tag)
        if not fdata:            
            continue
        terms =  fdata.get("terms")
        if terms:
            inreq = request.GET.getlist(fclass.param)
            parsed_facets = [Facet(value["term"], value["count"], value["term"] in inreq, fclass)\
                    for value in terms]
            facets.append((fclass, parsed_facets))
    return facets


def search(request):
    
    form = SearchForm(request.GET)
    query = form.data.get("q", None)
    try:
        page = int(request.GET.get("page"))
    except (ValueError, TypeError):
        page = 1
    start = max(0, page - 1)

    client = Elasticsearch()
    s = Search(using=client, index="xmlfacets")
    if query:
        s = s.query("match", text=query)
    s = s[start:start+20]
    s = get_facets(request, s)
    print(s.to_dict())
    r = s.execute()

    print("Facets: %s" % r.facets.to_dict())
    facets = parse_facets(request, r.facets)
    paginator = SearchPaginator(r.hits)
    try:
        docs = paginator.page(page)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)
    context = dict(page=docs)
    return render(request, "elsearch/document_list.html", dict(page=docs, form=form, facets=facets))


def document(request, doc_id):
    client = Elasticsearch()
    doc = client.get(index="xmlfacets", id=doc_id)
    context = dict(document=doc)
    return render(request, "elsearch/document.html", context)

