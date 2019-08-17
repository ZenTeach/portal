import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from .models import ClassQuiz, QuizGrade, SchoolClass, Student, Teacher

db = SQLAlchemy()

def create_app(script_info=None):
	app = Flask(__name__)

	app_settings = os.getenv('APP_SETTINGS')
	app.config.from_object(app_settings)

	db.init_app(app)
	from . import models
	from flask_migrate import Migrate, MigrateCommand
	migration_directory= os.path.join('server', 'models', 'migrations')
	migrate = Migrate(app, db, directory=migration_directory)

	# Register bluprints
	from .api import api as api_blueprint
	app.register_blueprint(api_blueprint, url_prefix='/api/v1')

	@app.shell_context_processor
	def ctx():
		return {'app': app, 'db': db}

	return app