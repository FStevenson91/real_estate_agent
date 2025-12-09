import requests

def detect_location() -> dict:
    """Detect the user's country based on their IP."""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        data = response.json()
        country = data.get("country_name", "Unknown")
        city = data.get("city", "Unknown")
        
        return {
            "status": "success",
            "country": country,
            "city": city,
            "instruction": "YOU MUST respond in professional Spanish for " + country + ". Do NOT adapt to how the user writes. Use the dialect of " + country + " ONLY."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": "Could not detect location: " + str(e)
        }