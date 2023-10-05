from app.extensions import socketio, Migrate, SQLAlchemy, Flask




# Create and configure application
app = Flask(__name__)
app.secret_key = "Sb39MDCIyj1kWgEKVzpmkQ"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Wj7gWQuu849VNDMYSY3j@containers-us-west-191.railway.app:7456/railway"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app)
socketio.init_app(app)
migrate = Migrate(app, db)


from app import routes
from app import events