import requests

class RemoteCallConnectionException(Exception):

    def __init__(self, address):
        self.address=address
        super().__init__(f"Unable to connect with the remote server with address:{self.address}")

class RemoteCallResponseException(Exception):

    def __init__(self, address):
        self.address=address
        super().__init__(f"Unable to fetch response from: {self.address}")



class RPC():

    def __init__(self, domain_name):
        self.BASE_URL = domain_name

    def get(self, path, headers, query_params):

        request_url = self.BASE_URL+path
        try:
            response = requests.get(request_url, params=query_params, headers=headers)
        except:
            print(f"Cannot communicate with {request_url}.")
            raise RemoteCallConnectionException(self.BASE_URL)   

        if response.status_code==200:
            return response.json()
        else:
            print("Invalid Response")
            print(f"Status code:{response.status_code}")
            raise RemoteCallResponseException(self.BASE_URL)
