import requests

class Notify:
    def __init__(self):
        self.auth_base_url = 'https://run.mocky.io/v3/54dc2cf1-3add-45b5-b5a9-6bf7e7f1f4a6'
        self.response = None

    def authenticate(self):
        self.response = requests.get(self.auth_base_url)
        
        authStatus = self.response.status_code
        if authStatus >= 400 and authStatus < 500:
            return False
        else:
            return True

notify = Notify()