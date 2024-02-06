import logging
import os
from datetime import datetime
from db.models import Product, db, User
from sqlalchemy.exc import IntegrityError

LOG_FOLDER = 'logs'
log_folder_path = os.path.join(os.path.dirname(os.getcwd()), LOG_FOLDER)


def make_logger(name):
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    log_file = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(LOG_FOLDER, f"{log_file}.log")

    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    # Create a StreamHandler to log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter for the console handler
    console_formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    console_handler.setFormatter(console_formatter)

    # Get the logger and add the console handler
    logger = logging.getLogger(name)
    logger.addHandler(console_handler)

    return logger


def delete_user_products(user_id):
    product_list = Product.query.filter(Product.sellerID == user_id).all()
    if product_list:
        for product in product_list:
            db.session.delete(product)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(e)


def calculate_change(rest_amount, coin_list):
    change: list[dict] = []
    for coin in sorted(coin_list, reverse=True):
        coin_count = rest_amount // coin
        if coin_count:
            change.append({"coinType": coin, "amount": coin_count})
            rest_amount -= coin_count * coin
    return change
