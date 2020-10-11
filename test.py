import json
import requests

local_url = 'http://localhost:5000/predict'
heroku_url = 'https://speciate.herokuapp.com/predict'
test_path = r'./test/elephant.jpg'
data = json.dumps({
    'path': test_path
})
response = requests.post(heroku_url, data)
print(response)
# if (response) {
# print(response.json())
# }