import os, json
import requests
from flask import current_app
from app.routes import bp
from app.vars import schemaorg


domainIncludes = 'schema:domainIncludes'
organization = 'schema:Organization'
subParents = [
    'schema:Airline',
    'schema:Consortium',
    'schema:Corporation',
    'schema:EducationalOrganization',
    'schema:FundingScheme',
    'schema:GovernmentOrganization',
    'schema:LibrarySystem',
    'schema:LocalBusiness',
    'schema:MedicalOrganization',
    'schema:NGO',
    'schema:NewsMediaOrganization',
    'schema:PerformingGroup',
    'schema:Project',
    'schema:ResearchOrganization',
    'schema:SportsOrganization',
    'schema:WorkersUnion'
]

subClassOf = 'rdfs:subClassOf'
classType = 'rdfs:Class'


@bp.route('/users/schema', methods=['GET'])
def get_schema():
    schemaorgPath = os.path.join(current_app.static_folder, 'schemaorg.jsonld')
    resSchemas = []
    try:
        all = requests.get(schemaorg).json()
    except:
        all = json.load(open(schemaorgPath, encoding='utf8'))
    graph = all['@graph']

    parentClasses = [organization] + subParents
    x = []

    def get_sub_classes(_subClasses):
        _newSubClasses = []
        for schema in graph:
            if schema['@type'] == classType and subClassOf in schema:
                for subClass in schema[subClassOf]:
                    if isinstance(subClass, dict):
                        sub_class_id = subClass['@id']
                        if sub_class_id in _subClasses and sub_class_id not in _newSubClasses:
                            x.append(sub_class_id)
                    elif subClass == '@id':
                        sub_class_id = schema[subClassOf][subClass]
                        if sub_class_id in _subClasses and sub_class_id not in _newSubClasses:
                            x.append(sub_class_id)
                if len(x):
                    for s in x:
                        if s not in parentClasses:
                            parentClasses.append(s)
                        # else:
                        #     _newSubClasses.remove(s)

                    get_sub_classes(x)

    # get_sub_classes(start)
    # print('parentClasses', start)

    for idx, schema in enumerate(graph):
        if schema['@type'] == 'rdf:Property' and domainIncludes in schema:
            domainIncludesField = schema[domainIncludes]
            for domain in domainIncludesField:
                if (isinstance(domain, dict) and '@id' in domain and domain['@id'] in parentClasses) or \
                        (domain == '@id' and domainIncludesField[domain] in parentClasses):
                    schema['text'] = schema['rdfs:label']
                    schema['label'] = schema['rdfs:label']
                    schema['id'] = idx  # text_to_num(schema['@id'])
                    if schema not in resSchemas:
                        resSchemas.append(schema)
    return {'schema': resSchemas}
