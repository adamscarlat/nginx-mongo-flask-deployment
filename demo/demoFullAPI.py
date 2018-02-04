from flask import Flask, abort, request, make_response, jsonify
from flask_jwt import JWT, jwt_required, current_identity
import redis, datetime, sys



#------- Redis ------------
redis_port = 6379
user_db = 0
redis_host = 'localhost'
redis_cli = redis.StrictRedis(host=redis_host, port=redis_port, db=user_db)

#------ App ---------
app = Flask(__name__)
app.debug = True
certificate_path = 'certificate/cert.pem'
key_path = 'certificate/key.pem'
app_host = '0.0.0.0'
is_debug = True


#API utils
#------------------------------------------------------------------------------------------------------
'''
Handler for 400 messages
'''
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': error.description['message']}))

#API
#------------------------------------------------------------------------------------------------------
'''
curl -i -X get -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1MTY5MTE5ODMsImlkZW50aXR5IjoidXNlcjEiLCJleHAiOjE1MTc3NzU5ODMsIm5iZiI6MTUxNjkxMTk4M30.y7lerY9NrJOkXVeRBQbjPnnxF484dozA3Ory_vWNtyg"  https://ec2-18-217-231-215.us-east-2.compute.amazonaws.com:5000/protected
'''
@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


#Config
#------------------------------------------------------------------------------------------------------

# ----- JWT -----------

'''
Authenticate an incoming user against the user store. This method will be used by the JWT 
libray and will get the path /auth

authenticate needs to create a User object with id, username and password

curl -i -X post -H "Content-Type: application/json" -d '{"username":"user1", "password":"blaj"}'  https://ec2-18-217-231-215.us-east-2.compute.amazonaws.com:5000/auth
'''
def authenticate(username, password_req):
    user_profile = redis_cli.hgetall(username)

    user_profile = {key.decode('utf-8'): value.decode('utf-8') for key, value in user_profile.items()}

    if not user_profile or 'password' not in user_profile or 'id' not in user_profile:
        return

    password_db = user_profile['password']

    print (password_db, file=sys.stdout)

    user_id = user_profile['id']
    if password_db == password_req:
        return User(username, username, password_db)

'''
Identity is a method needed by the JWT library. It takes the JWT token and extracts the payload
from it. We can use the identity property of the payload to extract the user object from the
database. 

* The identity property maps to the id property of the User object we set in the authenticate property
'''
def identity(payload):
    print (payload, file=sys.stdout)
    return payload['identity']

# @app.route('/api/register', methods=['POST'])
# def register():
#     if not request.json or not 'username' in request.json or not 'password' in request.json:
#         abort(400, {'message': 'missing data'})

#     username = request.json['username']
#     password = request.json['password']
    
#     if not username or username == '':
#         abort(400, {'message': 'invalid username'})

#     if not password or password == '':
#         abort(400, {'message': 'invalid password'})
    
#     if not redis_cli.get(username):
#         redis_response = redis_cli.set(username, password)
#         return make_response(jsonify({'db': redis_response}))

#     return make_response(jsonify({'db': '%s exists ' % username}))

    

#JWT config and declaration
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=10)
jwt = JWT(app, authenticate, identity)

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



if __name__ == '__main__':
    app.run(host = app_host, debug=is_debug, ssl_context=(certificate_path, key_path))