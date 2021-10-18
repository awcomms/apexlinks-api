from app.routes import bp

@bp.route('/', methods=['POST'])
def github_website_edit():
    # TODO-regex update pages with all in $push/src/routes/[*.svelte not ^_ or ^__]
    pass