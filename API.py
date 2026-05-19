import pytest
import requests
import json
import random
import string

from urllib3 import proxy_from_url

#base url:
base_url="https://gorest.co.in"

#token
auth_token="Bearer 163ce60307f0fadecad8ec441f416332cff8f8a3c237099e6a278afdcc2a49ad"
#Get request
def get_request():
    url=base_url+"/public/v2/users"
    headers={"Authorization":auth_token}
    response=requests.get(url,headers=headers)
    assert response.status_code==200
    json_data=response.json()
    json_sr=json.dumps(json_data,indent=4)
    print("Json Req. Body",json_sr)

def post_request():

    url = base_url + "/public/v2/users"

    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }

    # Random email generator
    random_num = random.randint(1000, 9999)

    payload = {
        "name": "Rahul QA",
        "gender": "male",
        "email": f"rahul{random_num}@gmail.com",
        "status": "active"
    }

    response = requests.post(url, headers=headers, json=payload)

    # Status Code Validation
    assert response.status_code == 201

    # Convert response into JSON
    json_data = response.json()

    # Pretty print response
    json_sr = json.dumps(json_data, indent=4)

    print("POST Response:\n", json_sr)

    # Validations
    assert json_data["name"] == payload["name"]
    assert json_data["status"] == payload["status"]

    print("User created successfully ")


def delete_request():
    url=base_url+"/public/v2/users/8469261"
    headers = {"Authorization": auth_token}
    response=requests.delete(url,headers=headers)
    #print("Status code",response.status_code)
    #print("Message-> ",response.message)
    #assert response.status_code==204
    if response.status_code==404:
        print("Request already fullfilled with status code-> ",response.status_code)
    elif response.status_code==204:
        print("Data deleted successfully witb status code-> ", response.status_code)

delete_request()

#post_request()
#get_request()


