import requests
from utils.logger import Logger

class APIActions:
    @staticmethod
    def get(url):
        log = Logger()
        log.info(f"API Action: Sending GET request to {url}")
        response = requests.get(url)
        log.info(f"API Action: Received response with status code {response.status_code}")
        return response

    @staticmethod
    def post(url, payload):
        log = Logger()
        log.info(f"API Action: Sending POST request to {url} with payload: {payload}")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        log.info(f"API Action: Received response with status code {response.status_code}")
        return response

    @staticmethod
    def put(url, payload):
        log = Logger()
        log.info(f"API Action: Sending PUT request to {url} with payload: {payload}")
        headers = {'Content-Type': 'application/json'}
        response = requests.put(url, json=payload, headers=headers)
        log.info(f"API Action: Received response with status code {response.status_code}")
        return response

    @staticmethod
    def delete(url):
        log = Logger()
        log.info(f"API Action: Sending DELETE request to {url}")
        response = requests.delete(url)
        log.info(f"API Action: Received response with status code {response.status_code}")
        return response