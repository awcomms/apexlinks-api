from app import create_app, db
from app.item_model import Item
from app.user_model import User
from app.room_model import Room
from app.models.sitemap_index import SitemapIndex
from app.models.sitemap import Sitemap
from app.models.site_page import SitePage
from app.models.mod import Mod

app = create_app()
app.static_folder = 'static'
print(app.static_folder)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Room': Room,
        'User': User,
        'Item': Item,
        'SitemapIndex': SitemapIndex,
        'Sitemap': Sitemap,
        'SitePage': SitePage,
        'Mod': Mod
    }