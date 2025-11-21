from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import yes_no_dialog,choice
from prompt_toolkit import print_formatted_text
import os
from pathlib import Path
from convex import ConvexClient
import pyotp
from cryptography.fernet import Fernet
CONVEX_URL = os.getenv("CONVEX_URL")
convexclient = ConvexClient(CONVEX_URL)
key=convexclient.query("security:getKey")

def main():
    print_formatted_text('Welcome to the Snowflake CLI!')
    user_id = prompt('Please enter your user ID: ')
    auth=prompt('Please enter your authentication key: ')
    response = convexclient.query("users:getUserInfo",{"userId":user_id })
    if auth != response[0]['keys'][0]["name"]:
        print_formatted_text("Invalid auth key")
    result = choice(
    message="Please choose a action to continue:",
    options=[
        ("keys", "Generate OTP Key"),
        ("manage", "Manage your OTP's")
    ],
    default="keys",)
    if result=="keys":
        choices=[]
        for x in response[0]['keys'][1:]:
            choices.append((x["name"],x["name"]))
        otp_Secret=choice(
        message="Select the OTP key you want to generate the code for:",
        options=choices,
        default=choices[0][0]
        )
        for x in response[0]['keys'][1:]:
            if x["name"]==otp_Secret:
                f=Fernet(key[0]["key"])
                otp=pyotp.TOTP(f.decrypt(bytes(x["token"]))).now()
                print_formatted_text(f'Your OTP code for {otp_Secret} is: {otp}')
    elif result=="manage":
        choices=[]
        for x in response[0]['keys'][1:]:
            choices.append((x["name"],x["name"]))
        choices.append(("add","Add a new OTP key"))
        manage=choice(
        message="Select the OTP key that you want to edit or add a new one:",
        options=choices,
        default=choices[0][0]
        )
        if not manage=="add":
            manage_=choice(
                message=f"What do you want to do with {manage} key?",
                options=[
                    ("delete","Delete the OTP key"),
                    ("rename","Rename the OTP key"),
                    ("change","Change the OTP Secret")
                ]
            )
            if manage_=="delete":
                keys=response[0]['keys']
                for x in keys[1:]:
                    if x["name"]==manage:
                        keys.remove(x)
                        response = convexclient.mutation("users:updateUserKeys",{"userId": user_id,"keys":keys},)
                        print_formatted_text(f"Hey! We deleted your key")
            elif manage_=="rename":
                keys=response[0]['keys']
                for x in keys[1:]:
                    if x["name"]==manage:
                        newname=prompt("Hey! What should be the new name?")
                        x["name"]=newname
                        response = convexclient.mutation("users:updateUserKeys",{"userId": user_id,"keys":keys},)
                        print_formatted_text(f"Hey! We renamed your key")
            elif manage_=="change":
                keys=response[0]['keys']
                for x in keys[1:]:
                    if x["name"]==manage:
                        newSecret=prompt("Hey! What should be the new secret?")
                        newSecret=f.encrypt(b""+bytes(f"{newSecret}",'utf-8'))
                        x["token"]=newSecret
                        response=convexclient.mutation("users:updateUserKeys",{"userId": user_id,"keys":keys},)
                        print_formatted_text("Succesfully changed secret")
            else:
                print_formatted_text("This operation is not supported")
        elif manage=="add":
            keys=response[0]['keys']
            f=Fernet(key[0]["key"])
            name=prompt("Please enter your secret's name: ")
            secret=prompt("Please enter your secret: ")
            secret=f.encrypt(b""+bytes(secret,'utf-8'))
            keys.append({"name":name,"token":secret})
            response=convexclient.mutation("users:updateUserKeys",{"userId": user_id,"keys":keys},)
            print_formatted_text("Succesfully added new token")





            


    


    
        
