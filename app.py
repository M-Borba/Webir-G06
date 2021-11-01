import os
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import json
import requests
import time
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS, cross_origin

Base = declarative_base()


# Init app
app = Flask(__name__)
CORS(app)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://coco:root@localhost/camel"
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://oiyrrypgcshihu:b11c89365f624d7c4fbeb9f8aa330d1a9594da91668a294858b10ce39716c320@ec2-52-207-47-210.compute-1.amazonaws.com:5432/d4als9lkenqs1b'

app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False

# basedir = os.path.abspath(os.path.dirname(__file__))
# # Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
#     os.path.join(basedir, 'db.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# # Person Class/Model


class Person(db.Model, Base):
    email = db.Column(db.String(75), primary_key=True)
    children = relationship("Person_product")

    def __init__(self, email):
        self.email = email

# Product Class/Model


class Product(db.Model, Base):
    sku = db.Column(db.String(100), primary_key=True)
    price = db.Column(db.Integer)
    parent = relationship("Person_product")

    def __init__(self, sku, price):
        self.sku = sku
        self.price = price


class Person_product(db.Model, Base):
    email = Column(ForeignKey(
        'person.email', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    sku = Column(ForeignKey('product.sku', ondelete="CASCADE", onupdate="CASCADE"),
                 primary_key=True)
    drop_price = db.Column(db.Float)
    #drop_discount = db.Column(db.Float)

    def __init__(self, sku, email, drop_price):
        self.sku = sku
        self.email = email
        #self.drop_discount = drop_discount
        self.drop_price = drop_price

# Product Schema -- para la serializacion, esto se retorna


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('sku', 'price')


# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a Product


@app.route('/product', methods=['POST'])
@cross_origin(origin='*')
def add_product():
    req = request.get_json()
    print(req)
    sku = req['sku']
    price = requests.get(
        "https://api.mercadolibre.com/items/MLU"+sku).json()['price']
    email = req['email']
    drop_price = req['drop_price']
    #drop_discount = request.json['drop_discount']

    if not isinstance(sku, str):
        return "sku debe estar compuesto por caracteres"
    # try:
    #     json.loads(json.dumps(json_data))
    # except ValueError as err:
    #     return "json_data debe ser formato JSON"
    if not isinstance(email, str):
        return "email debe estar compuesto por caracteres"
    if not isinstance(drop_price, int):
        return "drop_price debe ser un numero"
    # if not isinstance(drop_discount, int):
    #    return "drop_discount debe ser un numero"

    product = Product.query.get(sku)
    if product is None:
        product = Product(sku, price)
        db.session.add(product)

    person = Person.query.get(email)
    if person is None:
        person = Person(email)
        db.session.add(person)

    person_product = Person_product.query.filter_by(
        email=email, sku=sku).first()
    if person_product is None:
        person_product = Person_product(sku, email, drop_price)
        db.session.add(person_product)
    else:
        person_product.drop_price = drop_price
        #person_product.drop_discount = drop_discount

    db.session.commit()
    #
    resp = product_schema.jsonify(product)
    resp.status_code = 302
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# @app.route('/notificar')


def report_elements():
    products = Product.query.all()
    for prod in products:
        resp = requests.get(
            "https://api.mercadolibre.com/items/MLU"+prod.sku).json()
        # print(resp['id'])
        prods_pers = Person_product.query.filter_by(sku=resp['id'])
        for pp in prods_pers:
            if pp.drop_price > resp['price']:
                # return {'Dato':'Valor menor','reposnse':resp['price'],'db':pp.drop_price}
                subject = "Camel-UY => " + resp['title']
                if(enviarCorreo(pp.email, resp['permalink'], subject)):
                    print("Correo enviado a "+pp.email+" con subject "+subject)
                    sku_aux = prod.sku
                    email_aux = pp.email
                    join_sku = db.session.query(Product).join(
                        Person_product).filter(Product.sku == sku_aux).count() == 1
                    join_email = db.session.query(Person).join(
                        Person_product).filter(Person.email == email_aux).count() == 1
                    db.session.delete(pp)
                    if join_sku:
                        db.session.delete(prod)
                    if join_email:
                        person = Person.query.get(email_aux)
                        db.session.delete(person)
                    db.session.commit()


def enviarCorreo(dirDestino, mensaje, subject):  # enviarCorreo(dirDestino,mensaje)
    dirOrigen = 'webir2021@gmail.com'
    contraseña = 'camelcamelcamel'

    msg = MIMEText('''Bajo el precio!!!
    Que estas esperando? Anda a buscarlo!!
    {}
    '''.format(mensaje))
    # print(pp.email)
    # print(mensaje)
    msg['Subject'] = subject
    msg['From'] = 'webir2021@gmail.com'
    msg['To'] = dirDestino
    try:
        servidor_smtp = smtplib.SMTP("smtp.gmail.com", 587)
        servidor_smtp.ehlo()
        servidor_smtp.starttls()
        servidor_smtp.ehlo()
        servidor_smtp.login(dirOrigen, contraseña)
        servidor_smtp.sendmail(dirOrigen, dirDestino, msg.as_string())
        servidor_smtp.quit()
        return True
    except:
        return False


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
    app.run()


def getApp():
    return app


# ------------------Mails

# def prueba():
#   i = 1
#   while True:
#     time.sleep(10)
#     enviarCorreo()

# hilo = threading.Thread(target=prueba)
# hilo.daemon = True
# hilo.start()
# import smtplib
