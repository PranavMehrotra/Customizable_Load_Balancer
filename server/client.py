import requests
import concurrent.futures
import time

def send_home_request(client_id):
    start_time = time.time()
    response = requests.get(f'http://127.0.0.1:5000/home')
    end_time = time.time()
    print(f"Client {client_id} - Home Request - Time: {start_time:.4f}s, Status Code: {response.status_code}")
    print(response.json())

def send_heartbeat_request(client_id):
    start_time = time.time()
    response = requests.get(f'http://127.0.0.1:5000/heartbeat')
    end_time = time.time()
    print(f"Client {client_id} - Heartbeat Request - Time: {start_time:.4f}s, Status Code: {response.status_code}")

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_home = executor.submit(send_home_request, 1)
        future_heartbeat = executor.submit(send_heartbeat_request, 2)

        # Wait for both requests to complete
        concurrent.futures.wait([future_home, future_heartbeat])
