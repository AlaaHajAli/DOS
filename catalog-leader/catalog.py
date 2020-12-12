from flask import Flask, json
import requests
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, request
from flask_sqlalchemy import SQLAlchemy


CATALOG_Replica = 'http://192.168.1.108:5000'

### initializing the service and creating it as an api
app = Flask(__name__)
api = Api(app)

### connecting to the database of type sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
### database model
class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False )
    stock_count = db.Column(db.Integer, nullable = False)
    cost = db.Column(db.Integer, nullable = False)
    topic = db.Column(db.String(100), nullable = False)

    ### returned book object representation
    def __repr__(self):
        return f"Book(name = {name}, topic = {topic}, stock_count = {stock_count}, cost = {cost})"

### database creation 'only run once'
#db.create_all()

### parsing request's arguments and making them json seriarizable for the response.
book_put_args = reqparse.RequestParser()
book_put_args.add_argument("name", type=str, help="Name of the book is required", required=True)
book_put_args.add_argument("stock_count", type=int, help="stock count is required", required=True)
book_put_args.add_argument("cost", type=int, help="book cost is required", required=True)
book_put_args.add_argument("topic", type=str, help="book topic is required", required=True)
book_update_args = reqparse.RequestParser()
book_update_args.add_argument("name", type=str, help="Name of the book")
book_update_args.add_argument("stock_count", type=int, help="stock count")
book_update_args.add_argument("cost", type=int, help="book cost")
book_update_args.add_argument("topic", type=str, help="book topic")

### to map the request arguments with the correct form for each argument and filtering them.
resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
    'topic': fields.String,
	'stock_count': fields.Integer,
	'cost': fields.Integer,
}

class Catalog(Resource):
    ###  marshal_with is a decorator: takeing the args of the object and applying fields filtering. 
    @marshal_with(resource_fields)
    def put(self, book_id):
        try:   
            args = book_put_args.parse_args()
            ### adding to replica
            resp = requests.put(CATALOG_Replica+'/add/'+str(book_id), args)
            if resp:
                print("Replica says: Done")
            else:
                print("Failed to add to the replica")
            ### adding to leader
            res = BookModel.query.filter_by(id = book_id).first()
            if res:
                abort(404, message = "Book id is already taken")
            book = BookModel(id = book_id, name = args['name'], stock_count = args['stock_count'], cost = args['cost'], topic = args['topic'])
            db.session.add(book)
            db.session.commit()
            return book, 201
        except:
            ### if replica is down, do no add "maintaning consistency"
            print("Failed to connect to the replica")
            return 'Somthing went wrong, cannot add!', 500

    @marshal_with(resource_fields)
    def patch(self, book_id):
        try:
            args = book_update_args.parse_args()
            result = BookModel.query.filter_by(id=book_id).first()
            if not result:
                abort(404, message="book doesn't exist, cannot update")
            ### updating the replica
            resp = requests.patch(CATALOG_Replica+'/update/'+str(book_id), args)
            if resp:
                print("Replica says: Done") 
            else:
                print("Failed to update the replica")
            ### updating the leader
            if args['name']:
                result.name = args['name']
            if args['cost'] and args['cost']>=0:
                result.cost = args['cost']
            if args['stock_count'] and args['stock_count']>=0:
                result.stock_count = args['stock_count']
            if args['topic']:
                result.topic = args['topic']
	        
            db.session.commit()
            return result, 201
        except:
            ### if replica is down, do no update "maintaning consistency"
            print("Failed to connect to the replica")
            return 'Somthing went wrong, cannot update!', 500
        

    @marshal_with(resource_fields)
    def get(self, book_id):
        result = BookModel.query.filter_by(id = book_id).first()
        if not result:
            abort(404, message="Could not find book with that id")
        return result

class CatalogSearchAll(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result = BookModel.query.all()
        if not result:
            abort(404, message="No books found!")
        return result

class CatalogSearchTopic(Resource):
    @marshal_with(resource_fields)
    def get(self, book_topic):
        result = BookModel.query.filter_by(topic = book_topic).all()
        if not result:
            abort(404, message="Could not find books with that topic")
        return result

### adding the class to the api to recognize it.
### api resources cannot contain the same REST method twice and I want to use classes.
api.add_resource(Catalog, '/add/<int:book_id>', '/update/<int:book_id>', '/lookup/<int:book_id>')
api.add_resource(CatalogSearchAll, '/search')
api.add_resource(CatalogSearchTopic, '/search/<string:book_topic>')

### main method
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
