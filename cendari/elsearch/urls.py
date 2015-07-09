from django.conf.urls import patterns, url

from elsearch import views

urlpatterns = patterns("",
    url(r"^$", views.search, name="document_list"),
    url(r"^document/(?P<doc_id>[-\w\.]+)/?$", views.document, name="document"),
    url(r"^download/(?P<doc_id>[-\w\.]+)/?$", views.download, name="download"),
)
