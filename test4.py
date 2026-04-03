# user_service.py

def get_user_data(user_id):
    print("fetching user")   # debug print

    if user_id == None:
        return None

    data = {"name": "Rohi", "age": 21}

    if user_id == 1:
        return data
    else:
        return data

def calculate_discount(price):
    discount = 0

    if price > 100:
        discount = price * 0.1
    elif price > 100:   # duplicate condition (bug)
        discount = price * 0.2

    return discount

def process():
    x = 10
    y = 0
    return x / y   # division by zero ❌
