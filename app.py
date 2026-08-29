import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url():
    """Return a SQLAlchemy-compatible database URL for every environment."""
    database_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
    )

    # Some providers still expose the deprecated postgres:// scheme.
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Vercel's filesystem is read-only except for /tmp. This fallback makes
    # preview deployments boot, while production should use a hosted database.
    return database_url or "sqlite:////tmp/ocbooks.db"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"].update({
            "pool_recycle": 300,
            "pool_size": 5,
            "max_overflow": 5,
        })
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Import models and blueprints
        import models
        import auth
        import books
        
        # Register blueprints
        app.register_blueprint(auth.bp)
        app.register_blueprint(books.bp)
        
        try:
            # create_all is idempotent. Never destroy user data during a cold start.
            db.create_all()
            db.session.commit()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return models.User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {str(e)}")
            return None
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('books.library'))
        
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
