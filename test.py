import json
import requests

local_url = 'http://localhost:5000/predict'
test_path = r'./test/elephant.jpg'
data = json.dumps({
    'path': test_path
})
response = requests.post(local_url, data)
print(response.json())