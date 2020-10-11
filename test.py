import json
import requests

local_url = 'http://localhost:5000/predict'
heroku_url = 'https://speciate.herokuapp.com/predict'
floydhub_url = 'https://www.floydlabs.com/serve/HEymaCcSNwJrkYHyCQHy3Q/predict'

path = './data/image-0.jpg'
file = {'file': open(path, 'rb')}

response = requests.post(local_url, file)
print(response)
if (response.status_code == 200):
	print(response.json())