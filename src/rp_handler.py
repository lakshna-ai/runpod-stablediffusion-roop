import io
import time
import base64
import runpod
import requests
from PIL import Image, PngImagePlugin
from requests.adapters import HTTPAdapter, Retry


automatic_session = requests.Session()
retries = Retry(total=10, backoff_factor=0.1, status_forcelist=[502, 503, 504])
automatic_session.mount('http://', HTTPAdapter(max_retries=retries))


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #
def wait_for_service(url):
    '''
    Check if the service is ready to receive requests.
    '''
    while True:
        try:
            requests.get(url)
            return
        except requests.exceptions.RequestException:
            print("Service not ready yet. Retrying...")
        except Exception as err:
            print("Error: ", err)

        time.sleep(0.2)


def run_inference(inference_request):
    '''
    Run inference on a request.
    '''
    endpoint = inference_request['endpoint']
    if endpoint in ['img2img','txt2img']:
        try:
            roop_img = inference_request['roop_img']
            inference_request["alwayson_scripts"] = {"roop": {"args":[roop_img, True, '0', '/stable-diffusion-webui/models/roop/inswapper_128.onnx', 'CodeFormer', 1, None, 1, 'None', False, True]}}
            print(inference_request)
            return automatic_session.post(url=f'http://127.0.0.1:3000/sdapi/v1/{endpoint}',json=inference_request, timeout=600).json()
        except:
            r = automatic_session.post(url=f'http://127.0.0.1:3000/sdapi/v1/{endpoint}',json=inference_request, timeout=600)
            return r.json()
    else:
        return {'error'}


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event["input"])

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    wait_for_service(url='http://127.0.0.1:3000/sdapi/v1/txt2img')

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
