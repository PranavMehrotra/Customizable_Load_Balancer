# Import necessary modules
from aiohttp import web
import os
import datetime
import json
import random
import string
import asyncio

# Initialize server_id as an empty string (will be set later)
server_id = ""

# Function to generate a random string of a given length
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# Define an asynchronous function for handling the home endpoint
async def home(request):
    try:
        # Print when the request is received
        print(f"Received Home Request at {datetime.datetime.now()}")

        # Prepare response data
        response_data = {
            "message": f"Hello from Server: {server_id}",
            "status": "successful"
        }

        # Print when the response is generated
        print(f"Generated Home Response at {datetime.datetime.now()}")
        # Return a JSON response with a 200 OK status and Cache-Control header
        return web.json_response(response_data, status=200, headers={"Cache-Control": "no-store"})
    
    except Exception as e:
        # Log the exception and return an error response if an exception occurs
        print(f"Error in home endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Define an asynchronous function for handling the heartbeat endpoint
async def heartbeat(request):
    try:
        # Print when the request is received
        print(f"Received Heartbeat Request at {datetime.datetime.now()}")

        # Print when the response is generated
        print(f"Generated Heartbeat Response at {datetime.datetime.now()}")
        # Return a simple 200 OK response
        return web.Response(status=200)
    
    except Exception as e:
        # Log the exception and return an error response if an exception occurs
        print(f"Error in heartbeat endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Define a synchronous function for handling requests to unknown endpoints
async def not_found(request):
    # Print when a request for an unknown endpoint is received
    print(f"Received Not Found Request at {datetime.datetime.now()}")
    # Return a 400 Bad Request response with a plain text message
    return web.Response(text="Not Found", status=400)

# Define the main function to run the web server
def run_server():
    # Create an instance of the web Application
    app = web.Application()

    # Add routes for the home and heartbeat endpoints
    app.router.add_get('/home', home)
    app.router.add_get('/heartbeat', heartbeat)

    # Add a catch-all route for any other endpoint, which returns a 400 Bad Request
    app.router.add_route('*', '/{tail:.*}', not_found)

    # Run the web application on port 5000
    web.run_app(app, port=5000)

# Entry point of the script
if __name__ == '__main__':
    # Get the server_id from the environment variable, or generate a random string if not set
    server_id = os.environ.get("SERVER_ID")
    if not server_id:
        server_id = generate_random_string(6)
    # Run the web server
    run_server()
