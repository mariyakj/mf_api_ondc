from ondc_api import send_request

if __name__ == "__main__":
    action = "search"  # Change to "on_search", "init", etc.
    response = send_request(action)
    print("\nAPI Response:", response)
