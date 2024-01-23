import aiohttp
import asyncio
import time
import os
import matplotlib.pyplot as plt
import json

# write code to send 10000 async requests to the load balancer via GET requests
frequency_map = {}

async def send_request(
        session: aiohttp.ClientSession, 
        request_id : int,
        address: str, 
        port: int = 5000, 
        path: str = "/home"):
    
    global frequency_map
    try:
        async with session.get(f'http://{address}:{port}{path}') as response:
            resp = await response.text()
            print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {resp}")
            resp = json.loads(resp)
            
            message = resp['message']
            server_name = message.split(' ')[-1]
            if server_name not in frequency_map:
                frequency_map[server_name] = 1
            else:
                frequency_map[server_name] += 1

    except Exception as e:
        print(f"Request ID: {request_id} | Error: An exception occurred during client request: {e}")

async def send_requests(num_requests: int, address: str, port_no: int):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                tasks.append(send_request(session, i+1, address, port=port_no))
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error: An exception occurred while sending multiple client requests: {e}")

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

        start = time.time()
        # Send 10000 requests to the load balancer
        asyncio.run(send_requests(10000, lb_address, port_no))
        end = time.time()

        plot_bar_chart(frequency_map)
        print(f"Time taken to send 10000 requests: {end-start} seconds")

    except Exception as e:
        print(f"Error: An exception occurred in overall run: {e}")
