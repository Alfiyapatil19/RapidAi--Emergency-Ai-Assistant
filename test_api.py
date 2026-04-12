import requests
import json

data = {"emergency": "fracture", "lang": "en"}
print("Requesting AI Guide for fracture...")
resp = requests.post("http://127.0.0.1:5000/ai/guide", json=data)

try:
    res = resp.json()
    if res.get("success"):
        print("SUCCESS!")
        print("Title:", res.get("title"))
        print("Steps:", len(res.get("steps")))
        img = res.get("image_base64")
        if img:
            print("Image generated successfully. Length:", len(img))
            print("Image header:", img[:50])
        else:
            print("NO IMAGE GENERATED")
    else:
        print("FAILED:", res.get("message"))
except Exception as e:
    print("ERROR parsing JSON:", e)
    print("Response text:", resp.text)
