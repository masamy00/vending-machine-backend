from flask import Blueprint, request, jsonify
from db.models import User, Product, db
from utils.aux_functions import make_logger, calculate_change
from utils.auth_decorators import requires_authentication, check_user_role

logging = make_logger(__name__)
operations_bp = Blueprint('operations_bp', __name__)
acceptable_coins = [5, 10, 20, 50, 100]


@operations_bp.route('/deposit', methods=['POST'])
@requires_authentication
@check_user_role(['buyer'])
def perform_deposit():
    data = request.json
    user_id = request.headers.get('User-Id', type=int)
    deposit_amount = data["depositAmount"]
    if deposit_amount not in acceptable_coins:
        logging.error(f'Invalid operation deposit for user_id: {user_id}, reason: invalid coin type')
        return jsonify({"status": "error", "message": "Invalid coin type"}), 403
    user = User.query.get(user_id)

    user.deposit += deposit_amount
    try:
        db.session.commit()
        logging.info(f'successfully deposited ammount for user id: {user_id}')
        return jsonify({"status": "success", "message": f"current available amount {user.deposit}"}), 200
    except Exception as e:
        logging.error("e")
        return jsonify({"status": "error", "message": e}), 500


@operations_bp.route('/buy', methods=['POST', 'GET'])
@requires_authentication
@check_user_role(['buyer'])
def perform_buy():
    check_out_list: list[dict] = request.json
    valid_checkout_list = all(
        len(d) == 2 and isinstance(d.get("productId", None), (int, float)) and isinstance(d.get("amount", None),
                                                                                          (int, float))
        for d in check_out_list
    ) if isinstance(check_out_list, list) and len(check_out_list) > 0 else False

    if not valid_checkout_list:
        logging.error("invalid checkout list data types")
        return jsonify({"status": "error",
                        "message": "invalid list key, typical object should be: {\"productId\": int, \"amount\": int, float}"}), 400
    user_id = request.headers.get('User-Id', type=int)
    user = User.query.get(user_id)
    user_deposit = user.deposit
    product_cost = {}

    for item in check_out_list:
        """
        loop to extract the price list and also check for some conditions like:
            - product existence
            - product requested amount is more than the available amount 
        """
        product_id = item["productId"]
        product = Product.query.get(product_id)
        if product:
            if product.amountAvailable < item["amount"]:
                logging.error("product is not available")
                return jsonify({"status": "error",
                                "message": f"product {product.productName} has only {product.amountAvailable} left"}), 400
            product_cost[product_id] = product.cost
        else:
            logging.error(f"product with id {product_id} not found")
            return jsonify({"status": "error", "message": f"product with id {product_id} not found"}), 404

    check_out_amount = sum(obj['amount'] * product_cost[obj['productId']] for obj in check_out_list)

    if check_out_amount > user_deposit:
        """
            check out amount is more than the available amount for user
        """
        logging.error(
            f"checkout amount is greater than user deposit, user_id={user_id}, user_deposit= {user_deposit},amount={check_out_amount}")
        return jsonify({"status": "error",
                        "message": f"checkout amount is greater than user deposit, user_id={user_id}, user_deposit= {user_deposit},amount={check_out_amount}"}), 400

    rest_amount = user_deposit - check_out_amount
    change = calculate_change(rest_amount, sorted(acceptable_coins, reverse=True))
    user.deposit = 0
    try:
        db.session.commit()
        return jsonify({"status": "success", "totalSpent": check_out_amount, "change": change}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"status": "error", "message": e}), 500


@operations_bp.route('/reset', methods=['POST', 'GET'])
@requires_authentication
@check_user_role(['buyer'])
def perform_rest():
    user_id = request.headers.get('User-Id', type=int)
    user = User.query.get(user_id)
    change = calculate_change(user.deposit, sorted(acceptable_coins, reverse=True))
    user.deposit = 0
    try:
        db.session.commit()
        return jsonify({"status": "success", "change": change}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"status": "error", "message": e})
