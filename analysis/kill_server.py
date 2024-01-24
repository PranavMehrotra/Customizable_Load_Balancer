import aiohttp
import asyncio
import time
import threading
import os
import json
import random

from analysis import plot_bar_chart

# write code to send 10000 async requests to the load balancer via GET requests
frequency_map = {}
unique_servers = []

async def send_request(
        session: aiohttp.ClientSession, 
        request_id : int,
        address: str, 
        port: int = 5000, 
        path: str = "/home",
        data: dict = None):
    
    global frequency_map, unique_servers
    if path == '/home' or path == '/rep':   # GET request
        try:
            async with session.get(f'http://{address}:{port}{path}') as response:
                resp = await response.text()
                if path == '/rep':
                    print(resp)     # print the status of the servers
                elif path == '/home':
                    resp = json.loads(resp)
                    # print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {resp}")
                    message = resp['message']
                    # if "Hello from Server" not in message:
                    #     print(message)
                    server_name = message.split(' ')[-1]
                    if server_name not in frequency_map:
                        unique_servers.append(server_name)
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

def kill_server():
    global unique_servers
    time.sleep(5)
    # print(unique_servers, len(unique_servers), flush=True)
    hostname = random.choice(unique_servers)
    print(f"Killing server: {hostname} ...")
    os.system(f"sudo docker stop {hostname} && sudo docker rm {hostname}")
    print(f"Success: Container with ID {hostname} stopped and removed.")

    return 
    
if __name__ == "__main__":
    # send 2500 requests initially (/add)
    address = "127.0.0.1"

    # start thread to kill server
    t = threading.Thread(target=kill_server)
    t.start()
    
    num_requests = 30000
    asyncio.run(send_requests(num_requests//30, address, 5000, "/home"))
    asyncio.run(send_requests(num_requests, address, 5000, "/home"))
    print("Server stats:\n")
    for server in frequency_map:
        print(f"{server}: {frequency_map[server]}/{num_requests}")

    plot_bar_chart(frequency_map)
    
    t.join()
    
    


    # add a server (/add)
    data = {
        'n': 1,
        'hostnames': ['serverX']
    }


    asyncio.run(send_requests(1, address, 5000, '/add', data=data))
    asyncio.run(send_requests(1, address, 5000, '/rep'))

    # remove a server (/rm)
    data = {
        'n': 1,
        'hostnames': ['serverX']
    }

    asyncio.run(send_requests(1, address, 5000, '/rm', data=data))
    asyncio.run(send_requests(1, address, 5000, '/rep'))



    # exit(0)

    # print("\n")
    # # kill server 1
    # try:
    #     # Remove the container

    #     # os.system(f"sudo docker stop {hostname} && sudo docker rm {hostname}")

    #     # reset frequency map
    #     frequency_map = {server: 0 for server in frequency_map}
    #     print(frequency_map)

    #     # send 2500 requests again (/home)
    #     asyncio.run(send_requests(num_requests, address, 5000, '/home'))
    #     print("Server stats after killing server:\n")
    #     for server in frequency_map:
    #         print(f"{server}: {frequency_map[server]}/{num_requests}")

    #     # add a server (/add)
    #     data = {
    #         'n': 1,
    #         'hostnames': ['serverX']
    #     }

    #     asyncio.run(send_requests(1, address, 5000, '/add', data=data))
    #     asyncio.run(send_requests(1, address, 5000, '/rep'))

    #     # remove a server (/rm)
    #     data = {
    #         'n': 1,
    #         'hostnames': ['serverX']
    #     }

    #     asyncio.run(send_requests(1, address, 5000, '/rm', data=data))
    #     asyncio.run(send_requests(1, address, 5000, '/rep'))


    # except Exception as e:
    #     print(f"Error: An exception occurred during container removal: {e}")

    