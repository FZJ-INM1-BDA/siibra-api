from socket import gethostname
import sys

def main():
    from api.worker.app import app
    i = app.control.inspect()
    all_workers = i.ping()
    for worker_hostnames, value in all_workers.items():
        if gethostname() in worker_hostnames:
            return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
