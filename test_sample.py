# import requests
#
# base_url = "https://gorest.co.in"
#
# def test_get_users():
#
#     response = requests.get(
#         base_url + "/public/v2/users"
#     )
#
#     assert response.status_code == 200
import pytest


#------------------------------------------------------------
#
# import pytest
# import requests
#
#
# @pytest.fixture
# def user_response():
#
#     response = requests.get(
#         "https://gorest.co.in/public/v2/users"
#     )
#
#     return response
#
#
# def test_status_code(user_response):
#
#     assert user_response.status_code == 200
#
#
# def test_json_response(user_response):
#
#     assert user_response.headers[ "Content-Type" ] == "application/json; charset=utf-8"

#----------------------------------------------------------------------------------------------#
# @pytest.fixture
# def num():
#     return [10,20,30]
#
# def test_length(num):
#     assert len(num) == 3
#
# def test_first(num):
#     assert num[0] == 10
#     assert num[1] == 20
#
# def test_sum(num):
#     assert num[0]+num[1]+num[2]== 60
#     assert sum(num) == 60
#
#----------------------------------------------------------------------------------------------#
# import pytest
#
#
# @pytest.mark.parametrize(
#     "a, b, result",
#     [
#         (10, 20, 30),
#         (5, 5, 10),
#         (2, 3, 5)
#     ]
# )
# def test_sum(a, b, result):
#
#     assert a + b == result
#
#
#
# @pytest.mark.parametrize("k,l,m,results",
#                          [
#                              (1,2,3,6),
#                              (2,3,4,9),
#                              (11,22,44,77)
#                          ]
#
# )
# def test_sumk(k,l,m,results):
#     assert k+l+m==results
#----------------------------------------------------------------------------------------------#

# import pytest
#
# @pytest.mark.parametrize("username,password,response",[
#     ("admin","1234","Success"),
#     ("aditya","1973","Success"),
#     ("micku",'0000',"Failure")]
# )
# def test_login(username,password,response):
#     if username=="admin" and password=="1234":
#         return "Success"
#
#     elif username=="micku" and password=="0000":
#         return "Failure"
#----------------------------------------------------------------------------------------------#
import pytest


@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("admin", "1234", "Success"),
        ("aditya", "1973", "Success"),
        ("micku", "0000", "Failure")
    ]
)

def test_login(username, password, expected):

    if (
        (username == "admin" and password == "1234")
        or
        (username == "aditya" and password == "1973")
    ):

        result = "Success"

    else:

        result = "Failure"

    assert result == expected


