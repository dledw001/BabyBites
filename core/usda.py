import requests
from django.conf import settings

def search_usda_foods(query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": query,
        "pageSize": 5,
        "api_key": settings.USDA_API_KEY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
