import time
import sys
import requests
import multiprocessing


worker_process = None


def start_worker(port: int):
    global worker_process
    worker_process = multiprocessing.Process(target=work, args=[port], daemon=True)
    worker_process.start()


def stop_worker():
    if worker_process is not None:
        worker_process.kill()


###
# TODO:
# - get samples
# - check if new (how? e.g. last changed) -> if not, wait
# - train
# - update samples (in batches?)


def work(port: int):
    while True:
        print('Ping')
        sys.stdout.flush()
        try:
            result = requests.get(f'http://127.0.0.1:{port}/samples')
            print(result.json())
            sys.stdout.flush()
        except Exception as err:
            print(err)
            sys.stdout.flush()
        time.sleep(5)