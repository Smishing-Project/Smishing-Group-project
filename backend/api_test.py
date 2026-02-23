import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')

# 테스트용 악성url
test_url = "http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/"

# API 요청
endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
payload = {
    "client": {
        "clientId": "smishing-detector",
        "clientVersion": "1.0.0"
    },
    "threatInfo": {
        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
        "platformTypes": ["ANY_PLATFORM"],
        "threatEntryTypes": ["URL"],
        "threatEntries": [{"url": test_url}]
    }
}

response = requests.post(
    f"{endpoint}?key={api_key}",
    json=payload
)

print(f"상태 코드: {response.status_code}")
print(f"응답: {response.json()}")

if response.status_code == 200: # 200 응답이 왔다면
    print("API Activate")
else:
    print("API Error")