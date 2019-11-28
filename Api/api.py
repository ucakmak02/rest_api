import requests
import json
import jsonify
from flask import jsonify, Flask,request, Response, abort,send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
import uuid
from flask_mysqldb import MySQL
from functools import wraps
from flask_socketio import SocketIO

import numpy as np
import cv2
import os
import subprocess

import time

from pyfcm import FCMNotification
# image save path
path ="/src/static/"
fb_api_key = "AAAAFJdH0Qs:APA91bHuYiJqrTmxIENcvS4bfYvmU4nlPpW0xEkvPjjYNDlC6ryBP7p-BGGNzNGaPm2bJ5QkkVokxbggvC5RPmPM1T9xUlP8RxemBRW0zUPLxwp6OvhG-3mSTVJ4L6MLxPuhnJj-OsyP"
app = Flask(__name__,instance_path=path)
CORS(app)
api = Api(app)
app.secret_key='secret123'

app.logger.info('Attempt mysql connection with user=root db=bh_db')
# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "********"
app.config['MYSQL_DB'] = "homesafety"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['default_authentication_plugin']='sha2_password'
app.logger.info('mysql connection with user=root db=homesafety successfull')

# init MYSQL
mysql = MySQL(app)

socketio = SocketIO(app)
class SignIn(Resource):
    def post(self,username,password,tokenNotification):

        # Take Datas in Mysql with Username
        def data(username):
            cur = mysql.connection.cursor()
            cur.execute("SELECT user_password,token,token_storage FROM user WHERE username = %s",[username])
            data =cur.fetchall()
            return data

        # Create Token For App Storage and Save It
        def generateStorageToken(token_storage_data):
            if token_storage_data == None:
                token_storage=uuid.uuid4()
                #Save tokenStorage to database
                cur = mysql.connection.cursor()
                cur.execute("UPDATE user SET token_storage=%s WHERE username=%s;",[token_storage,username])
                # Commit to DB
                mysql.connection.commit()
                # Close connection
                cur.close()
            else:
                token_storage = token_storage_data
            return token_storage

        # Checking username
        data = data(username)
    
        if data == ():
            postContent = jsonify(token = "Null",message ="Wrong Username")

        else:
            data=list(data)
            token_data =data[0]['token']
            pass_data =data[0]['user_password']
            token_storage_data =data[0]['token_storage']

            # Checking password
            if password == pass_data:
                token_storage = generateStorageToken(token_storage_data)
                postContent = jsonify(token = token_storage,message ="Welcome")

                #Check and Update Token
                if token_data == tokenNotification:
                    pass
                elif token_data == None:
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE user SET token=%s WHERE username=%s;",[tokenNotification,username])

                    # Commit to DB
                    mysql.connection.commit()

                    # Close connection
                    cur.close()

                else:
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE user SET token=%s WHERE username=%s;",[tokenNotification,username])
                    
                    # Commit to DB
                    mysql.connection.commit()
                    
                    # Close connection
                    cur.close()


            else:
                postContent = jsonify(token = "Null",message ="Wrong Password")

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

class Status(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        user_id = json_data['userid']
        status = json_data['pictureStatus']
        socketio.emit("{}".format(user_id), {"message": status})

        return jsonify(message = status+"Status is Receipt")


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
            # Take token and Check
            cur = mysql.connection.cursor()
            cur.execute("SELECT token_storage FROM user WHERE username = %s",[foldername])
            token =cur.fetchall()
            token = list(token)[0]
            token = token['token_storage']
            print(token)

            try:
                if appSecretKey == token:
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
    number = 1
    images = request.files.getlist("images")
    data_message = {}
    for img in images:
        img.save(os.path.join(path, cust_id,f"{number}.jpg"))
        data_message[f"image_{number}"] = f"http://134.119.194.237:7000/static/highstone/{number}.jpg/47f6da8f-4409-48c4-86d2-3b926f3cbf54/"
        number += 1

    #send notification
    cur = mysql.connection.cursor()
    cur.execute("SELECT token FROM user WHERE username='{}'".format(cust_id))
    token = cur.fetchone()
    push_service = FCMNotification(api_key=fb_api_key)
    registration_id = str(f"{token['token']}")
    message_title = "Danger Detected!"
    message_body = "A Danger situation happened on oven. Due to this danger situation Nuriel turned off the oven. Please verify this stiuation!"
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body, data_message=data_message)
    # 1123123/static/1.jpg
    return jsonify(message='image received.',
                    status=200
                )
###Rest Api Resource Areas
#SignIn Sources
api.add_resource(SignIn,"/<string:username>/<string:password>/<string:tokenNotification>")
#forgetPassword Sources
api.add_resource(ForgotPassword,"/forgotPassword/<string:username>/<string:oldPassword>/<string:password>")
#status
api.add_resource(Status,"/status")








if __name__ == '__main__':
    socketio.run(host="0.0.0.0",debug=True)
