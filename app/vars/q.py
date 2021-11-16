schemaorg = 'https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/releases/13.0/schemaorg-all-https.jsonld'
host = 'https://apexlinks.org'
api_host = 'https://api.apexlinks.org'

sitemap_entry_limit = 50000
sitemap_index_entry_limit = 50000
sitemap_index_byte_limit = 52428800
sitemap_byte_limit = 52428800

global_priority = '1'

sitemap_namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
user_change_freq = 'always'

urlset_attribs = {
    'xmlns': sitemap_namespace
}

sitemapindex_attribs = {
    'xmlns': sitemap_namespace
}

sitemap_attribs = {
    'xmlns': sitemap_namespace
}

default_user_fields = [
    'name',
    'email',
    'telephone',
]

_default_user_fields = [
    'name',
    'latitude',
    'longitude',
    'country',
    'state',
    'city',
    'town',
    'email',
    'telephone',
]