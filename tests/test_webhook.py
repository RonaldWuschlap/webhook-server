import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("Health check: PASS")
            return True
        else:
            print(f"Health check: FAIL (Status {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("Health check: FAIL (Connection refused)")
        return False

def test_deploy_webhook():
    try:
        response = requests.post(f"{BASE_URL}/webhook/deploy", json={"branch": "main"})
        if response.status_code == 200:
            print("Deploy webhook: PASS")
            print(response.json())
            return True
        else:
            print(f"Deploy webhook: FAIL (Status {response.status_code})")
            print(response.text)
            return False
    except Exception as e:
        print(f"Deploy webhook: FAIL ({e})")
        return False

def test_notify_webhook():
    try:
        response = requests.post(f"{BASE_URL}/webhook/notify", json={"event": "test"})
        if response.status_code == 200:
            print("Notify webhook: PASS")
            print(response.json())
            return True
        else:
            print(f"Notify webhook: FAIL (Status {response.status_code})")
            print(response.text)
            return False
    except Exception as e:
        print(f"Notify webhook: FAIL ({e})")
        return False

if __name__ == "__main__":
    print("Waiting for server to start...")
    for _ in range(5):
        if test_health():
            break
        time.sleep(1)
    else:
        print("Server failed to start.")
        sys.exit(1)

    success = True
    success &= test_deploy_webhook()
    success &= test_notify_webhook()

    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)
