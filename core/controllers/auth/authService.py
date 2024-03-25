import requests

class Auth:
    def __init__(self):
        self.auth_base_url = 'https://run.mocky.io/v3/5794d450-d2e2-4412-8131-73d0293ac1cc'
        self.response = None

    def authenticate(self):
        self.response = requests.get(self.auth_base_url)
        
        authStatus = self.response.status_code
        if authStatus >= 400 and authStatus < 500:
            return False
        else:
            return True

auth = Auth()
