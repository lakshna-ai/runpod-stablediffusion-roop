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
            model = inference_request['model']
            inference_request['override_settings'] = {"sd_model_checkpoint": model}
        except:
            inference_request['override_settings'] = {"sd_model_checkpoint": 'dreamshaper_8.safetensors'}
        json_data = automatic_session.post(url=f'http://127.0.0.1:3000/sdapi/v1/{endpoint}',json=inference_request, timeout=600).json()
        try:
            roop_img = inference_request['roop_img']
            for i in json_data['images']:
                index_of_i = json_data['images'].index(i)
                payload = {"source_image":roop_img,"target_image":i,"source_faces_index":[0],"face_index":[0],"upscaler":"4x_Struzan_300000","scale":2,"upscale_visibility":1,"face_restorer":"CodeFormer","restorer_visibility":1,"restore_first":1,"model":"inswapper_128.onnx","gender_source":0,"gender_target":0,"save_to_file":0,"result_file_path":""}
                face_swaped_image = requests.post('http://127.0.0.1:3000/reactor/image', headers={'accept': 'application/json','Content-Type': 'application/json'}, json=payload).json()['image']
                json_data['images'][index_of_i] = face_swaped_image
            return json_data
        except:
            return json_data
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
