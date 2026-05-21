import requests
import copy
import json



#-----Dev-> Aditya Chouhan------#

# --- Configuration ---
API_URL = "https://uat.nye.money/integration/api/v1/lending/get-lien-history"
AUTH_TOKEN = "eyJraWQiOiJWWTVFU053TGcwRFFQejVMUXQxRUdMT0ZNOWhJbzJsQkVCWkg1anFQekxjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwYTI3YWE3ZS00M2UxLTQxYzUtYTViZi0wZDRkNzBmOWFkMTMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXR0cmlidXRlX2tleTIiOiJhdHRyaWJ1dGVfdmFsdWUyIiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoLTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGgtMV9KOG9UQTNzWFoiLCJjb2duaXRvOnVzZXJuYW1lIjoiY2ljb19mdF91YXQiLCJvcmlnaW5fanRpIjoiZTVjZDkyMjktMmZiNC00NDMwLTk2NTYtZTViZWQzMGQ2ZTcxIiwiYXVkIjoiNXQ3cHAwMmNsZWkwNTgzamcwMGVobjRhNzQiLCJldmVudF9pZCI6ImU2N2Q4YzA5LTRkMmYtNGI5ZS1iNzY3LTFjYzNmZDcxNTIzZCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzc5Mjc4NDIzLCJhdHRyaWJ1dGVfa2V5IjoiYXR0cmlidXRlX3ZhbHVlIiwiZXhwIjoxNzc5MjgyMDIzLCJpYXQiOjE3NzkyNzg0MjMsImp0aSI6ImI2NDRiMjhlLWI2MGUtNDhkOC04MGM0LTU4MDM0YmNlN2RhZiJ9.zyudfuSpdT_T-GfAh9YwL3nRp-lsjzonP7iSfJcrb-8kT8BBLVBZFwyZ_SMJ_JcNAdKHBKdAhwBhKttZzzRqho8g9tri-VxDTFYSh-nV_P9WZBmYPOUC3kvTR-7VF2DccZq1cqNrxA2PV72UugD4U49P0eHt9W8xKZB8qMcq4CcF5yYnLv9Q2WWV0k6GkKzZAF6Ws9qMO4JPHGZRhDsc2quQKCPzE5tD9v_btcf5DZ1L_VEyWil77_TunXAVNoJo3jix14S7aicWobW3HXvxWxvvQ1W5qnCQWINvtqTDkQTqqe7QwTPLfFUnLMJqW-cZIH2YA62BA5jMkjSX_QXM2g"  # <-- REPLACE THIS

BASE_PARAMS = {
    "panId": "BRIPC8556P",
    "limit": "10",
    "offset": 1,
    "clientCode": "LENDING"
}

HEADERS = {
    "Authorization": AUTH_TOKEN,
    "accept": "*/*"
}


# --- Mutation Logic ---
def generate_mutations(base_params):
    mutations = []

    # 1. Remove each key
    for key in base_params.keys():
        m = copy.deepcopy(base_params)
        del m[key]
        mutations.append({"desc": f"Removed {key}", "params": m})

    # 2. Set values to None (Empty/Null test)
    for key in base_params.keys():
        m = copy.deepcopy(base_params)
        m[key] = None
        mutations.append({"desc": f"{key} = None", "params": m})

    # 3. Invalid Data Types
    m = copy.deepcopy(base_params)
    m["offset"] = "INVALID"
    mutations.append({"desc": "offset = string", "params": m})

    return mutations


# --- Main Execution ---
def run_tests():
    print(f"--- Starting Fuzzing on UAT API ---")
    mutations = generate_mutations(BASE_PARAMS)
    test_results = []

    for test in mutations:
        try:
            response = requests.get(API_URL, params=test["params"], headers=HEADERS)
            # Logic to extract Error Code and Message from the JSON response
            error_code = "N/A"
            error_message = "No detailed message"

            try:
                data = response.json()
                if "errors" in data and isinstance(data["errors"], list) and len(data["errors"]) > 0:
                    err = data["errors"][0]
                    error_code = err.get("code", "N/A")
                    error_message = err.get("message", "N/A")
                else:
                    error_code = response.status_code
                    error_message = "HTTP " + str(response.status_code)
            except:
                error_code = response.status_code
                error_message = "Non-JSON Response"

            test_results.append({
                "test": test["desc"],
                "code": error_code,
                "message": error_message
            })
            print(f"Tested: {test['desc']} -> {error_code}")

        except Exception as e:
            print(f"Request failed for {test['desc']}: {e}")

    # --- Print Summary Report ---
    print("\n" + "=" * 95)
    print(f"{'TEST CASE':<30} | {'ERROR CODE':<25} | {'MESSAGE'}")
    print("-" * 95)
    for res in test_results:
        print(f"{res['test']:<30} | {str(res['code']):<25} | {res['message']}")
    print("=" * 95)


if __name__ == "__main__":
    run_tests()