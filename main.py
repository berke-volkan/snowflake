import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import pyotp
from convex import ConvexClient
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import copy


from uuid import uuid4





app = App(token=OBB)



load_dotenv(".env")
CONVEX_URL = os.getenv("CONVEX_URL")

convexclient = ConvexClient(CONVEX_URL)

key=convexclient.query("security:getKey")
f=Fernet(key[0]['key'])



add_otp_view={
	"type": "modal",
    "private_metadata": "",
	"title": {
		"type": "plain_text",
		"text": "Snowflake",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Enter a name for this OTP key",
				"emoji": True
			},
			"optional": False
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Paste OTP Secret",
				"emoji": True
			},
			"optional": False
		}
	]
}
blocks=[
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Select an item",
						"emoji": True
					},
					"options": [

					],
					"action_id": "select_otp"
				}
			]
		},]

@app.action("select_otp")
def handle_select_key(ack, body, client):
    ack()  # Important: acknowledge the action
    response = convexclient.query(
	"users:getUserInfo",{
		"userId":body["user"]["id"] })
    selected_value = body["actions"][0]["selected_option"]["value"]
    otp=pyotp.TOTP(f.decrypt(bytes(response[0]['keys'][int(selected_value)]["token"]))).now()
    client.chat_postEphemeral(
		channel=body["channel"]["id"],
        user=body["user"]["id"],
        text=f"Your OTP for {response[0]['keys'][int(selected_value)]['name']} is: {otp}"
        
	)

@app.view("")
def handle_view_submission_events(ack, body, logger):
    ack()
    name=body["view"]["state"]["values"]['0BXy7']['plain_text_input-action']['value']
    secret=body["view"]["state"]["values"]['7FdBg']['plain_text_input-action']['value']
    
    fernet=f.encrypt(b""+bytes(f"{secret}",'utf-8'))
    user = convexclient.query(
	"users:getUserInfo",{
		"userId":body["user"]["id"] },)
    if user.__len__()==0:
        rand_token = uuid4()
        convexclient.mutation(
             "users:createUser",
             {
                 "userId": body["user"]["id"],
                 "keys":[{"name":rand_token,"token":""},{"name":name,"token":fernet}]
                 },)
        app.client.chat_postEphemeral(
        channel=body["view"]["private_metadata"],
        user=body["user"]["id"],
        text=f"Welcome! Your first key has been added with the name '{name}'. You can change it later.")
    else:
        user[0]['keys'].append({"name":f"{name}","token":fernet})
        response = convexclient.mutation(
			 "users:updateUserKeys",
			 {
				 "userId": body["user"]["id"],
				 "keys":user[0]['keys']
				 },)
        app.client.chat_postEphemeral(
        channel=body["view"]["private_metadata"],
        user=body["user"]["id"],
        text=f"Added key for {name}")



@app.command("/add-otp-key")
def otp(ack,command,client,):
    ack()
    add_otp_view["private_metadata"]=command["channel_id"]
    client.views_open(view=add_otp_view,trigger_id=command["trigger_id"])


@app.command("/otp")
def otp(ack, respond, command):
    ack()
    
    response = convexclient.query(
        "users:getUserInfo", {"userId": command["user_id"]}
    )
    
    otp = pyotp.TOTP(f.decrypt(bytes(response[0]['keys'][0]["token"]))).now()
    
    channel_id = command["channel_id"]

    # blocks'u her seferinde temizle / kopya oluştur
    local_blocks = copy.deepcopy(blocks)  # blocks sabitse deep copy ile temiz kopya al
    local_blocks[1]['elements'][0]['options'] = []  # eski seçenekleri sıfırla

    for x in range(len(response[0]['keys'])):
        local_blocks[1]['elements'][0]['options'].append({
            "text": {"type": "plain_text", "text": f"{response[0]['keys'][x]['name']}", "emoji": True},
            "value": f"{x}"                           
        })

    app.client.chat_postEphemeral(
        channel=channel_id,
        user=command["user_id"],
        blocks=local_blocks
    )


if __name__ == "__main__":
    handler = SocketModeHandler(app, APP)
    handler.start()


