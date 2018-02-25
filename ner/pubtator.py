"""Extract bio concepts from pubtator
"""

import json
import requests

def load_from_uri(uri):
    r = requests.get(uri)
    r.encoding = 'utf-8'

    return r.text

def get_bio_concepts(doc_id, concept='all'):
    if concept == 'all':
        concept = 'BioConcept'

    uri = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/%s/%d/JSON/' % (concept, doc_id)
    raw_data = load_from_uri(uri)
    
    if raw_data.startswith('[Error]'):
        return {}
    
    data = json.loads(raw_data)
    bioconcepts = []
    for denotation in data['denotations']:
        bioconcepts.append({
            'entity': data['text'][int(denotation['span']['begin']):int(int(denotation['span']['end']))],
            'type': denotation['obj'].split(':')[0]
        })

    return bioconcepts