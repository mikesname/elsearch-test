from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger

from models import Document, DocumentManager

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from django import forms

from utils import SearchPaginator

class SearchForm(forms.Form):
    q = forms.CharField(label="Search", required=False)


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
    r = s.execute().hits

    paginator = SearchPaginator(r)
    try:
        docs = paginator.page(page)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)
    context = dict(page=docs)
    return render(request, "elsearch/document_list.html", dict(page=docs, form=SearchForm()))


def document(request, doc_id):
    client = Elasticsearch()
    doc = client.get(index="xmlfacets", id=doc_id)
    context = dict(document=doc)
    return render(request, "elsearch/document.html", context)

