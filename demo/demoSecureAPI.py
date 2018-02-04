from flask import Flask
from flask_jwt import JWT, jwt_required, current_identity

'''
JWT token authentication for a flask API. 

- To obtain a token: make a POST request to /auth with username and password	
- To access a @jwt_required() endpoint, add an Authorization header to the 
http request

'''

'''
User object- used by the JWT for authentication
'''
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

#simple user store
users = [
    User(1, 'user1', 'abcxyz'),
    User(2, 'user2', 'abcxyz'),
]
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

'''
Authenticate an incoming user against the user store. This method will be used by the JWT 
libray and will get the path /auth

curl -i -X post -H "Content-Type: application/json" -d '{"username":"user1", "password":"abcxyz"}'  https://ec2-18-217-231-215.us-east-2.compute.amazonaws.com:5000/auth
'''
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and user.password.encode('utf-8') == password.encode('utf-8'):
        return user

'''
Identity will be used by the JWT library to make sure the user is there and is found in 
the user store.
'''
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

app = Flask(__name__)
app.debug = True

#JWT config and declaration
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=10)
jwt = JWT(app, authenticate, identity)

'''
curl -i -X get -H "Authorization: JWT <token>"  https://ec2-18-217-231-215.us-east-2.compute.amazonaws.com:5000/protected
'''
@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True, ssl_context=('certificate/cert.pem', 'certificate/key.pem'))





