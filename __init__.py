import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Person Class/Model


class Person(db.Model, Base):
    email = db.Column(db.String(25), primary_key=True)
    children = relationship("Person_product")

    def __init__(self, email):
        self.email = email

# Product Class/Model


class Product(db.Model, Base):
    sku = db.Column(db.String(50), primary_key=True)
    json_data = db.Column(db.JSON)

    def __init__(self, sku, json_data):
        self.sku = sku
        self.json_data = json_data


class Person_product(db.Model, Base):
    email = Column(ForeignKey(
        'person.email', ondelete="CASCADE"), primary_key=True)
    sku = Column(ForeignKey('product.sku', ondelete="CASCADE"),
                 primary_key=True)
    drop_price = db.Column(db.Float)
    drop_discount = db.Column(db.Float)
    child = relationship("Product")

    def __init__(self, sku, email, drop_price, drop_discount):
        self.sku = sku
        self.email = email
        self.drop_discount = drop_discount
        self.drop_price = drop_price

# Product Schema -- para la serializacion, esto se retorna


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('sku', 'json_data')


# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Product


@app.route('/product', methods=['POST'])
def add_product():
    sku = request.json['sku']
    json_data = request.json['json_data']
    email = request.json['email']
    drop_price = request.json['drop_price']
    drop_discount = request.json['drop_discount']

    if not isinstance(sku, str):
        return "sku debe estar compuesto por caracteres"
    try:
        json.loads(json.dumps(json_data))
    except ValueError as err:
        return "json_data debe ser formato JSON"
    if not isinstance(email, str):
        return "email debe estar compuesto por caracteres"
    if not isinstance(drop_price, int):
        return "drop_price debe ser un numero"
    if not isinstance(drop_discount, int):
        return "drop_discount debe ser un numero"

    product = Product.query.get(sku)
    if product is None:
        product = Product(sku, json_data)
        db.session.add(product)

    person = Person.query.get(email)
    if person is None:
        person = Person(email)
        db.session.add(person)

    person_product = Person_product.query.filter_by(
        email=email, sku=sku).first()
    if person_product is None:
        person_product = Person_product(sku, email, drop_price, drop_discount)
        db.session.add(person_product)
    else:
        person_product.drop_price = drop_price
        person_product.drop_discount = drop_discount

    db.session.commit()

    return product_schema.jsonify(product)

# # Get All Products
# @app.route('/product', methods=['GET'])
# def get_products():
#   all_products = Product.query.all()
#   result = products_schema.dump(all_products)
#   return jsonify(result)

# # Get Single Products
# @app.route('/product/<sku>', methods=['GET'])
# def get_product(sku):
#   product = Product.query.get(sku)
#   return product_schema.jsonify(product)

# # Update a Product
# @app.route('/product/<sku>', methods=['PUT'])
# def update_product(sku):
#   product = Product.query.get(sku)

#   sku = request.json['sku']
#   json_data = request.json['json_data']

#   product.sku = sku
#   product.json_data = json_data

#   db.session.commit()

#   return product_schema.jsonify(product)

# # Delete Product
# @app.route('/product/<sku>', methods=['DELETE'])
# def delete_product(sku):
#   product = Product.query.get(sku)
#   db.session.delete(product)
#   db.session.commit()

#   return product_schema.jsonify(product)


# Run Server


if __name__ == '__main__':
    app.run(debug=True)

def getApp():
    return app