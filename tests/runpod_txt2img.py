import base64
import io
import json
import requests
from PIL import Image, PngImagePlugin

runpod_url = 'THE_HOSTED_URL'
runpod_api_key = 'YOUR_API_KEY'

def encode_image(image_path):
    im = Image.open(image_path)
    img_bytes = io.BytesIO()
    im.save(img_bytes, format='PNG')
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return img_base64

roop_img = encode_image("roop.png")

prompt = "portrait of a woman"
neg = "disfigured mouth, disfigured teeth"

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
        "width": 512,
        "height": 512,
        "restore_faces": True
    }
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": runpod_api_key
}

r = requests.post(runpod_url, json=payload, headers=headers).json()
for i in r['output']['images']:
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
    image.save('output.png')
