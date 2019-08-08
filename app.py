from flask import Flask, request, Response,jsonify, make_response
import bcrypt
import json
import time
import dbMysql
import dbClass
import env
import secrets

app = Flask(__name__)
mysql_obj = dbMysql.DbMysql(env.DB_HOST, env.DB_PORT, env.DB_USERNAME, env.DB_PASSWORD, env.DB_DATABASE)
db_obj = dbClass.DbWrapper(mysql_obj)


def valid_auth(auth_key):
    if auth_key != env.AUTH_KEY:
        return False
    return True


def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt(12))


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


@app.route('/api/user', methods=['POST', 'GET'])
def action_user():
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):
            message = ""
            if request.method == 'POST':
                # Creating a user with given values.
                json_data = request.get_json()
                print(json_data)
                name_surname = json_data['name_surname']
                password = get_hashed_password(json_data['password'])
                email = json_data['email']

                db_obj.insert_data('user',
                                   [(name_surname, password, email, time.time())],
                                   COLUMNS=['name_surname', 'password', 'email', 'created_at'])

                # Generating an API key assigned to the user id.
                api_key = ''.join(secrets.token_hex(20))
                userid = db_obj.get_last_insert_id()
                db_obj.insert_data('api_key',
                                   [(userid, api_key, time.time())],
                                   COLUMNS=['user_id', 'api_key', 'timestamp'])
                # Success!
                return make_response(jsonify({
                    "message": "User is generated successfully!",
                    "User ID": userid,
                    "API Key:": api_key})
                    , 200)

            elif request.method == 'GET':
                userdata = db_obj.execute("SELECT * FROM user")
                return make_response(jsonify(userdata), 200)
            else:
                return Response(status=405)
        else:
            return Response(status=401)
    else:
        return Response(status=401)


@app.route('/check_connection', methods=['POST', 'GET'])
def check_connection():
    # Validate the request body contains JSON
    if request.is_json:
        req = request.get_json()
        res = make_response(jsonify({"message": "All okay!", "request": req}), 200)
        return res
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):
            return "API is working!", 200
        else:
            return Response(status=401)
    else:
        return Response(status=401)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
