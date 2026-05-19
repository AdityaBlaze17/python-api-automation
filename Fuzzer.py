import requests
import copy
import json

# --- Configuration ---
API_URL = "https://uat.nye.money/integration/api/v1/lending/get-lien-history"
AUTH_TOKEN = "eyJraWQiOiJWWTVFU053TGcwRFFQejVMUXQxRUdMT0ZNOWhJbzJsQkVCWkg1anFQekxjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwYTI3YWE3ZS00M2UxLTQxYzUtYTViZi0wZDRkNzBmOWFkMTMiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXR0cmlidXRlX2tleTIiOiJhdHRyaWJ1dGVfdmFsdWUyIiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoLTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGgtMV9KOG9UQTNzWFoiLCJjb2duaXRvOnVzZXJuYW1lIjoiY2ljb19mdF91YXQiLCJvcmlnaW5fanRpIjoiNTFiMjJmNmItODc0NS00Nzk4LTk2MDQtYWYxZDdkODI2NmRiIiwiYXVkIjoiNXQ3cHAwMmNsZWkwNTgzamcwMGVobjRhNzQiLCJldmVudF9pZCI6ImI4MjE5OWQxLWM1YzgtNGViZS1hN2U3LWUxZDMyYTc4MmY1YSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzc5MTg4MDA5LCJhdHRyaWJ1dGVfa2V5IjoiYXR0cmlidXRlX3ZhbHVlIiwiZXhwIjoxNzc5MTkxNjA5LCJpYXQiOjE3NzkxODgwMDksImp0aSI6ImM1MTdmMjAyLTg3NDgtNDA5OS04ZDk4LTQwZTRiMDg2Y2RkYyJ9.f34KoSkYTHRLp1We1RgnX314qj79gyOOly4bm491excd1az-xzeKef10hhLq4UGEy14jCPu4w1FOe6ZTxgWtO4vTgDx22IUK3Vs4HR3JZlTpCnyVlAQQgiBC1IVVG7aTLv2lVVQrXc1qDZCBWP4PYkmkHBxps3fHFWMIjtO5RUmw4Mzgko9S7df3i-gOA4H8aeTcLFR_SnkF7LEacZ0DIXqCOo416wtJ-S51WqH8VNMb6VNx1OY8sNGpf-wfz2kPRwuhtXfJ79gJIKnKxgTNcL-7xEYtGnchIoi6-T_lKi5UqBD9-joAniL30vyq58G8gUo27gU0YJElveJWojUacQ"  # <-- REPLACE THIS

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