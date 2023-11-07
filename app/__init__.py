from app.extensions import socketio, Migrate, SQLAlchemy, Flask, Mail




# Create and configure application
app = Flask(__name__)
app.secret_key = "Sb39MDCIyj1kWgEKVzpmkQ"

# Production Server:
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Wj7gWQuu849VNDMYSY3j@containers-us-west-191.railway.app:7456/railway"

# Development Server:
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:h6CIkVq5BOGYvuf9bYWd@containers-us-west-76.railway.app:6936/railway"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = "587"
app.config["MAIL_USERNAME"] = "lptennisladder"
app.config["MAIL_PASSWORD"] = "swcm dtum jlqr ltzr"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL)USE_SSL"] = False


app.app_context().push()
db = SQLAlchemy(app)
socketio.init_app(app)
migrate = Migrate(app, db)
mail = Mail()
mail.init_app(app)


from app import routes
from app import events