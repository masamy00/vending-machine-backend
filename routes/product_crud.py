from flask import Blueprint, request, jsonify
from db.models import User, Product, db
from utils.aux_functions import make_logger
from sqlalchemy.exc import IntegrityError
from utils.auth_decorators import requires_authentication, check_user_role

logging = make_logger(__name__)
product_bp = Blueprint('product_bp', __name__, url_prefix='/products')


@product_bp.route("", methods=["GET"])
@requires_authentication
def get_products():
    products = Product.query.all()
    logging.debug(f"products: {products}")
    product_list = [{"id": p.id, "productName": p.productName, "amountAvailable": p.amountAvailable, "cost": p.cost,
                     "sellerID": p.sellerID} for
                    p in products]
    logging.info(f"getting products info : {product_list}")
    return jsonify(product_list), 200


@product_bp.route("", methods=["POST"])
@check_user_role(['seller'])
@requires_authentication
def add_product():
    data = request.json
    seller = User.query.get(request.headers.get("User-Id", type=int))
    logging.debug(seller.role)

    new_product = Product(productName=data["productName"], amountAvailable=data.get("amountAvailable", 0),
                          cost=data['cost'], seller=seller)

    try:
        db.session.add(new_product)
        logging.info(f"added new product {data["productName"]}")
        db.session.commit()
        return jsonify(
            {"status": "success", "id": new_product.id, "productName": new_product.productName,
             "amountAvailable": new_product.amountAvailable,
             "cost": new_product.cost, "sellerID": new_product.sellerID}), 201
    except IntegrityError as ie:
        logging.error(f"IntegrityError: {ie}")
        db.session.rollback()
        error_info = str(ie.orig) if ie.orig else str(ie)
        return jsonify({"status": "error",
                        "message": error_info}), 400

    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify({"status": "error",
                        "message": e}), 500


@product_bp.route("/<int:product_id>", methods=["PUT"])
@check_user_role(['seller'])
@requires_authentication
def update_product(product_id):
    data = request.json
    product = Product.query.get(product_id)
    if product:
        seller_id = product.sellerID
        if seller_id != request.headers.get('User-Id', type=int):
            logging.error(f"seller with id {request.headers['User-Id']} is trying to update product {product_id}")
            return jsonify({"status": "error", "message": "Unauthorized access. seller is not the product owner"}), 403

        if data['sellerID'] != seller_id:
            logging.error(f"product change of sellerID {seller_id} is blocked")
            return jsonify({"status": "error", "message": "product seller cannot be changed"}), 400

        product.productName = data["productName"]
        product.cost = data["cost"]
        product.amountAvailable = data["amountAvailable"]
        try:
            db.session.commit()
            return jsonify(
                {"status": "success", "id": product.id, "productName": product.productName,
                 "amountAvailable": product.amountAvailable,
                 "cost": product.cost, "sellerID": product.sellerID}), 200
        except IntegrityError as ie:
            logging.error(f"{ie}")
            db.session.rollback()
            error_info = str(ie.orig) if ie.orig else str(ie)
            return jsonify({"status": "error", "message": error_info}), 400
        except Exception as e:
            logging.error(f"{e}")
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "Product not found"}), 404


@product_bp.route("/<int:product_id>", methods=["DELETE"])
@requires_authentication
@check_user_role(['seller'])
def remove_product(product_id):
    product = Product.query.get(product_id)
    if product:
        seller_id = product.sellerID
        if seller_id != request.headers.get('User-Id', type=int):
            logging.error(f"seller with id {request.headers['User-Id']} is trying to remove product {product_id}")
            return jsonify({"status": "error", "message": "Unauthorized access. seller is not the product owner"}), 403
        db.session.delete(product)
        try:
            db.session.commit()
            return jsonify({"status": "success", "message": "successfully removed product"}), 200
        except Exception as e:
            logging.error(f"error while deleting product with id={product_id}, error: {e}")
            db.session.rollback()

    return jsonify({"status": "error", "message": "Product not found"}), 404
