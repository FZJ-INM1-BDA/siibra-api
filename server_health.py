import requests
import time
import sys

url = "http://localhost:5000/metrics"

def main():
    resp = requests.get(url)
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

if __name__ == "__main__":
    sys.exit(main())
