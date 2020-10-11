import json
import requests

local_url = 'http://localhost:5000/predict'
heroku_url = 'https://speciate.herokuapp.com/predict'
floydhub_url = 'https://www.floydlabs.com/serve/JeAa7YgKvaPFGuPcohGkag/predict'
test_path = r'./test/elephant.jpg'
data = json.dumps({
    'path': test_path
})
response = requests.post(floydhub_url, data)
print(response)
# print(response.json())