
from django.core.urlresolvers import reverse

from pyelasticsearch import ElasticSearch

class Document(object):
    """A document, indexed in Elasticsearch"""

    def __init__(self, id, name, filename, creator, data=None):
        self.id = id
        self.name = name
        self.filename = filename
        self.creator = creator
        self.data = {} if data is None else data

    def __unicode__(self):
        return "Document: %s: '%s'" % (self.id, self.name)

    def get_absolute_url(self):
        return reverse("document", kwargs=dict(doc_id=self.id))
    

class DocumentManager(object):
    test_docs = [
            Document(
                "test-doc-1",
                "This is test document 1",
                "test-doc-1.xml",
                "Bob"
            ),
            Document(
                "test-doc-2",
                "This is test document 2",
                "test-doc-2.xml",
                "Alice"
            )
    ]

    @classmethod
    def find_all(self, query = "*", start=0, size=20):
        es = ElasticSearch()
        res = es.search(query, index="xmlfacets", es_from=start, size=size)
        print("Result: %s" % res)
        return [d for d in self.test_docs if query in d.name]

    @classmethod
    def find_one(self, id):
        return next(d for d in self.test_docs if d.id == id)

