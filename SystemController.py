import app

@app.route('/notificar')
def report_elements():
   products = Product.query().all()
   for prod in products:
        resp = requests.get("https://api.mercadolibre.com/items/"+prod.sku).json()
        print(resp['id'])
        #prods_pers = Person_product.query().filter_by(sku=resp['id'])
        