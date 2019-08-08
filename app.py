from flask import Flask, request, Response,jsonify, make_response

import json
import dbMysql
import dbClass
import env

app = Flask(__name__)
mysql_obj = dbMysql.DbMysql(env.DB_HOST, env.DB_PORT, env.DB_USERNAME, env.DB_PASSWORD, env.DB_DATABASE)
db_obj = dbClass.DbWrapper(mysql_obj)


@app.route('/check_connection', methods=['POST', 'GET'])
def check_connection():
    # Validate the request body contains JSON
    if request.is_json:
        req = request.get_json()
        res = make_response(jsonify({"message": "All okay!", "request": req}), 200)
        return res
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070)
