from app.extensions import socketio, Migrate, SQLAlchemy, Flask




# Create and configure application
app = Flask(__name__)
app.secret_key = "Sb39MDCIyj1kWgEKVzpmkQ"

# Production Server:
app.config["SQLALCHEMY_DATABASE_URI"] =  "postgresql://postgres:cgd2ecFCaE4a4cGA4Dc61GCAEFB5DGF4@viaduct.proxy.rlwy.net:57688/railway"

# Development Server:
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:dE4G1Aa46D3Efaa3fGcBb664BFCf5E3A@monorail.proxy.rlwy.net:49454/railway"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app)
socketio.init_app(app)
migrate = Migrate(app, db)


from app import routes
from app import events