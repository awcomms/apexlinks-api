from app import create_app

app = create_app()
app.static_folder = 'static'