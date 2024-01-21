from aiohttp import web
import random
import asyncio
import requests
from load_balancer import LoadBalancer
from heartbeat import HeartBeat
from docker_utils import spawn_server_cntnr, kill_server_cntnr
import aiohttp

SERVER_PORT = 5000

lb : LoadBalancer = ""
hb_threads = {}

def generate_random_req_id():
    return random.randint(10000, 99999)

async def home(request):
    global lb
    
    # Generate a random request id
    req_id = generate_random_req_id()

    # Assign a server to the request using the load balancer
    server = lb.assign_server(req_id)

    print(f"Request {req_id} assigned to server: {server}", flush=True)

    try:
        # Send the request to the server and get the response, use aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{server}:{SERVER_PORT}/home') as response:
            # async with request.app['client_session'].get(f'http://{server}:{SERVER_PORT}/home') as response:
                response_json = await response.json()
                response_status = response.status
                # Return the response from the server
                return web.json_response(response_json, status=response_status, headers={"Cache-Control": "no-store"})
        # async with request.app['client_session'].get(f'http://{server}:{SERVER_PORT}/home') as response:
            # response_json = await response.json()
            # response_status = response.status
            # # Return the response from the server
            # return web.json_response(response_json, status=response_status, headers={"Cache-Control": "no-store"})
    except:
        # Request failed, return a failure response
        response_json = {
            "message": f"<Error> Request Failed",
            "status": "failure"
        }
        return web.json_response(response_json, status=400)
    
async def add_server_handler(request):
    global lb
    global hb_threads
    print("Hello", flush=True)
    # Get a payload json from the request
    payload = await request.text()
    print(payload, flush=True)
    # Get the number of servers to be added
    # num_servers = payload['n']
    num_servers = 3
    # Get the list of preferred hostnames
    # pref_hosts = payload['hostnames']
    pref_hosts = ['pranav']
    print("Hello5", flush=True)
    if num_servers<=0:
        response_json = {
            "message": f"<Error> Invalid number of servers to be added: {num_servers}",
            "status": "failure"
        }
        return web.json_response(response_json, status=400)

    # Add the servers to the system
    num_added, added_servers, err = lb.add_servers(num_servers, pref_hosts)

    if num_added<=0:
        response_json = {
            "message": f"<Error> Failed to add servers to the system",
            "status": "failure"
        }
        return web.json_response(response_json, status=400)

    print(f"Added {num_added} servers to the system")
    print(f"Added Servers: {added_servers}", flush=True)
    if err!="":
        print(f"Error: {err}")

    # Spawn the heartbeat threads for the added servers
    for server in added_servers:
        t1 = HeartBeat(lb, server)
        hb_threads[server] = t1
        t1.start()

    # Return the full list of servers in the system
    server_list = lb.list_servers()
    response_json = {
        "message": {
            "N" : len(server_list),
            "replicas": server_list
        },
        "status": "successful"
    }

    return web.json_response(response_json, status=200)



async def remove_server_handler(request):
    global lb
    global hb_threads
    # Get a payload json from the request
    # payload = await request.json()
    payload = await request.text()
    print(payload, flush=True)
    # Get the number of servers to be removed
    # num_servers = payload['n']
    num_servers = 3
    # Get the list of preferred hostnames
    # pref_hosts = payload['hostnames']
    pref_hosts = ['pranav']

    if num_servers<=0:
        response_json = {
            "message": f"<Error> Invalid number of servers to be removed: {num_servers}",
            "status": "failure"
        }
        return web.json_response(response_json, status=400)
    
    # Remove the servers from the system
    num_removed, removed_servers, err = lb.remove_servers(num_servers, pref_hosts)

    if num_removed<=0:
        response_json = {
            "message": f"<Error> Failed to remove servers from the system",
            "status": "failure"
        }
        return web.json_response(response_json, status=400)
    
    print(f"Removed {num_removed} servers from the system")
    print(f"Removed Servers: {removed_servers}", flush=True)
    if err!="":
        print(f"Error: {err}")

    # Kill the heartbeat threads for the removed servers
    for server in removed_servers:
        hb_threads[server].stop()
        del hb_threads[server]

    # Return the full list of servers in the system
    server_list = lb.list_servers()
    response_json = {
        "message": {
            "N" : len(server_list),
            "replicas": server_list
        },
        "status": "successful"
    }

    return web.json_response(response_json, status=200)


async def rep_handler(request):
    global lb
    print(f"Received Replicas Request")
    # return a list of all the current servers
    server_list = lb.list_servers()
    response_json = {
        "message": {
            "N" : len(server_list),
            "replicas": server_list
        },
        "status": "successful"
    }
    return web.json_response(response_json, status=200)

async def not_found(request):
    global lb
    print(f"Invalid Request Received", flush=True)
    response_json = {
        "message": f"<Error> '{request.rel_url}' endpoint does not exist in server replicas",
        "status": "failure"
    }
    return web.json_response(response_json, status=400)


def run_load_balancer():
    global lb
    global hb_threads
    lb = LoadBalancer()
    tem_servers = lb.list_servers()
    print(tem_servers)
    for server in tem_servers:
        hb_threads[server] = HeartBeat(lb, server)
        hb_threads[server].start()
        # t1.start()
    app = web.Application()
    app.router.add_get('/home', home)
    app.router.add_post('/add', add_server_handler)
    app.router.add_delete('/rm', remove_server_handler)
    app.router.add_get('/rep', rep_handler)

    app.router.add_route('*', '/{tail:.*}', not_found)

    web.run_app(app, port=5000)

    print("Load Balancer Ready!", flush=True)

    for thread in hb_threads.values():
        thread.join()