from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import Document, DocumentManager

def document_list(request):
    query = request.GET.get("q")
    page = request.GET.get("page")
    paginator = Paginator(DocumentManager.find_all("*" if query is None else query), per_page = 20)
    try:
        docs = paginator.page(page)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)
    context = dict(page=docs)
    return render(request, "elsearch/document_list.html", dict(page=docs))

def document(request, doc_id):
    doc = DocumentManager.find_one(id=doc_id)
    context = dict(document=doc)
    return render(request, "elsearch/document.html", context)

