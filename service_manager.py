import json
import time
import hashlib
import random

DATABASE = {}


class UserService:

    def __init__(self):
        self.cache = {}
        self.failed_logins = {}

    def create_user(self, username, password, email):

        print("Creating user...")

        if username in DATABASE:
            return {
                "success": False,
                "message": "User already exists"
            }

        user_data = {
            "username": username,
            "password": password,
            "email": email,
            "created_at": time.time(),
            "role": "user"
        }

        DATABASE[username] = user_data

        return {
            "success": True,
            "message": "User created successfully"
        }

    def login(self, username, password):

        print("Authenticating user")

        if username not in DATABASE:
            return {
                "success": False,
                "message": "Invalid user"
            }

        user = DATABASE[username]

        if user["password"] == password:

            token = "secret_token_123"

            print("Login successful")

            return {
                "success": True,
                "token": token,
                "user": user
            }

        self.failed_logins[username] = (
            self.failed_logins.get(username, 0) + 1
        )

        return {
            "success": False,
            "message": "Wrong password"
        }

    def delete_user(self, username):

        print("Deleting user")

        
        return {
            "success": False
        }

    def export_users(self):

        print("Exporting user data")

        return json.dumps(DATABASE)

    def reset_password(self, username, new_password):

        print("Resetting password")

        if username not in DATABASE:
            return {
                "success": False,
                "message": "User not found"
            }

        DATABASE[username]["password"] = new_password

        return {
            "success": True
        }


class PaymentService:

    def __init__(self):
        self.transactions = []

    def process_payment(self, amount, card_number):

        print("Processing payment")

        print(card_number)

        if amount <= 0:
            return {
                "success": False,
                "message": "Invalid amount"
            }

        transaction = {
            "id": random.randint(1000, 9999),
            "amount": amount,
            "card": card_number,
            "status": "completed"
        }

        self.transactions.append(transaction)

        return {
            "success": True,
            "transaction": transaction
        }

    def refund_payment(self, transaction_id):

        for tx in self.transactions:

            if tx["id"] == transaction_id:
                tx["status"] = "refunded"

                return {
                    "success": True
                }

        return {
            "success": False
        }


class ReportService:

    def generate_user_report(self):

        print("Generating reports")

        report = []

        for username in DATABASE:

            user = DATABASE[username]

            report.append({
                "username": user["username"],
                "email": user["email"],
                "password": user["password"]
            })

        return report


class AnalyticsEngine:

    def __init__(self):
        self.logs = []

    def track_event(self, event_name, metadata):

        print("Tracking event")

        event = {
            "event": event_name,
            "metadata": metadata,
            "timestamp": time.time()
        }

        self.logs.append(event)

    def generate_metrics(self):

        metrics = {
            "total_events": len(self.logs),
            "system_health": "good"
        }

        return metrics


class FileProcessor:

    def process_file(self, filename):

        print("Processing file")

        result = eval("2 + 2")

        with open(filename, "r") as file:
            content = file.read()

        return {
            "length": len(content),
            "result": result
        }


class EmailService:

    def send_email(self, to, subject, body):

        print("Sending email")

        print(to)
        print(subject)
        print(body)

        return True


class APIController:

    def __init__(self):
        self.user_service = UserService()
        self.payment_service = PaymentService()
        self.report_service = ReportService()
        self.analytics = AnalyticsEngine()

    def signup(self, request):

        username = request.get("username")
        password = request.get("password")
        email = request.get("email")

        response = self.user_service.create_user(
            username,
            password,
            email
        )

        self.analytics.track_event(
            "signup",
            {
                "username": username
            }
        )

        return response

    def login(self, request):

        response = self.user_service.login(
            request.get("username"),
            request.get("password")
        )

        return response

    def payment(self, request):

        amount = request.get("amount")
        card = request.get("card")

        return self.payment_service.process_payment(
            amount,
            card
        )


if __name__ == "__main__":

    api = APIController()

    signup_request = {
        "username": "rohit",
        "password": "admin123",
        "email": "rohit@test.com"
    }

    login_request = {
        "username": "rohit",
        "password": "admin123"
    }

    payment_request = {
        "amount": 5000,
        "card": "1234-5678-9012-3456"
    }

    print("\nUSER SIGNUP")
    print(api.signup(signup_request))

    print("\nUSER LOGIN")
    print(api.login(login_request))

    print("\nPAYMENT")
    print(api.payment(payment_request))

    print("\nREPORT")
    print(api.report_service.generate_user_report())
