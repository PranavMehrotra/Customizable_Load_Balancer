import aiohttp
import asyncio
import time
import os

# write code to send 10000 async requests to the load balancer via GET requests

async def send_request(
        session: aiohttp.ClientSession, 
        request_id : int,
        address: str, 
        port: int = 5000, 
        path: str = "/home"):
    try:
        async with session.get(f'http://{address}:{port}/{path}') as response:
            print(f"Request ID: {request_id} | Status Code: {response.status} - Response: {await response.text()}")
    except Exception as e:
        print(f"Request ID: {request_id} | Error: An exception occurred during client request: {e}")

async def send_requests(num_requests: int, address: str):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                tasks.append(send_request(session, i+1, address))
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error: An exception occurred while sending multiple client requests: {e}")

if __name__ == '__main__':
    try:
        # Get the address of the load balancer
        lb_address = os.environ.get("LB_ADDRESS")
        if lb_address is None:
            print("Error: LB_ADDRESS not set!")
            exit()      # replace with default load balancer address (to be set)

        start = time.time()
        # Send 10000 requests to the load balancer
        asyncio.run(send_requests(10000, lb_address))
        end = time.time()

        print(f"Time taken to send 10000 requests: {end-start} seconds")

    except Exception as e:
        print(f"Error: An exception occurred in overall run: {e}")




