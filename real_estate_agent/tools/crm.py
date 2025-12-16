import requests
import os

def create_contact(name: str, email: str, phone_number: str) -> dict:
    """Creates a new contact in the CRM."""
    try:
        url = "https://api.spicytool.net/spicyapi/v1/contact"

        headers = {
            "Authorization": os.getenv("SPICY_API_TOKEN"),
            "Content-Type": "application/json"
        }
        
        body = {
            "name": name,
            "email": email,
            "phoneNumber": phone_number
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        data = response.json()
        
        return {
            "status": "success",
            "contact": data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": "Could not create contact: " + str(e)
        }


def get_contact(contact_id: str) -> dict:
    """Gets a contact by ID from the CRM."""
    try:
        url = "https://api.spicytool.net/spicyapi/v1/contact/" + contact_id
        
        headers = {
            "Authorization": os.getenv("SPICY_API_TOKEN"),
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # If the CRM returns an error disguised as a success
        if data.get("message") or not data.get("name"):
            return {
                "status": "not_found",
                "contact": None
            }
        
        return {
            "status": "success",
            "contact": data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": "Could not get contact: " + str(e)
        }
    
def update_contact(contact_id: str, name: str = None, email: str = None, phone_number: str = None) -> dict:
    """Updates a contact in the CRM."""
    try:
        url = "https://api.spicytool.net/spicyapi/v1/contact/" + contact_id
        
        headers = {
             "Authorization": os.getenv("SPICY_API_TOKEN"),
            "Content-Type": "application/json"
        }
        
        body = {}
        if name:
            body["name"] = name
        if email:
            body["email"] = email
        if phone_number:
            body["phoneNumber"] = phone_number
        
        response = requests.put(url, headers=headers, json=body, timeout=10)
        data = response.json()
        
        return {
            "status": "success",
            "contact": data
        }
        
    except Exception as e:
        return {
           "status": "error",
            "error_message": "Could not update contact: " + str(e)
        }

def list_contacts(search_term: str = None, page: int = 1, limit: int = 10) -> dict:
    """Lists contacts from the CRM."""
    try:
        url = "https://api.spicytool.net/spicyapi/v1/contacts?page=" + str(page) + "&limit=" +str(limit)
        
        headers = {
             "Authorization": os.getenv("SPICY_API_TOKEN"),
            "Content-Type": "application/json"
        }
        
        body = {}
        if search_term:
            body["searchTerm"] = search_term
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        data = response.json()
        
        return {
             "status": "success",
            "contacts": data
        }
        
    except Exception as e:
        return {
           "status": "error",
            "error_message": "Could not list contacts: " + str(e)
        }
    
def delete_contact(contact_id: str) -> dict:
    """Delete a contact from the CRM."""
    try:
        url= "https://api.spicytool.net/spicyapi/v1/contact/" + contact_id

        headers = {
            "Authorization": os.getenv("SPICY_API_TOKEN"),
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers, timeout=10)
        data = response.json()

        return {
             "status": "success",
            "message": data
        }
    
    except Exception as e:
        return {
           "status": "error",
            "error_message": "Could not delete contact: " + str(e)
        }