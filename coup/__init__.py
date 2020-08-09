import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from AppConfig import AppConfig

app = Flask(__name__)
app.config.from_object(AppConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.init_app(app)

# Import relevant flask handling modules here, to avoid circular imports
from coup import routes, socketio_handlers, models
