import http.client
import json

HOST = "127.0.0.1"
PORT = 5000
ENDPOINT = "/temperature"

test_cases = [
    
    ("Valid New York", "40.7128", "-74.0060", 200),
    ("Valid London", "51.5074", "-0.1278", 200),
    ("Valid Tokyo", "35.6895", "139.6917", 200),

    
    ("Missing lat", None, "-74.0060", 400),
    ("Missing lng", "40.7128", None, 400),
    ("Missing both lat/lng", None, None, 400),
 

  
    
    ("Extra query params", "40.7128", "-74.0060&extra=123", 200),
    ("Very small decimal values", "40.0000001", "-74.0000001", 200),
    ("Very large decimal values", "40.712812345678", "-74.006012345678", 200),


]

def make_request(lat, lng):
    """Send HTTP request to flask api."""
    conn = http.client.HTTPConnection(f"{HOST}:{PORT}")

    if lat is None and lng is None:
        url = ENDPOINT
    elif lat is None:
        url = f"{ENDPOINT}?lng={lng}"
    elif lng is None:
        url = f"{ENDPOINT}?lat={lat}"
    else:
        url = f"{ENDPOINT}?lat={lat}&lng={lng}"

    conn.request("GET", url)
    response = conn.getresponse()

    
    status_code = response.status
    try:
        data = json.loads(response.read().decode("utf-8"))
    except json.JSONDecodeError:
        data = None  

    conn.close()
    return status_code, data

def run_tests():
    """Run all test cases and display results."""
    passed, failed = 0, 0

    for name, lat, lng, expected_status in test_cases:
        status_code, response = make_request(lat, lng)

        if status_code == expected_status:
            print(f" {name} - Passed")
            passed += 1
        else:
            print(f" {name} - Failed (Expected {expected_status}, got {status_code})")
            failed += 1

    print("\n Test Summary:")
    print(f" Passed: {passed}")
    print(f" Failed: {failed}")
    print(f" Success Rate: {round((passed / len(test_cases)) * 100, 2)}%")

if __name__ == "__main__":
    run_tests()
