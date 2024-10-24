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

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    
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
            # Drop all tables
            db.drop_all()
            logger.info("Existing tables dropped successfully")
            
            # Recreate tables
            db.create_all()
            db.session.commit()
            logger.info("Database tables reset successfully")
            
        except Exception as e:
            logger.error(f"Database reset error: {str(e)}")
            
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
