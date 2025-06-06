import requests
import json

BASE_URL = "http://localhost:8000"

def post_feedback_test():
    """
    Tests the POST /feedback endpoint.
    """
    url = f"{BASE_URL}/feedback"
    payload = {
        "Category": "General",
        "Message": "This is a test feedback message."
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(f"Sending POST request to {url} with payload: {payload}")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"POST Response Status Code: {response.status_code}")
        try:
            print(f"POST Response JSON: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"POST Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"POST Request failed: {e}")
    print("-" * 20)

def get_feedback_test():
    """
    Tests the GET /feedback endpoint.
    """
    url = f"{BASE_URL}/feedback"
    print(f"Sending GET request to {url}")
    try:
        response = requests.get(url)
        print(f"GET Response Status Code: {response.status_code}")
        try:
            print(f"GET Response JSON: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"GET Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"GET Request failed: {e}")
    print("-" * 20)

if __name__ == "__main__":
    print("Starting frontend spoof tests...")
    # Test POST endpoint
    post_feedback_test()

    # Test GET endpoint to see the newly added feedback and any existing ones
    get_feedback_test()

    # Example of posting another feedback to see multiple entries
    print("\nPosting another feedback entry...")
    payload_2 = {
        "Category": "Bug Report",
        "Message": "Found a minor issue on the login page."
    }
    url = f"{BASE_URL}/feedback"
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, data=json.dumps(payload_2), headers=headers)
        print(f"POST Response Status Code: {response.status_code}")
        try:
            print(f"POST Response JSON: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"POST Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"POST Request failed: {e}")
    
    print("\nGetting all feedback again...")
    get_feedback_test()
    print("Frontend spoof tests finished.")
