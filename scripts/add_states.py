import requests
import json

# US States data
states = [
    {"code": "AL", "name": "Alabama"},
    {"code": "AK", "name": "Alaska"},
    {"code": "AZ", "name": "Arizona"},
    {"code": "AR", "name": "Arkansas"},
    {"code": "CA", "name": "California"},
    {"code": "CO", "name": "Colorado"},
    {"code": "CT", "name": "Connecticut"},
    {"code": "DE", "name": "Delaware"},
    {"code": "FL", "name": "Florida"},
    {"code": "GA", "name": "Georgia"},
    {"code": "HI", "name": "Hawaii"},
    {"code": "ID", "name": "Idaho"},
    {"code": "IL", "name": "Illinois"},
    {"code": "IN", "name": "Indiana"},
    {"code": "IA", "name": "Iowa"},
    {"code": "KS", "name": "Kansas"},
    {"code": "KY", "name": "Kentucky"},
    {"code": "LA", "name": "Louisiana"},
    {"code": "ME", "name": "Maine"},
    {"code": "MD", "name": "Maryland"},
    {"code": "MA", "name": "Massachusetts"},
    {"code": "MI", "name": "Michigan"},
    {"code": "MN", "name": "Minnesota"},
    {"code": "MS", "name": "Mississippi"},
    {"code": "MO", "name": "Missouri"},
    {"code": "MT", "name": "Montana"},
    {"code": "NE", "name": "Nebraska"},
    {"code": "NV", "name": "Nevada"},
    {"code": "NH", "name": "New Hampshire"},
    {"code": "NJ", "name": "New Jersey"},
    {"code": "NM", "name": "New Mexico"},
    {"code": "NY", "name": "New York"},
    {"code": "NC", "name": "North Carolina"},
    {"code": "ND", "name": "North Dakota"},
    {"code": "OH", "name": "Ohio"},
    {"code": "OK", "name": "Oklahoma"},
    {"code": "OR", "name": "Oregon"},
    {"code": "PA", "name": "Pennsylvania"},
    {"code": "RI", "name": "Rhode Island"},
    {"code": "SC", "name": "South Carolina"},
    {"code": "SD", "name": "South Dakota"},
    {"code": "TN", "name": "Tennessee"},
    {"code": "TX", "name": "Texas"},
    {"code": "UT", "name": "Utah"},
    {"code": "VT", "name": "Vermont"},
    {"code": "VA", "name": "Virginia"},
    {"code": "WA", "name": "Washington"},
    {"code": "WV", "name": "West Virginia"},
    {"code": "WI", "name": "Wisconsin"},
    {"code": "WY", "name": "Wyoming"}
]

def get_access_token():
    """Get the access token by logging in"""
    login_url = "http://localhost:8000/api/v1/auth/login"
    # Replace these with your actual credentials
    credentials = {
        "username": "admin",
        "password": "admin"
    }
    response = requests.post(login_url, data=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception("Failed to get access token")

def add_states():
    """Add all US states to the database"""
    # token = get_access_token()
    headers = {
        "Authorization": f"Bearer",
        "Content-Type": "application/json"
    }
    
    base_url = "http://localhost:8000/api/v1/common/states"
    
    for state in states:
        # Add status=True for active states
        state_data = {**state, "status": True}
        
        try:
            response = requests.post(base_url, headers=headers, json=state_data)
            if response.status_code == 201:
                print(f"Successfully added {state['name']}")
            else:
                print(f"Failed to add {state['name']}: {response.text}")
        except Exception as e:
            print(f"Error adding {state['name']}: {str(e)}")

if __name__ == "__main__":
    add_states()
