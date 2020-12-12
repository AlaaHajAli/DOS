import requests
from flask import Flask
from flask_restful import Api, Resource, request

LEADER = 'http://192.168.1.118:5000'
### initializing the service as an api
app = Flask(__name__)
api = Api(app)

class Log(Resource):
    ### only one method for log to handle buying a book
    def post(self, book_id):
        try:
            ### first contact catalog server to be sure that the book exists and is in stock
            address = request.args.get('address')
            response = requests.get(address+'/lookup/'+str(book_id))
            if response.json().get('message'): #== 'Could not find book with that id':
                return(response.json().get('message'))
            elif response.json().get('stock_count') == 0:
                return(str(response.json().get('name')) + "is Out of stock!")
            else:
                val = response.json().get('stock_count') - 1
                ### if exists and in stock, contact catalog to update the book's stock count
                resp = requests.patch(LEADER +'/update/'+str(book_id), {'stock_count': val})
                return ("Bought Book : " + str(resp.json().get('name'))), 201
        except:
            ### if one is not live, do not update, "maintaining consistency."
            print('Failed to connect to server/s ...')
            return 'Something went wrong, cannot buy!'
         

api.add_resource(Log, "/buy/<int:book_id>")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
