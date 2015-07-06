from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_str
from django.conf import settings
from django.db import transaction
from lxml import etree
from os import path
from optparse import make_option
from elasticsearch import Elasticsearch

import re

class Command(BaseCommand):
    args = '<xml_filename xml_filename ...>'
    label = 'XML filename'
    help = 'Imports the specified XML files.'

    namespaces = dict(
        eag="http://www.ministryculture.es/"
    )

    xmlpaths = dict(
        id = "eag:eagheader/eag:eagid",
        name = "eag:archguide/eag:identity/eag:autform",
        language = "eag:eagheader/eag:languagedecl/eag:language/@langcode"
    )

    option_list = BaseCommand.option_list + (
        make_option('-p',
                    '--port',
                    action='store',
                    default="9200",
                    help='the elasticsearch port'),
        
        make_option('-i',
                    '--index',
                    action='store',
                    default=settings.DEFAULT_INDEX_TABLESPACE,
                    help='the elasticsearch index to import into'),
        
        make_option('-f',
                    '--force-update',
                    action='store_true',
                    default=False,
                    help='update documents whether or not they have changed'),
    )
    def handle(self, *filepaths, **options):
        self.es = Elasticsearch("localhost:" + options["port"])
        self.es.indices.create(index=options["index"], ignore=400)
        for filepath in filepaths:
            try:
                self.parse_file(filepath, options)
            except CommandError as e:
                print e

    def parse_file(self, filename, options):
        if not path.isfile(filename):
            raise CommandError('%s is not a file.' % filename)

        try:
            doc = etree.parse(filename)
        except etree.LxmlError as e:
            raise CommandError('could not parse %s:\n  %s' % (filename, e))
        
        self.handle_xml(filename, doc, **options)

    def handle_xml(self, filename, doc, **options):
        contents = etree.tostring(doc, encoding=unicode)
        data = dict(
                filename = filename,
                contents = contents,
        )

        def get_path_value(path):
            try:
                obj = doc.xpath(path, namespaces=self.namespaces)[0]
                if hasattr(obj, "text"):
                    return obj.text
                else:
                    return obj                    
            except IndexError:
                pass


        for key, path in self.xmlpaths.items():
            value = get_path_value(path)
            if value is not None:
                data[key] = value        
        
        if data.get("id") is None:
            raise "Unable to find id for file: %s" % filename

        self.es.index(index=options["index"], doc_type="document", id=data["id"], body=data)
        print("Indexed: %s" % filename)
        
