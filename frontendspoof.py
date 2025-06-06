import requests
import json

BASE_URL = "http://localhost:8002"
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

def query_feedback_test():
    """
    Tests the POST /query-feedback endpoint.
    """
    url = f"{BASE_URL}/query-feedback"
    # Ensure there's some feedback data first for a meaningful query
    # This assumes post_feedback_test() has run and added some data
    payload = {
        "question": "What are the common themes in the feedback?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(f"Sending POST request to {url} with payload: {payload}")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Query Response Status Code: {response.status_code}")
        try:
            print(f"Query Response JSON: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"Query Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Query Request failed: {e}")
    print("-" * 20)

def topic_frequency_test():
    """
    Tests the POST /topic-frequency endpoint.
    """
    url = f"{BASE_URL}/topic-frequency"
    # Example topic; adjust as needed based on your feedback.csv content for meaningful results
    payload = {
        "topic": "meetings" 
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(f"Sending POST request to {url} with payload: {payload}")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Topic Frequency Response Status Code: {response.status_code}")
        try:
            print(f"Topic Frequency Response JSON: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"Topic Frequency Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Topic Frequency Request failed: {e}")
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

    # Test the query feedback endpoint
    print("\nTesting query feedback endpoint...")
    query_feedback_test()

    # Test the topic frequency endpoint
    print("\nTesting topic frequency endpoint...")
    topic_frequency_test()

    print("Frontend spoof tests finished.")
