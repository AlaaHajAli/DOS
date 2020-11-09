import requests
from flask import Flask
from flask_restful import Api, Resource, request


### initializing the service as an api
app = Flask(__name__)
api = Api(app)

### handling the log server requests.
class LogHandler(Resource):
    def post(self, book_id):
        ### directing the client's request to the correct server and returning the response -same for the rest-
        response = requests.post('http://127.0.0.1:6300/buy/'+str(book_id))
        return response.json()

### handling the catalog server requests.
class CatalogHandler(Resource): 
    def put(self, book_id):
        args = request.args
        response = requests.put('http://127.0.0.1:6200/add/'+str(book_id), args)
        return response.json()

    def patch(self, book_id):
        args = request.args
        response = requests.patch('http://127.0.0.1:6200/update/'+str(book_id), args)
        return response.json()
    
    def get(self, book_id):
        response = requests.get('http://127.0.0.1:6200/lookup/'+str(book_id))
        return response.json()

class CatalogHandlerSearch(Resource): 
    def get(self):
        response = requests.get('http://127.0.0.1:6200/search')
        return response.json()

class CatalogHandlerSearchTopic(Resource): 
    def get(self, book_topic):
        response = requests.get('http://127.0.0.1:6200/search/'+str(book_topic))
        return response.json()

api.add_resource(LogHandler, '/buy/<int:book_id>')
api.add_resource(CatalogHandler, '/add/<int:book_id>', '/update/<int:book_id>', '/lookup/<int:book_id>')
api.add_resource(CatalogHandlerSearch, '/search')
api.add_resource(CatalogHandlerSearchTopic, '/search/<string:book_topic>')

if __name__ == "__main__":
    app.run(debug=True, port= 6400)