import requests

print("Testing Panic Endpoint with simulated Google Maps Location...")

session = requests.Session()

# 1. Register a user
import time
email = f"test_{time.time()}@test.com"
reg_data = {"name": "Test User", "email": email, "password": "password123"}
resp0 = session.post("http://127.0.0.1:5000/auth/register", json=reg_data)
print("Registration status:", resp0.status_code)

# 2. Add Contact
contact_data = {"name": "Mom", "relation": "Family", "phone": "9999999999"}
resp1 = session.post("http://127.0.0.1:5000/contacts/add", json=contact_data)
print("Contact Add status:", resp1.status_code)

# 3. Trigger Panic
panic_data = {"location": "https://maps.google.com/?q=21.1458,79.0882"}
resp2 = session.post("http://127.0.0.1:5000/panic", json=panic_data)
print("Panic Trigger Response:", resp2.json())
