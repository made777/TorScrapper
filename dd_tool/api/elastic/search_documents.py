import sys
import base64
from datetime import datetime
from config import es as default_es

def get_context(terms, field = "text", size=500, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    if len(terms) > 0:
        query = {
            "query": {
                "match": {
                    field: {
                        "query": ' '.join(terms[0:]),
                        "operator" : "and"
                    }
                }
             },
            "highlight" : {
                "fields" : {
                    field: {
                        "fragment_size" : 100, "number_of_fragments" : 1
                    }
                }
            },
            "fields": ["url"]
        }

        res = es.search(body=query, index=es_index, doc_type=es_doc_type, size=size, request_timeout=600)
        hits = res['hits']

        context = {}
        for hit in hits['hits']:
            context[hit['fields']['url'][0]] = hit['highlight']['text'][0]

        return context

def term_search(field, queryStr, start=0, pageCount=100, fields=[], es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    if len(queryStr) > 0:
        query = {
            "query" : {
                "match": {
                    field: {
                        "query": ' '.join(queryStr),
                        "minimum_should_match":"100%"
                    }
                }
            },
            "fields": fields
        }

        res = es.search(body=query, index=es_index, doc_type=es_doc_type, from_=start, size=pageCount)
        hits = res['hits']['hits']

        results = []
        for hit in hits:
            if hit.get('fields') is None:
                print hit
            else:
                fields = hit['fields']
                fields['id'] = hit['_id']
                fields['score'] = hit['_score']
                results.append(fields)

        return {"total": res['hits']['total'], 'results':results}

def get_image(url, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    if url:
        query = {
            "query": {
                "term": {
                    "url": url
                }
            },
            "fields": ["thumbnail", "thumbnail_name"]
        }
        res = es.search(body=query, index=es_index, doc_type=es_doc_type, size=500)

        hits = res['hits']['hits']
        if (len(hits) > 0):
            try:
                img = base64.b64decode(hits[0]['fields']['thumbnail'][0])
                img_name = hits[0]['fields']['thumbnail_name'][0]
                return [img_name, img]
            except KeyError:
                print "No thumbnail found"
        else:
            print "No thumbnail found"
    return [None, None]