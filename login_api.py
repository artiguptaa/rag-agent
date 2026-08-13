# api.py

from login import login

def login_api(name):
    user = login(name)

    return {
        "message": "Login successful",
        "user": user.name
    }