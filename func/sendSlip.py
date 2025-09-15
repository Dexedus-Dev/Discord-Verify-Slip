import requests
import json

def sendSlip(image_data_uri: str) -> dict:
    payload = {"img": image_data_uri}
    try:
        print("=== sendSlip Debug ===")
        print("Payload size:", len(image_data_uri), "characters")
        response = requests.post(
            "https://slip-c.oiioioiiioooioio.download/api/slip",
            json=payload,
            timeout=15
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return {"error": str(e)}

def sendSlipV2(refNbr: str, amount: str, token: str) -> dict:
    payload = {"refNbr": refNbr, "amount": amount, "token": token}
    headers = {"Content-Type": "application/json"}
    try:
        print("=== sendSlipV2 Debug ===")
        print("Payload:", json.dumps(payload, indent=2))
        response = requests.post(
            "https://api.openslipverify.com",
            json=payload,
            headers=headers,
            timeout=15
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return {"error": str(e)}
