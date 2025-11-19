# snowflake : You deserve being safe
 Snowflake is a cross-platform project where you can store everything (soon™) related to your security needs.
## Accessible via
### [Pypi](https://pypi.org/project/snowflake-security/) (Python Library & Terminal)
Install using following command:

```pip install snowflake-security```

Supported functions:
 - snowflake.hello() -> Say hello to snowflake! You can use this for testing purposes
 - snowflake.add_key(id,auth_key,name,secret) -> Add a OTP key
 - snowflake.generate_otp(id,auth_key,name) -> Generate OTP
 - snowflake.remove_key(id,auth_key,name) -> Remove a OTP key

id -> User's slack ID

auth_key -> Snowflake's security solution for making sure you are you :) (Get from slack bot)

name -> Name of your OTP key

secret -> Key provided by software that you are adding 

### Slack

Available Commands
- /add-otp-key -> Add a new OTP key
- /otp -> Generate a OTP

