from aiohttp import web
import random
import asyncio

from load_balancer import load_balancer
from docker_utils import spawn_server_cntnr, kill_server_cntnr

lb : load_balancer.LoadBalancer = ""

async def home(request):
    global lb
    pass

async def add_server_handler(request):
    global lb
    pass

async def remove_server_handler(request):
    global lb
    pass

async def rep_handler(request):
    global lb
    # return a list of all the current servers

async def not_found(request):
    global lb
    print(f"Invalid Request Received")
    response_json = {
        "message": f"<Error> '{request.rel_url}' endpoint does not exist in server replicas",
        "status": "failure"
    }
    return web.json_response(response_json, status=400)


def run_load_balancer():
    global lb
    lb = load_balancer.LoadBalancer()
    app = web.Application()
    app.router.add_get('/home', home)
    app.router.add_get('/add', add_server_handler)
    app.router.add_get('/rm', remove_server_handler)
    app.router.add_get('/rep', rep_handler)

    app.router.add_route('*', '/{tail:.*}', not_found)