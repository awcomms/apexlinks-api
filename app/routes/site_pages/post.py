from app.routes import bp

@bp.route('/', methods=['POST'])
def github_website_edit():
    """ TODO-regex update pages with all in $push/src/routes/[*.svelte not ^_ or ^__]
        get query of pages edited in push
        for page in query:
            if not page.sitemap:
                Sitemap.add_new_page(page)
            page.new_mod()
    """
    return ''