import requests
import json
import jsonify
from flask import jsonify, Flask,request, Response, abort,send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
import uuid
from flask_mysqldb import MySQL
from functools import wraps

import numpy as np
import cv2
import os
# image save path
path = "/home/dreamventures/hs/projects/HomeSafety/RestApi/Api/static"

app = Flask(__name__,instance_path="/home/ugur/hs/projects/RestApiHomeSafety/Api/static")
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
        cur.execute("SELECT user_password,token FROM user WHERE username = %s",[username])
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
                     cur.execute("UPDATE user SET token=%s WHERE username=%s;",[tokenNotification,username])
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
        cur.execute("SELECT user_password FROM user WHERE username = %s",[username])
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



def special_requirement(f):
    @wraps(f)
    def wrap(*args ,**kwargs):
        try:
            appSecretKey = "bluerabbitt"
            if appSecretKey == "bluerabbit":
                return f(*args ,**kwargs)
            else:
                return "access close"
        except:
            return "wrap except"
    return wrap

@app.route("/static/<string:foldername>/<string:filename>/")
@special_requirement
def protected(foldername,filename):
    try:
        return send_from_directory(os.path.join(app.instance_path,''),foldername+"/"+filename)

    except Exception as e:
        return e

@app.route("/static/<string:foldername>/<string:filename>/<string:appSecretKey>/")

def protectedOpenWithKey(foldername,filename,appSecretKey):

    def special_requirement(f):
        @wraps(f)
        def wrap(*args ,**kwargs):
            try:
                if appSecretKey == "bluerabbit":
                    return f(*args ,**kwargs)
                else:
                    return "token except"
            except:
                return "wrap except"
        return wrap
    @special_requirement
    def decorater(foldername,filename,appSecretKey):
        try:
            return send_from_directory(os.path.join(app.instance_path,''),foldername+"/"+filename)

        except Exception as e:
            return e
    return decorater(foldername,filename,appSecretKey)

@app.route("/send_images/<string:cust_id>",methods=["POST"])
def send_images(cust_id):
    # checks if customer folder exists
    if not os.path.exists(os.path.join(path, cust_id)):
        os.makedirs(os.path.join(path, cust_id))
    # get the current number of images on customer folder
    number = len(os.listdir(os.path.join(path, cust_id)))
    nparr = np.fromstring(request.data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # save image to customer folder
    cv2.imwrite(os.path.join(path, cust_id,f"{number}.jpg"), img)
    return jsonify(message='image received.',
                    status=200
                )
#Rest Api Resource Areas
    #SignIn Sources
api.add_resource(SignIn,"/<string:username>/<string:password>/<string:tokenNotification>")
    #forgetPassword Sources
api.add_resource(ForgotPassword,"/forgotPassword/<string:username>/<string:oldPassword>/<string:password>")






if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
