from flask import Blueprint, request, jsonify
from db.models import User, Product, db
from utils.aux_functions import make_logger, delete_user_products
from sqlalchemy.exc import IntegrityError
from utils.auth_decorators import requires_authentication, check_user_role

logging = make_logger(__name__)
user_bp = Blueprint('user_bp', __name__, url_prefix='/users')


@user_bp.route("", methods=["GET"])
@requires_authentication
def get_users():
    users = User.query.all()
    user_list = [{"id": u.id, "username": u.username, "role": u.role, "deposit": u.deposit, "password": u.password} for
                 u in users]
    logging.info(f"getting users info : {user_list}")
    return jsonify(user_list), 200


@user_bp.route("", methods=["POST"])
def add_user():
    data = request.json
    new_user = User(username=data["username"], role=data["role"], deposit=data.get('deposit', 0))
    new_user.set_password(data["password"])
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as ie:
        db.session.rollback()
        error_info = str(ie.orig) if ie.orig else str(ie)
        return jsonify({"status": "error", "message": error_info}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": e}), 500

    logging.info(f"User added - ID: {new_user.id}, Username: {new_user.username}, Role: {new_user.role}")

    return jsonify(
        {"status": "success", "id": new_user.id, "username": new_user.username, "role": new_user.role,
         "deposit": new_user.deposit}), 201


@user_bp.route("/<int:user_id>", methods=["PUT"])
@requires_authentication
def update_user(user_id):
    header_user_id = request.headers.get("User-Id", type=int)
    if header_user_id != user_id:
        """
            check if the provided User-Id in the headers is the same in the api path
            - the user can only update his own record
        """
        logging.warning(f"User ID: {header_user_id} is trying to update User ID: {user_id} data")
        return jsonify({"status": "error",
                        "message": "User can only change his own information please provide correct User-Id & Password in the request headers"}), 403
    data = request.json
    logging.debug(f"request data {data}")
    user = User.query.get(user_id)
    logging.debug(f"user: {user}")

    if user and user.role == "seller" and data['role'] == "buyer":
        """
            the condition checks if the user role will change from seller to buyer
            which will force delete all the user related product as he will not be selling anymore
        """
        try:
            delete_user_products(user_id)
            logging.debug(f"all the products of user_id {user_id} have been deleted")
        except Exception as e:
            logging.error(f"delete_user_products error: {e}")

    if user:
        user.username = data["username"]
        user.role = data["role"]
        user.deposit = data["deposit"]
        user.set_password(data["password"])
        try:
            db.session.commit()
        except IntegrityError as ie:
            db.session.rollback()
            error_info = str(ie.orig) if ie.orig else str(ie)
            logging.error(f"{error_info}")
            return jsonify({"status": "error", "message": error_info}), 400
        except Exception as e:
            logging.error(f"{e}")
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

        logging.info(
            f"User updated - ID: {user.id}, Username: {user.username}, Role: {user.role}, deposit: {user.deposit}")

        return jsonify({"id": user.id, "username": user.username, "role": user.role, "deposit": user.deposit}), 200

    logging.error(f"User {user_id} does not exist")

    return jsonify({"error": f"User {user_id} not found"}), 404


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@requires_authentication
def remove_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        try:
            db.session.commit()
            logging.info(
                f"User removed - ID: {user.id}, Username: {user.username}, Role: {user.role}, deposit: {user.deposit}")
            try:
                delete_user_products(user_id)
                logging.debug(f"all the products of user_id {user_id} have been deleted")
            except Exception as e:
                logging.error(f"delete_user_products error: {e}")
                raise Exception(e)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error while removing user with id={user_id} error: {e}")
            return jsonify({"status": "error", "message": e}), 500

        return jsonify({"success": True})

    return jsonify({"error": f"User with id={user_id} not found"}), 404
