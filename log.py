import requests
from flask import Flask
from flask_restful import Api, Resource

### IP ADDRESS OF CATALOG SERVER
CATALOG = 'http://192.168.1.113:5000'

### initializing the service as an api
app = Flask(__name__)
api = Api(app)

class Log(Resource):
    ### only one method for log to handle buying a book
    def post(self, book_id):
        ### first contact catalog server to be sure that the book exists and is in stock
        response = requests.get(CATALOG+'/lookup/'+str(book_id))
        if response.json().get('message') == 'Could not find book with that id':
            return(response.json().get('message'))
        elif response.json().get('stock_count') == 0:
            return(str(response.json().get('name')) + "is Out of stock!")
        else:
            val = response.json().get('stock_count') - 1
            ### if exists and in stock, contact catalog to update the book's stock count
            resp = requests.patch(CATALOG+'/update/'+str(book_id), {'stock_count': val})
            return("Bought Book : " + str(resp.json().get('name')))

api.add_resource(Log, "/buy/<int:book_id>")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')