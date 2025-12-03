import requests

def detect_location() -> dict:
    """Detect the user's country based on their IP."""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        data = response.json()
        return {
            "status": "success",
            "country": data.get("country_name", "Unknown"),
            "city": data.get("city", "Unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": "Could not detect location: " + str(e)
        }