"""The app module, containing the app factory function."""
import flask_login
from flask import Flask, g, redirect, render_template
from flask_social_auth import user, public
from flask_social_auth.extensions import db, login_manager, bcrypt
from flask_social_auth.settings import DevConfig
from social.apps.flask_app.default.models import init_social
from social_flask.routes import social_auth
from social.apps.flask_app.template_filters import backends
from social.exceptions import SocialAuthBaseException

db = SQLAlchemy()

def create_app(config_object=DevConfig):
    """The application factory.

    Explained here: http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    register_blueprints(app)
    register_before_requests(app)
    register_errorhandlers(app)
    register_context_processors(app)
    register_teardown_appcontext(app)
    
    db.init_app(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    init_social(app, db.session)


def register_blueprints(app):
    """Register own and 3rd party blueprints."""
    app.register_blueprint(social_auth)

    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(public.views.blueprint)


def register_errorhandlers(app):
    """Add errorhandlers to the app."""
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)

    def social_error(error):
        if isinstance(error, SocialAuthBaseException):
            return redirect('/socialerror')
    app.errorhandler(500)(social_error)


def register_before_requests(app):
    """Register before_request functions."""
    def global_user():
        g.user = flask_login.current_user
    app.before_request(global_user)


def register_context_processors(app):
    """Register context_processor functions."""
    def inject_user():
        try:
            return {'user': g.user}
        except AttributeError:
            return {'user': None}
    app.context_processor(inject_user)
    app.context_processor(backends)


def register_teardown_appcontext(app):
    """Register teardown_appcontext functions."""
    def commit_on_success(error=None):
        if error is None:
            db.session.commit()
    app.teardown_appcontext(commit_on_success)
