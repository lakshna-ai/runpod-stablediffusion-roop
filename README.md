<div align="center">

<h1>Runpod | Automatic1111 | Worker</h1>

This worker is a RunPod worker that uses the Stable Diffusion model for AI image generation. The worker is built upon the Stable Diffusion WebUI, which is a user interface for Stable Diffusion AI models. This worker supports TXT2IMG and IMG2IMG along with roop support
</div>

## PRE-BUILT DOCKER IMAGE

https://hub.docker.com/r/navinhariharan/runpod-serverless-roop

## HOW TO USE ROOP

This generates images with the help of roop from a text prompt

```python
import requests

url = "https://api.runpod.ai/v2/stable-diffusion-v1/runsync"

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
    "authorization": "testkey"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
```

<p align="center">
    <img src="https://github.com/navin-hariharan/runpod-stablediffusion-roop/blob/main/roop_example.png"></img>
  <br/>
  <br/>
</p>
