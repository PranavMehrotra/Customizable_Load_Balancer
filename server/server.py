from aiohttp import web
import os
import datetime
import json
import random
import string
import asyncio

server_id = ""

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

async def home(request):
    try:

        # Print when the request is received
        print(f"Received Home Request at {datetime.datetime.now()}")

        response_data = {
            "message": f"Hello from Server: {server_id}",
            "status": "successful"
        }

        
        # Print when the response is generated
        print(f"Generated Home Response at {datetime.datetime.now()}")
        return web.json_response(response_data, status=200, headers={"Cache-Control": "no-store"})
    
    except Exception as e:
        # Log the exception and return an error response
        print(f"Error in home endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

async def heartbeat(request):
    try:
    
        # Print when the request is received
        print(f"Received Heartbeat Request at {datetime.datetime.now()}")

        # Print when the response is generated
        print(f"Generated Heartbeat Response at {datetime.datetime.now()}")
        return web.Response(status=200)
    
    except Exception as e:
        # Log the exception and return an error response
        print(f"Error in heartbeat endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

async def not_found(request):
    # Print when a request for an unknown endpoint is received
    print(f"Received Not Found Request at {datetime.datetime.now()}")
    return web.Response(text="Not Found", status=400)  # Return a 400 Bad Request response

def run_server():
    app = web.Application()
    app.router.add_get('/home', home)
    app.router.add_get('/heartbeat', heartbeat)

    # Catch-all route for any other endpoint
    app.router.add_route('*', '/{tail:.*}', not_found)

    web.run_app(app, port=5000)

if __name__ == '__main__':
    server_id = os.environ.get("SERVER_ID")
    if not server_id:
        # Generate a random string if SERVER_ID is not set
        server_id = generate_random_string(6)
    run_server()
