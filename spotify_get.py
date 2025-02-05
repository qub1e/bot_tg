import requests
import base64

client_id = "46a656ffd21343b89266d8d3aa4f1ad3"
client_secret = "ac3e21281aaf46dfa9ff191d679e0753"

# Encode client_id and client_secret in Base64
auth = f"{client_id}:{client_secret}"
auth_b64 = base64.b64encode(auth.encode()).decode()

# Request access token
response = requests.post(
    "https://accounts.spotify.com/api/token",
    headers={
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={"grant_type": "client_credentials"},
)

# Parse response
token = response.json().get("access_token")
print("Access Token:", token)