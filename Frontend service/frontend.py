import requests
from flask import Flask
from flask_restful import Api, Resource, request

### initializing the service as an api
app = Flask(__name__)
api = Api(app)

### INTIALIZIN IP ADDRESSES of each server
# SINGLE LEADER REPLICATION: READ FROM ANY, WRITE TO LEADER
CATALOG = 'http://192.168.1.118:5000' #THE LEADER
LOG = 'http://192.168.1.107:5000'
CATALOG_Replica = 'http://192.168.1.108:5000'
LOG_Replica = 'http://192.168.1.111:5000'

### Flags for round robin load balancing
cat_flag = False
log_flag = False

### load balancers using round robin algorithm
def catalogLoadBalancer(flag):
    if flag:
        return CATALOG_Replica
    else:
        return CATALOG

def logLoadBalancer(flag):
    if flag:
        return LOG_Replica
    else:
        return LOG


### cache 
cache = []
### cache methods
def get_book(book_id):
    for item in cache:
        if item['id'] == book_id:
            return item
    return 0

def get_books(book_topic):
    temp = []
    for item in cache:
        if item['topic'] == book_topic:
            temp.append(item) 
    if len(temp) > 0:
        return temp
    else:
        return 0

def set_book(item):
    cache.append(item)   

def invalidate(book_id):
    [cache.remove(item) for item in cache if item['id']==book_id]

### handling the log server requests.
class LogHandler(Resource):
    def post(self, book_id):
        ### directing the client's request to the correct server and returning the response -same for the request-
        global cat_flag
        cat_flag = not cat_flag
        global log_flag
        log_flag = not log_flag
        args = {'address': catalogLoadBalancer(cat_flag)}
        try:
            response = requests.post(logLoadBalancer(log_flag)+'/buy/'+str(book_id), params = args )
            if response.status_code == 201:
                invalidate(book_id)
            return response.json()
        except:
            print('Failed to connect to server, switching ...')
            log_flag = not log_flag
            try:
                response = requests.post(logLoadBalancer(log_flag)+'/buy/'+str(book_id), params = args )
                if response.status_code == 201:
                    invalidate(book_id)
                return response.json()
            except:
                return 'Failed to connect to servers!!', 500
                
### handling the catalog server requests.
class CatalogHandler(Resource): 
    def put(self, book_id):
        args = request.args
        try:
            response = requests.put(CATALOG+'/add/'+str(book_id), args)
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 500:
                return 'something went wrong, cannot update!'
        except:
            print('Failed to connect to server ...')
            return 'something went wrong, cannot add a new book!', 500

    def patch(self, book_id):
        args = request.args
        try:
            response = requests.patch(CATALOG+'/update/'+str(book_id), args)
            if response.status_code == 200:
                invalidate(book_id)
                return response.json()
            elif response.status_code == 500:
                return 'something went wrong, cannot update!'
        except:
            print('Failed to connect to server ...')
            return 'something went wrong, cannot update!', 500
        
    def get(self, book_id):
        if get_book(book_id):
            print("getting from cache ...")
            return get_book(book_id)
        else:
            try:
                print("getting from server ...")
                global cat_flag
                cat_flag = not cat_flag
                response = requests.get(catalogLoadBalancer(cat_flag)+'/lookup/'+str(book_id))
                if response.status_code == 404:
                    return response.json()
                elif response.status_code == 200:
                    set_book(response.json())
                    return response.json()
            except:
                try:
                    print("getting from server ...")
                    cat_flag = not cat_flag
                    response = requests.get(catalogLoadBalancer(cat_flag)+'/lookup/'+str(book_id))
                    if response.status_code == 404:
                        return response.json()
                    elif response.status_code == 200:
                        set_book(response.json())
                        return response.json()
                except:
                    return 'Failed to connect to servers!!', 500
            

class CatalogHandlerSearch(Resource): 
    def get(self):
        try:
            global cat_flag
            cat_flag = not cat_flag
            response = requests.get(catalogLoadBalancer(cat_flag)+'/search')
            return response.json()
        except:
            try:
                cat_flag = not cat_flag
                response = requests.get(catalogLoadBalancer(cat_flag)+'/search')
                return response.json()
            except:
                return 'Failed to connect to servers!!', 500

class CatalogHandlerSearchTopic(Resource): 
    def get(self, book_topic):
        if get_books(book_topic):
            print('getting from cache ...')
            return get_books(book_topic)
        else:
            try:
                print('getting from server ...')
                global cat_flag
                cat_flag = not cat_flag
                response = requests.get(catalogLoadBalancer(cat_flag)+'/search/'+str(book_topic))
                if response.status_code == 404:
                    return response.json()
                else:
                    for item in response.json():
                        set_book(item)
                    return response.json()
            except:
                try:
                    print('getting from server ...')
                    cat_flag = not cat_flag
                    response = requests.get(catalogLoadBalancer(cat_flag)+'/search/'+str(book_topic))
                    if response.status_code == 404:
                        return response.json()
                    else:
                        for item in response.json():
                            set_book(item)
                        return response.json()
                except:
                    return 'Failed to connect to servers!!', 500



### registering the resources to the api
api.add_resource(LogHandler, '/buy/<int:book_id>')
api.add_resource(CatalogHandler, '/add/<int:book_id>', '/update/<int:book_id>', '/lookup/<int:book_id>')
api.add_resource(CatalogHandlerSearch, '/search')
api.add_resource(CatalogHandlerSearchTopic, '/search/<string:book_topic>')

if __name__ == "__main__":
    app.run(debug=True,host = '0.0.0.0' ,port= 6400)
