import colorlog
import requests
import json
import random
import logging

# ---------------- LOGGING CONFIG ---------------- #
handler = colorlog.StreamHandler()

handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
)

logger = logging.getLogger()

logger.addHandler(handler)

logger.setLevel(logging.INFO)

# ---------------- BASE URL ---------------- #

base_url = "https://gorest.co.in"

# ---------------- AUTH TOKEN ---------------- #

auth_token = "Bearer 163ce60307f0fadecad8ec441f416332cff8f8a3c237099e6a278afdcc2a49ad"


# ---------------- Get Request ---------------- #


def get_request():
    logging.info("Get API execution started")
    url=base_url+"/public/v2/users"
    headers={"Authorization":auth_token}
    response=requests.get(url,headers=headers)
    assert response.status_code==200
    json_data=response.json()
    json_sr=json.dumps(json_data,indent=4)
    print("Json Req. Body",json_sr)
    logging.info("API Execution Done!")



# ---------------- POST REQUEST FUNCTION ---------------- #

def post_request():

    logging.info("POST API execution started")

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

    logging.info(f"Request Payload:\n{json.dumps(payload, indent=4)}")

    # API Call
    response = requests.post(url, headers=headers, json=payload)

    logging.info(f"Actual Status Code: {response.status_code}")

    # ---------------- ASSERTION HANDLING ---------------- #

    try:

        # Intentionally wrong assertion
        assert response.status_code == 201

        logging.info("Status Code Validation Passed ✅")

    except AssertionError:

        logging.error(
            f"Status Code Validation Failed ❌ "
            f"Expected: 404, Actual: {response.status_code}"
        )

    # ---------------- RESPONSE BODY ---------------- #

    json_data = response.json()

    logging.info(
        f"Response Body:\n{json.dumps(json_data, indent=4)}"
    )

    print("Execution completed")


# ---------------- FUNCTION CALL ---------------- #
#get_request()
post_request()