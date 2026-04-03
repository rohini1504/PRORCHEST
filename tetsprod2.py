# auth.py

def login(username, password):
    if username == "admin" and password == "1234":
        print("Logged in")  # debug print
        return True
    return False

def execute_query(query):
    import os
    os.system(query)   # ⚠️ command injectio
