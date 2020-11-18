# DOS
## REQUIRMENTs:
*Install the following:
aniso8601==8.0.0
click==7.1.2
Flask==1.1.2
Flask-RESTful==0.3.8
Flask-SQLAlchemy==2.4.3
itsdangerous==1.1.0
Jinja2==2.11.2
MarkupSafe==1.1.1
pytz==2020.1
six==1.15.0
SQLAlchemy==1.3.18
Werkzeug==1.0.1
## HOW TO USE:
* initialize the ip addresses of your VMs in the frontend service for catalog and log services , and the ip address of catalog VM in the log service.
* run both catalog and log servers then run the frontend server and make sure of the used port for each server.
* send requests from your browser or using postman to the frontend server, make sure that the url of the request is correct and that you are using the frontend server's ip.
* make sure that you use the correct REST request method for each client's request and check that it's correct from the output response.
## NOTES:
***you can find all requests' kinds supported in this project and the output response log in the output folder in the repository.
***The services were first created and tested on the host machine and then created on two ubuntu VMs, one for catalog and one for log. frontend and client stayed on host and then tested all requests between all servers on the host and VMs using the IP address for each.
***all services can run on VMs, you only need to specify the correct ip address and make sure the Network settings of the VMs supports connection between diffrent ips in the same network.
***the update and add methods were added for easier usage with the database as sqlite was used.
***each request type/method was chosen for each functionality depending on the standard usage of each REST request method.
