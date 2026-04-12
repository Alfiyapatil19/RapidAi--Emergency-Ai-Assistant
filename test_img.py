from huggingface_hub import InferenceClient
import base64
from io import BytesIO

import os
token = os.environ.get("HF_TOKEN", "your_token_here")
client = InferenceClient(api_key=token)

try:
    print("Requesting image...")
    image = client.text_to_image("An illustration of a person doing CPR on another person. Medical guide style, clean vector.", model="black-forest-labs/FLUX.1-schnell")
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    print("SUCCESS, size:", len(img_str))
except Exception as e:
    print("FAILED FLUX")
    print(e)
    
    try:
        image = client.text_to_image("An illustration of a person doing CPR on another person. Medical guide style, clean vector.", model="stabilityai/stable-diffusion-3.5-large")
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        print("SUCCESS SD 3.5, size:", len(img_str))
    except Exception as e2:
        print("FAILED SD 3.5")
        print(e2)
