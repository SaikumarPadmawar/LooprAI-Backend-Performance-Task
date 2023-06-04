from datetime import datetime
from threading import active_count
from flask_restful import Resource, reqparse, Api
from flask import abort
from marshmallow import fields, Marshmallow
import markdown.extensions.fenced_code
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config



app = Flask(__name__)
CORS(app)
api = Api(app)
db = SQLAlchemy()
ma = Marshmallow()


class CartModel(db.Model):

    __tablename__ = "cart"

    productId = db.Column(db.Integer, primary_key = True, nullable=False,  autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    image = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Interger, nullable=False)

    def __repr__(self):
        return self.name


# Profile Schema for serialization using marsahmallow

class CartSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CartModel

    productId = ma.auto_field()
    name = ma.auto_field()
    image = ma.auto_field()
    price = ma.auto_field()
    quantity = ma.auto_field()

#Parser Arguments for Create
parser = reqparse.RequestParser()
parser.add_argument('image')
parser.add_argument('price')
parser.add_argument('quantity')




resolve_fields = {
    'productId': fields.Integer,
    'name': fields.String,
    'image': fields.String,
    'price': fields.Integer,
    'quantity': fields.Integer,
}

cart_schema = CartSchema()

class Cart(Resource):

    #get request on "cart"
    def get(self):
        product_schema = CartSchema()
        all_product = CartModel.query.all() #querying all the existing profiles
        
        # Dictonary for response

        response = dict()
        response["created_at"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        #if no database is empty
        if not all_product:
            response['data'] = "No product exist in the databse"
            return response, 200

        total = len(all_product)
        data = []

        for product in all_product:
            data.append(product_schema.dump(product)) #adding the profile object in Json

        response['data'] = data
        response['total'] = total

        return response, 200

    #POST request on 'product', Creates a product
    def post(self):
        product_schema = CartSchema()
        args = parser.parse_args()

        #if None Arguments
        if args["price"]==None or args["name"]==None or args["image"] or args["quantity"] :
            abort(400)


        profile = CartModel(name=args["name"], price=args["price"], image= args["image"], quantity = args["quantity"])
        
        #Saving and Adding to Database
        db.session.add(profile)
        db.session.commit()

        #response
        response = dict()
        response["created_at"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        response["data"] = product_schema.dump(profile)

        return response , 201

    def delete(self):
        abort(405)

    def put(self):
        abort(405)

#Parser Arguments for Update
update = reqparse.RequestParser() 
update.add_argument('name')
update.add_argument('image')
update.add_argument('price')
update.add_argument('quantity')


class Edit(Resource):

    #GET request on 'products/id', returns Product
    def get(self, id):
        product_schema = CartSchema()

        product = CartModel.query.get(id) #querying to get profile with id

        response = dict()

        #if product does not exist
        if not product:
            abort(404)
        
        #response
        response = dict()
        response["created_at"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        response["data"] = product_schema.dump(product)
        
        return response, 200

    def patch(self, id):
        args = update.parse_args()    
        product_schema = CartSchema()

        product = CartModel.query.get(id)

        #if the profile with given id does not exist
        if not product:
            abort(404)
            
        # Updating given args
            
        if args['name']!= None:
            product.name = args['name']

        if args['price']!= None:
            product.price = args['price']

        if args['image']!= None:
            product.image = args['image'] 
          
        if args['quantity']!= None:
            product.quantity = args['quantity'] 

        db.session.commit()

        #response
        response = dict()
        response["created_at"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        response["message"] = "Product Successfully added"
        response["data"] = product_schema.dump(product)

        return response, 200       

    def post(self, id):
        abort(405)

    def put(self, id):
        abort(405)

    def delete(self, id):
        product = CartModel.query.get(id) #querying for profile

        #if product does not exist
        if not product:
            abort(404)

        db.session.delete(product)
        db.session.commit()
        
        return {"message": "Product removed succesfully"}, 204



api.add_resource(Cart, '/products')
api.add_resource(Edit, '/products/<int:id>')



def create_app(config_class=Config):

    #configs
	app.config.from_object(config_class)

	# Init database, create tables if needed
	db.init_app(app)
	with app.app_context():
		db.create_all()

	# Using Marshmallow for serialization
	ma.init_app(app)

	# Create Api for this flask application using prefix
	api.init_app(app)

	return app