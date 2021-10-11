import requests
from app.api import bp
from app.resources import schema_dot_org

domainIncludes = 'schema:domainIncludes'
localBusiness = 'schema:LocalBusiness'
organization = 'schema:Organization'
subClassOf = 'rdfs:subClassOf'

@bp.route('/schema/organization', methods=['GET'])
def get_schema():
    id = 1
    subClasses = []
    localBusinessSchemas = []
    all = requests.get(schema_dot_org).json()
    graph = all['@graph']
    
    def get_sub_classes():
        _subClasses = [organization]
        _newSubClasses = []
        for schema in graph:
            if schema['@type'] == 'rdf:Class':
                for subClass in schema[subClassOf]:
                    if isinstance(subClass, dict):
                        sub_class_id = subClass['@id']
                        if sub_class_id in _subClasses:
                            if sub_class_id not in _newSubClasses:
                                _newSubClasses.append(sub_class_id)
                    elif subClass == '@id':
                        sub_class_id = schema[subClassOf][subClass]
                        if sub_class_id in _subClasses:
                            if sub_class_id not in _newSubClasses:
                                _newSubClasses.append(sub_class_id)
                if len(_newSubClasses):
                    for s in _newSubClasses:
                        if s not in _subClasses:
                            _subClasses.append(s)
                    get_sub_classes()
    subClasses = get_sub_classes()

    for schema in graph:
        if schema['@type'] == 'rdf:Property' and domainIncludes in schema:
            for domain in schema[domainIncludes]:
                if isinstance(domain, dict):
                    if domain['@id'] in subClasses:
                        schema['text'] = schema['rdfs:label']
                        print('schema text', schema['text'])
                        schema['id'] = id
                        id += 1
                        localBusinessSchemas.append(schema)
                elif domain == '@id':
                    if schema[domainIncludes][domain] in subClasses:
                        schema['text'] = schema['rdfs:label']
                        print('schema text', schema['text'])
                        schema['id'] = id
                        id += 1
                        localBusinessSchemas.append(schema)
    return {'schemas': localBusinessSchemas}