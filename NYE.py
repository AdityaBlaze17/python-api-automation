# import requests
# import json
#
# url="https://uat.nye.money/auth/api/v1/internals/user_id_from_mobile_number?mobileNumber=9354969417"
#
# def get_response():
#     response=requests.get(url_api)
#     json_data = response.json()
#     user_id = json_data["results"]["userId"]
#     json_sr = json.dumps(json_data, indent=4)
#     print("User Id ->", user_id)
#
# get_response()


import requests

base_url = "https://uat.nye.money/auth/api/v1/internals/user_id_from_mobile_number"

query_params = {
    "mobileNumber": "8077687033" #9354969417
}

response = requests.get(base_url, params=query_params)

json_data = response.json()

user_id = json_data["results"]["userId"]

print(query_params,user_id)