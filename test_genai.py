from dotenv import load_dotenv
load_dotenv(override=True)
import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
try:
    with open("models.txt", "w") as f:
        f.write("OK\n")
        # Try a basic request with a well known model
        res = client.models.generate_content(model="gemini-2.0-flash", contents="hello")
        f.write(res.text)
except Exception as e:
    with open("models.txt", "w") as f:
        f.write(str(e))
