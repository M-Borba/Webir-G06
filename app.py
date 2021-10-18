from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Person Class/Model
class Person(db.Model):
  email = db.Column(db.String(25), primary_key=True)
  products = db.relationship('Product', backref='owner')

  def __init__(self, email):
    self.email = email

# Product Class/Model
class Product(db.Model):
  sku = db.Column(db.String(50), primary_key=True)
  json_data = db.Column(db.JSON)
  owner_id = db.Column(db.Integer, db.ForeignKey('person.email'))

  def __init__(self, sku, json_data, owner_id):
    self.sku = sku
    self.json_data = json_data
    self.owner_id = owner_id

# Product Schema
class ProductSchema(ma.Schema):
  class Meta:
    fields = ('sku', 'json_data')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Suscription
@app.route('/suscription', methods=['POST'])
def add_suscription():
  email = request.json['email']
  sku = request.json['sku']
  json_data = request.json['json_data']
  #email = request.json['email'] si es nuevo mail se crea la persona, sino simplemente se asocia con person-product

  new_person = Person(email)

  new_product = Product(sku, json_data, email)

  db.session.add(new_person) 
  db.session.commit()

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)

# Create a Product
@app.route('/product', methods=['POST'])
def add_product():
  sku = request.json['sku']
  json_data = request.json['json_data']
  #email = request.json['email'] si es nuevo mail se crea la persona, sino simplemente se asocia con person-product

  new_product = Product(sku, json_data)

  db.session.add(new_product)
  db.session.commit()

  return product_schema.jsonify(new_product)

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
  all_products = Product.query.all()
  result = products_schema.dump(all_products)
  return jsonify(result)

# Get Single Products
@app.route('/product/<sku>', methods=['GET'])
def get_product(sku):
  product = Product.query.get(sku)
  return product_schema.jsonify(product)

# Update a Product
@app.route('/product/<sku>', methods=['PUT'])
def update_product(sku):
  product = Product.query.get(sku)

  sku = request.json['sku']
  json_data = request.json['json_data']

  product.sku = sku
  product.json_data = json_data

  db.session.commit()

  return product_schema.jsonify(product)

# Delete Product
@app.route('/product/<sku>', methods=['DELETE'])
def delete_product(sku):
  product = Product.query.get(sku)
  db.session.delete(product)
  db.session.commit()

  return product_schema.jsonify(product)


# Run Server
if __name__ == '__main__':
  app.run(debug=True)


#""""
#  class Association(Base):
#    tablename = 'association'
#    left_id = Column(ForeignKey('left.id'), primary_key=True)
#    right_id = Column(ForeignKey('right.id'), primary_key=True)
#    extra_data = Column(String(50))
#    child = relationship("Child")

#class Parent(Base):
#    tablename = 'left'
#    id = Column(Integer, primary_key=True)
#    children = relationship("Association")

#class Child(Base):
#    tablename = 'right'
#    id = Column(Integer, primary_key=True)
    
#""""