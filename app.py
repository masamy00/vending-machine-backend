from flask import Flask, request, jsonify
from utils.aux_functions import make_logger
from routes.user_crud import user_bp
from routes.product_crud import product_bp
from routes.operations_endpoints import operations_bp
from db.models import db

app = Flask(__name__)
logging = make_logger(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///vending_machine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(user_bp)
logging.info("Register user blueprint")
app.register_blueprint(product_bp)
logging.info("Register product blueprint")
app.register_blueprint(operations_bp)
logging.info("Register operations blueprint")


@app.before_request
def before_request():
    """
    first layer of checking
        - request method should be in [GET, POST, PUT, DELETE]
        - request Content-Type should be application/json
    """
    if request.method not in ['GET', 'POST', 'PUT', 'DELETE']:
        return jsonify(
            {"error": f"Unsupported API Method {request.method}. only [GET, POST, PUT, DELETE] is accepted"}), 415
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Unsupported Media Type. Please send content with 'application/json' type."}), 415


if __name__ == "__main__":
    app.run(debug=True, port=3000)
