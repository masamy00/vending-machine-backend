from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    User Model with constrains
        - role field value should be in ['seller', 'buyer']
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    deposit = db.Column(db.Float, nullable=True, default=0)
    role = db.Column(db.String(128), nullable=False)

    __table_args__ = (db.CheckConstraint("role IN ('seller', 'buyer')", name="check_valid_role"),)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Product(db.Model):
    """
        User Model with constrains
            - cost  field value should be Multiples of five,
            as the machine also accepts this way & this how it will return change

        Add relation one-to-many from User id to Product sellerID
        """
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(50), nullable=False)
    amountAvailable = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    sellerID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (
        db.CheckConstraint('cost % 5 = 0', name='check_cost_divisible_by_5'),
    )

    seller = db.relationship('User', backref='products')
