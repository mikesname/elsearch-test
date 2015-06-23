from django.conf.urls import patterns, url

from elsearch import views

urlpatterns = patterns("",
    url(r"^$", views.document_list, name="document_list"),
    url(r"^(?P<doc_id>[-\w]+)/$", views.document, name="document")
)
