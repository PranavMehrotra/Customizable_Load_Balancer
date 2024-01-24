import aiohttp
import asyncio
import time
import os
import matplotlib.pyplot as plt
import json
import numpy as np


def std_dev(nums):
  return np.std(nums)

def avg(nums):
  return np.mean(nums)


# write code to send 10000 async requests to the load balancer via GET requests
frequency_map = {}
NUM_REQUESTS = 10000


async def send_request(
        session: aiohttp.ClientSession, 
        request_id : int,
        address: str, 
        port: int = 5000, 
        path: str = "/home",
        data: dict = None):
    
    global frequency_map
    if path == '/home' or path == '/rep':   # GET request
        try:
            async with session.get(f'http://{address}:{port}{path}') as response:
                resp = await response.text()
                if path == '/rep':
                    print(resp)     # print the status of the servers
                elif path == '/home':
                    resp = json.loads(resp)
                    if response.status != 200:  # failure
                        print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {resp}")
                    message = resp['message']
                    # if "Hello from Server" not in message:
                    #     print(message)
                    server_name = message.split(' ')[-1]
                    if server_name not in frequency_map:
                        frequency_map[server_name] = 1
                    else:
                        frequency_map[server_name] += 1

        except Exception as e:
            print(f"Request ID: {request_id} | Error: An exception occurred during client request: {e}")

    elif path == '/add':    # POST request
        try:
            async with session.post(f'http://{address}:{port}{path}', json=data) as response:
                resp = await response.text()
                print(resp)
                # resp = json.loads(resp)
                # # print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {resp}")

        except Exception as e:
            print(f"Request ID: {request_id} | Error: An exception occurred during client request: {e}")

    elif path == '/rm':     # DELETE request
        try:
            async with session.delete(f'http://{address}:{port}{path}', json=data) as response:
                resp = await response.text()
                # print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {resp}")

                print(resp)
                # resp = json.loads(resp)

        except Exception as e:
            print(f"Request ID: {request_id} | Error: An exception occurred during client request: {e}")


async def send_requests(
        num_requests: int, 
        address: str, 
        port_no: int, 
        path: str = "/home", 
        data: dict = None):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                tasks.append(send_request(session, i+1, address, port=port_no, path=path, data=data))
            await asyncio.gather(*tasks)
        print(f"Success: {num_requests} {path} requests to the load balancer sent successfully.")
    except Exception as e:
        print(f"Error: An exception occurred while sending multiple {path} requests: {e}")


def plot_bar_chart(frequency_map):
    servers = list(frequency_map.keys())
    frequencies = list(frequency_map.values())

    plt.bar(servers, frequencies, color='blue')
    plt.xlabel('Server Number')
    plt.ylabel('Frequency')
    plt.title('Frequency of Servers')
    plt.show()

if __name__ == '__main__':
    try:
        # Get the address of the load balancer
        lb_address = "127.0.0.1"
        port_no = 5000     # set to this for now, as LB not ready yet - finally 5000
        # num_requests = 10000

        start = time.time()
        # Send 10000 requests to the load balancer
        asyncio.run(send_requests(NUM_REQUESTS, lb_address, port_no))
        end = time.time()

        for server in frequency_map:
            print(f"{server}: {frequency_map[server]}/{NUM_REQUESTS}")


        nums_list = list(frequency_map.values())
        print("Standard deviation:", std_dev(nums_list))
        print("Average:", avg(nums_list))


        plot_bar_chart(frequency_map)
        print(f"Time taken to send 10000 requests: {end-start} seconds")

    except Exception as e:
        print(f"Error: An exception occurred in overall run: {e}")
