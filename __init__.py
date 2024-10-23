from flask import Flask

def create_app():

    app = Flask(__name__)

    # Set a secret key for session management
    app.secret_key = 'your_very_secret_random_key'
    # Load configuration settings
    #app.config.from_pyfile('../config.py')

    # Import and register the routes from the routes.py file
    from .routes import main
    app.register_blueprint(main)

    return app
