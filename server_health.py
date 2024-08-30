import requests
import time
import sys

url = "http://localhost:5000/metrics"

def main():
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        for line in resp.text.split("\n"):
            if line.startswith("#"):
                continue
            if "last_pinged" in line:
                label, value = line.split(" ")
                time_checked = float(value)
                diff_sec = time.time() - time_checked
                if diff_sec < 60 * 5:
                    return 0
        return 1
    except Exception as e:
        print(f"Err: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
