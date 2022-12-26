import requests
import threading
import time 

url = 'https://us-central1-glowing-bird-367505.cloudfunctions.net/eksi-gundem'  # Replace with the target URL
num_requests = 1  # Number of requests to send
num_threads = 10  # Number of threads to create
times = []
retries = 0

def retry_request(url, max_retries=10):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=120)
            # If the request was successful, return the response
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException:
            # If there was a connection error, wait and retry
            time.sleep(100*i)
            retries += 1

def send_request():
    startTime = time.time()
    for i in range(num_requests):
        response = retry_request(url)
    endTime = time.time()
    times.append(endTime - startTime)

# Create and start the threads
startTime = time.time()
print(f'Started sending requests at {time.ctime(startTime)}')
threads = []
for i in range(num_threads):
    thread = threading.Thread(target=send_request)
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
endTime = time.time()
print(f'Finished sending requests at {time.ctime(endTime)}')
print(f'Total time: {endTime - startTime}')

print(times, sum(times))
print(retries)

