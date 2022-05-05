from itertools import product
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required


shop = Blueprint('shop', __name__, template_folder='shop_templates')

from app.models import db, Product, Cart


@shop.route('/products')
def allProducts():
    products = Product.query.all()
    return render_template('shop.html',products = products)

@shop.route('/products/<int:product_id>')
def individualProduct(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return redirect(url_for('shop.allProducts'))
    return render_template('individual_product.html', product = product)

#Cart

@shop.route('/cart')
@login_required
def showCart():
    cart = Cart.query.filter_by(user_id = current_user.id)
    count = {}
    for item in cart:
        count[item.product_id] = count.get(item.product_id, 0) + 1
    
    cart_products = []
    for product_id in count:
        product_info = Product.query.filter_by(id=product_id).first().to_dict()
        product_info["quantity"] = count[product_id]
        product_info['subtotal'] = product_info['quantity'] * product_info['price']
        cart_products.append(product_info)
    return render_template('show_cart.html', cart = cart_products)


@shop.route('/cart/add/<int:product_id>')
@login_required
def addToCart(product_id):
    cart_item = Cart(current_user.id, product_id)
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('shop.allProducts'))

#API CREATION


@shop.route('/api/products')
def apiProducts():
    products = Product.query.all()
    return {
        'status': 'ok',
        'total_results': len(products),
        'products': [p.to_dict() for p in products]
    }

@shop.route('/api/login', methods =["POST"])
def apiLogin():
    return 

@shop.route('/api/products/<int:product_id>')
def apiSingleProducts(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return{
            'status': 'not ok',
            'total_results': 0,
        }
    return {
        'status': 'ok',
        'total_results': 1,
        'product': product.to_dict()
    }

@shop.route('/api/cart/get')
def getCart(user):
    cart = Cart.query.filter_by(user_id = user.id)
    myCart = [Product.query.filter_by(id = item.product_id).first().to_dict() for item in cart]
    return {
        'status': 'ok',
        'cart': myCart
    }
## SHOP API ##
##############


@shop.route('/api/products/update/<int:product_id>', methods=["POST"])
# @login_required
def apiUpdateProducts(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return {
            'status': 'not ok',
            'total_results': 0,
        }
    
    if request.method == "POST":
        data = request.json
        product_name = data['product_name']
        image = data['image']
        price = data['price']
        description = data['description']

        # update the original post
        product.product_name = product_name
        product.image = image
        product.description = description
        product.price = price

        db.session.commit()   

        return {
            'status':'ok',
            'message':'Your product has been updated',
            'product':product.to_dict()
        }

@shop.route('/api/products/delete/<int:product_id>', methods=["POST"])
# @login_required
def apideleteProduct(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return {
            'status': 'not ok',
            'total_results': 0,
        }

    db.session.delete(product)
    db.session.commit()
               
    return {
        'status':'ok',
        'message': 'this product has been deleted',
        'product': product.to_dict()

    }

@shop.route('/api/create-product', methods=["POST"])
#@login_required
def apicreatePost():
    if request.method == "POST":
        data = request.json
        product_name = data['product_name']
        image = data['image']
        description = data['description']
        price = data['price']

        product = Product(product_name, image, description, price)

        db.session.add(product)
        db.session.commit()   

        return {
            'status': 'ok',
            'message': 'Successfully created a new product',
            'product' : product.to_dict()
        }
