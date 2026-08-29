import requests

def gather_data(url:str, timeout = 10):
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "News_digester/0.1"})
    response.raise_for_status()
    return response.text