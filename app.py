from flask import Flask, request, Response, jsonify, make_response
import bcrypt
import traceback
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
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.
            if request.method == 'POST':
                # Creating a user with given values.
                json_data = request.get_json()
                if 'name_surname' in json_data and 'password' in json_data and 'email' in json_data:
                    name_surname = json_data['name_surname']
                    password = get_hashed_password(json_data['password'])
                    email = json_data['email']

                    try:
                        db_obj.insert_data('user',
                                           [(name_surname, password, email, time.time())],
                                           COLUMNS=['name_surname', 'password', 'email', 'created_at'])
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)

                    # Generating an API key assigned to the user id.
                    api_key = ''.join(secrets.token_hex(20))
                    userid = db_obj.get_last_insert_id()

                    try:
                        db_obj.insert_data('api_key',
                                           [(userid, api_key, time.time())],
                                           COLUMNS=['user_id', 'api_key', 'timestamp'])
                    except Exception as e:
                        print(e)
                        try:
                            db_obj.execute("DELETE FROM user WHERE user.id = " + userid + " LIMIT 1;")
                        except Exception as e:
                            print(e)
                            return Response("Action could not be performed. Query did not execute successfully.",
                                            status=500)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)

                    # Success!
                    return make_response(jsonify({
                        "message": "User is generated successfully!",
                        "User ID": userid,
                        "API Key:": api_key}), 200)
                else:
                    return Response("Invalid parameters.", status=400)

            elif request.method == 'GET':
                try:
                    userdata = db_obj.execute("SELECT * FROM user")
                except Exception as e:
                    print(e)
                    return Response("Action could not be performed. Query did not execute successfully.", status=500)
                return make_response(jsonify(userdata), 200)
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/seo-errors/<int:error_id>', methods=['GET'])
def action_get_seo_error(error_id):
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.
            if request.method == 'GET':
                if error_id and error_id > 0:
                    try:
                        error_detail = db_obj.execute("SELECT * FROM seo_errors WHERE id = '" + str(error_id) + "';")
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    if len(error_detail) > 0:
                        return make_response(jsonify(error_detail), 200)
                    else:
                        return Response("No record found for this error ID.", status=404)
                else:
                    return Response("No record found for this error ID.", status=404)
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/seo-errors', methods=['POST', 'PUT', 'GET'])
def action_seo_errors():
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.

            # POST
            if request.method == 'POST':
                # Creating a new SEO error with given name, description and error-condition.
                json_data = request.get_json()
                if 'name' in json_data and 'error_condition' in json_data and 'description' in json_data:
                    name = json_data['name']
                    error_condition = json_data['error_condition']
                    description = json_data['description']

                    try:
                        db_obj.insert_data('seo_errors',
                                           [(name, error_condition, description)],
                                           COLUMNS=['name', 'error_condition', 'description'])
                        message = "A new error has been added successfully!"
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    return make_response(message, 200)
                else:
                    return Response("Invalid parameters.", status=400)

            # PUT
            elif request.method == 'PUT':
                json_data = request.get_json()
                if 'id' in json_data and 'data' in json_data:
                    row_id = json_data['id']
                    update_items = json_data['data'].items()

                    try:
                        db_obj.update_data('seo_errors', update_items, row_id)
                        message = "Error with id #" + str(row_id) + " is updated successfully!"
                    except Exception as e:
                        print(traceback.format_exc() + "\n" + e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    return make_response(message, 200)
                return Response("Invalid parameters.", status=400)

            # GET
            elif request.method == 'GET':
                try:
                    error_detail = db_obj.execute("SELECT * FROM seo_errors")
                except Exception as e:
                    print(e)
                    return Response("Action could not be performed. Query did not execute successfully.", status=500)

                if len(error_detail) > 0:
                    return make_response(jsonify(error_detail), 200)
                else:
                    return Response("No record found for this error ID.", status=404)

            # 405
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/analysed-url/<int:url_id>', methods=['GET'])
def action_get_analysed_url(url_id):
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.
            if request.method == 'GET':
                if url_id and url_id > 0:
                    try:
                        url_detail = db_obj.execute("SELECT * FROM analysed_url WHERE id = '" + str(url_id) + "';")
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    if len(url_detail) > 0:
                        return make_response(jsonify(url_detail), 200)
                    else:
                        return Response("No record found for this error ID.", status=404)
                else:
                    return Response("No record found for this error ID.", status=404)
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/analysed-url', methods=['POST', 'GET'])
def action_analysed_url():
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.

            # POST
            if request.method == 'POST':
                # Creating a new record of analysed URL with given name, accessed-time and error_percentage.
                json_data = request.get_json()
                if 'url' in json_data and 'time_accessed' in json_data and 'error_percentage' in json_data:
                    url = json_data['url']
                    time_accessed = json_data['time_accessed']
                    error_percentage = json_data['error_percentage']

                    try:
                        db_obj.insert_data('analysed_url',
                                           [(url, time_accessed, error_percentage)],
                                           COLUMNS=['url', 'time_accessed', 'error_percentage'])
                        message = "A new URL has been added successfully!"
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    return make_response(message, 200)
                else:
                    return Response("Invalid parameters.", status=400)

            # GET
            elif request.method == 'GET':
                try:
                    analysis_detail = db_obj.execute("SELECT * FROM analysed_url")
                except Exception as e:
                    print(e)
                    return Response("Action could not be performed. Query did not execute successfully.", status=500)

                if len(analysis_detail) > 0:
                    return make_response(jsonify(analysis_detail), 200)
                else:
                    return Response("No record found for this error ID.", status=404)

            # 405
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/analysis-errors/<int:url_id>', methods=['GET'])
def action_get_analysis_errors(url_id):
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.
            if request.method == 'GET':
                if url_id and url_id > 0:
                    try:
                        url_detail = db_obj.execute(
                            """SELECT analysis_errors.id, analysed_url.url, analysed_url.time_accessed, 
                            seo_errors.name, seo_errors.error_condition, seo_errors.description FROM analysis_errors 
                            RIGHT JOIN analysed_url ON analysis_errors.url_id=analysed_url.id 
                            RIGHT JOIN seo_errors ON analysis_errors.error_id=seo_errors.id 
                            WHERE url_id = '""" + str(url_id) + "';")
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    if len(url_detail) > 0:
                        return make_response(jsonify(url_detail), 200)
                    else:
                        return Response("No record found for this error ID.", status=404)
                else:
                    return Response("No record found for this error ID.", status=404)
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/api/analysis-errors', methods=['POST', 'GET'])
def action_analysis_errors():
    if 'Auth-Key' in request.headers:
        auth_key = request.headers['Auth-Key']
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.

            # POST
            if request.method == 'POST':
                # Creating a new record of analysed URL with given name, accessed-time and error_percentage.
                json_data = request.get_json()
                if 'url_id' in json_data and 'error_id' in json_data:
                    url_id = json_data['url_id']
                    error_id = json_data['error_id']

                    try:
                        db_obj.insert_data('analysis_errors',
                                           [(url_id, error_id)],
                                           COLUMNS=['url_id', 'error_id'])
                        message = "A new URL & error match has been added successfully!"
                    except Exception as e:
                        print(e)
                        return Response("Action could not be performed. Query did not execute successfully.",
                                        status=500)
                    return make_response(message, 200)
                else:
                    return Response("Invalid parameters.", status=400)

            # GET
            elif request.method == 'GET':
                try:
                    all_records = db_obj.execute(
                        """SELECT analysis_errors.id, analysed_url.url, analysed_url.time_accessed, 
                            seo_errors.name, seo_errors.error_condition, seo_errors.description FROM analysis_errors 
                            JOIN analysed_url ON analysis_errors.url_id=analysed_url.id 
                            JOIN seo_errors ON analysis_errors.error_id=seo_errors.id;""")
                except Exception as e:
                    print(e)
                    return Response("Action could not be performed. Query did not execute successfully.", status=500)

                if len(all_records) > 0:
                    return make_response(jsonify(all_records), 200)
                else:
                    return Response("No record found for this error ID.", status=404)

            # 405
            else:
                return Response(status=405)
    return Response(status=401)


@app.route('/check-connection', methods=['POST', 'GET'])
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
        if valid_auth(auth_key):  # Valid Auth Key, proceed as usual.
            return "API is working!", 200
    return Response(status=401)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
