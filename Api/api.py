import requests
import json
import jsonify
from flask import jsonify, Flask,request
from flask_restful import Resource, Api
from flask_cors import CORS
import uuid
from flask_mysqldb import MySQL
app = Flask(__name__)
CORS(app)
api = Api(app)
app.secret_key='secret123'

app.logger.info('Attempt mysql connection with user=root db=bh_db')
# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "Kartalx1986"
app.config['MYSQL_DB'] = "homesafety"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['default_authentication_plugin']='sha2_password'
app.logger.info('mysql connection with user=root db=homesafety successfull')

# init MYSQL
mysql = MySQL(app)

class SignIn(Resource):
    def post(self,username,password,tokenNotification):
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_password,token FROM user WHERE username = {}".format(username))
        data =cur.fetchall()
        # Checking username
        if data == ():
            postContent = jsonify(token = "Null",message ="Wrong Username")

        else:
            data=list(data)
            token_data =data[0]['token']
            pass_data =data[0]['user_password']

            # Checking password
            if password == pass_data:
                postContent = jsonify(token = uuid.uuid4(),message ="Welcome")

                    #Check and Update Token
                if token_data == tokenNotification:
                    pass
                elif token_data == None:
                     cur.execute("UPDATE user SET token={} WHERE username={};".format(tokenNotification,username))
                     # Commit to DB
                     mysql.connection.commit()
                else:
                    pass


            else:
                postContent = jsonify(token = "Null",message ="Wrong Password")
            print(username,password)
        return postContent
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()

class ForgotPassword(Resource):
    def post(self,username,oldPassword,password):
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_password FROM user WHERE username = {}".format(username))
        data =cur.fetchall()
        json_data =list(data)

        #Control Username
        if data == ():
            postContent = jsonify(message="Wrong Username")

        else:
            password_data = json_data[0]['user_password']
            
            #Control Password
            if oldPassword!=password_data:
                postContent = jsonify(message="Wrong Password")

            else:
                print(username,oldPassword,password)
                cur.execute("UPDATE user SET user_password=%s WHERE username=%s;",[password,username])
                # Commit to DB
                mysql.connection.commit()
                postContent = jsonify(message="Success")
        # Close connection
        cur.close()       
        return postContent

#Rest Api Resource Areas
    #SignIn Sources
api.add_resource(SignIn,"/<string:username>/<string:password>/<string:tokenNotification>")
    #forgetPassword Sources
api.add_resource(ForgotPassword,"/forgotPassword/<string:username>/<string:oldPassword>/<string:password>")


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)