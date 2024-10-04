from flask import Flask
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)

    # Laden der Konfiguration
    app.config.from_object('config.Config')

    # Initialisieren der Erweiterungen
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrieren der Routen
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Initialisieren der Kategorien
    with app.app_context():
        from .models import init_categories
        init_categories()

    return app