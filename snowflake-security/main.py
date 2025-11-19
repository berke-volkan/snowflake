from dotenv import load_dotenv
import os
from convex import ConvexClient
from cryptography.fernet import Fernet
import pyotp
load_dotenv(".env.local")

CONVEX_URL = os.getenv("CONVEX_URL")
convexclient = ConvexClient(CONVEX_URL)
key=convexclient.query("security:getKey")
f=Fernet(key[0]['key'])


def hello():
    print("Hello from Snowflake!")


def generate_otp(id,auth_key,name):
    response = convexclient.query(
	"users:getUserInfo",{
		"userId":id })
    if auth_key != response[0]['keys'][0]["authKey"]:
        return "Invalid auth key"
    else:
        for x in response[0]['keys']:
            if x["name"]==name:
                otp=pyotp.TOTP(f.decrypt(bytes(x["token"]))).now()
                return otp

def add_key(id,auth_key,name,secret):
    response = convexclient.query(
	"users:getUserInfo",{
		"userId":id })
    if auth_key != response[0]['keys'][0]["authKey"]:
        return "Invalid auth key"
    else:
        keys=response["keys"]
        secret=f.encrypt(b""+bytes(secret,'utf-8'))
        keys.append({"name":name,"token":secret})
        response=convexclient.mutation("users:updateUserKeys",{"userId":id,"keys":keys},)
        return "Succesfully added new token"
def remove_key(id,auth_key,name):
    response = convexclient.query(
	"users:getUserInfo",{
		"userId":id })
    if auth_key != response[0]['keys'][0]["authKey"]:
        return "Invalid auth key"
    else:
        keys=response["keys"]
        for x in keys:
            if x["name"==name]:
                keys.remove(x)
                response=convexclient.mutation("users:updateUserKeys",{"userId":id,"keys":keys},)
                return "Succesfully deleted token"


