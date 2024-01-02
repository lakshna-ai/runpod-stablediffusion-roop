import base64
import io
import json
import requests
from PIL import Image, PngImagePlugin

runpod_url = 'runpod_url'
runpod_api_key = 'RUNPOD_API_KEY'

def encode_image(image_path):
    im = Image.open(image_path)
    img_bytes = io.BytesIO()
    im.save(img_bytes, format='PNG')
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return img_base64

roop_img = encode_image("roop.png")

prompt = "a beautiful portrait of emma watson"
neg = "(((teeth, ugly, old)))"

payload = {
    "input": {
        "endpoint": "txt2img",
        "roop_img":roop_img,
        "prompt": prompt,
        "negative_prompt": neg,
        "seed": -1,
        "sampler_name": "Euler a",
        "steps": 20,
        "cfg_scale": 7,
        "width": 1024,
        "height": 1024,
        "restore_faces": True
    }
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": runpod_api_key
}

r = requests.post(f"{runpod_url}/run", json=payload, headers=headers).json()

DATA = 'PENDING'

while DATA != 'COMPLETED':
    r = requests.post(f"{runpod_url}/status/{r['id']}",headers=headers).json()
    DATA = r['status']

with open('output.json', 'w') as jsonfile:
    json.dump(r, jsonfile)
for i in r['output']['images']:
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
    image.save('output.png')
