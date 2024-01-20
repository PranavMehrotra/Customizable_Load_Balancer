import requests
import time
import os 
import random
import string

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def container_exists(container_id):
    # Check if the container with given ID exists
    try:
        check_command = f'sudo docker ps -q -f name={container_id}'
        return os.popen(check_command).read().strip() != ""
    except Exception as e:
        print(f"Error: An exception occurred during container existence check: {e}")
        return False

def spawn_docker_container(server_id):
    try:
        # Spawn a new container with the environment variable
        res = os.popen(f'sudo docker run --name {server_id} --network mynet --network-alias {server_id} -e SERVER_ID={server_id} -d server_img:latest').read()
        
        if len(res) == 0:
            print(f"Error: Unable to start container with ID {server_id}. Please check manager logs.", 400)
        else:
            print(f"Success: Container with ID {server_id} started successfully.", 200)
    except Exception as e:
        print(f"Error: An exception occurred during container spawn: {e}")

def send_heartbeat(server_id, num_requests=5):
    try:
        print(f"Info: Waiting for the server {server_id} to initialize...")

        # Simulate some time passing
        time.sleep(10)
        
        for i in range(num_requests):
            try:
                # Send a GET request to the server
                response = requests.get(f"http://{server_id}:5000/home")
                print(f"Client - Request {i+1} - Status Code: {response.status_code} - Response: {response.text}")
                time.sleep(3)
            except Exception as e:
                print(f"Error: An exception occurred during client request {i+1}: {e}")
    except Exception as e:
        print(f"Error: An exception occurred during heartbeat: {e}")

def remove_docker_container(container_id):
    try:
        # Remove the container
        os.system(f"sudo docker stop {container_id} && sudo docker rm {container_id}")
        print(f"Success: Container with ID {container_id} stopped and removed.")
    except Exception as e:
        print(f"Error: An exception occurred during container removal: {e}")

def spawn_and_remove_container():
    try:
        # Generate a unique server_id
        server_id = generate_random_string(6)

        # Check if the container with the generated ID already exists, generate a new one if it does
        while container_exists(server_id):
            server_id = generate_random_string(6)

        # Set the server_id as an environment variable
        try:
            spawn_docker_container(server_id)
        except Exception as e:
            print(f"Error: An exception occurred during container spawn: {e}")

        # Send heartbeat
        send_heartbeat(server_id)

        # Remove the container
        try:
            remove_docker_container(server_id)
        except Exception as e:
            print(f"Error: An exception occurred during container removal: {e}")

    except Exception as e:
        print(f"Error: An exception occurred during operations on container with ID {server_id}: {e}")

if __name__ == '__main__':
    # try:
    spawn_and_remove_container()
    #     os.system(f"sudo docker stop client_con && sudo docker rm client_con")
    # except Exception as e:
    #     print(f"Error: An exception occurred during main execution: {e}")
    print("hello")