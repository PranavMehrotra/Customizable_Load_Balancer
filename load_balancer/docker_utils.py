import os

def spawn_server_cntnr(hostname):
    try:
        # Spawn a new container with the environment variable
        res = os.popen(f'sudo docker run --name {hostname} --network mynet --network-alias {hostname} -e hostname={hostname} -d server_img:latest').read()
        
        if len(res) == 0:
            print(f"Error: Unable to start container with ID {hostname}.")
            return False
        else:
            print(f"Success: Container with ID {hostname} started successfully.")
            return True
    
    except Exception as e:
        print(f"Error: An exception occurred during container spawn: {e}")
        return False


def kill_server_cntnr(hostname):
    try:
        # Remove the container
        os.system(f"sudo docker stop {hostname} && sudo docker rm {hostname}")
        print(f"Success: Container with ID {hostname} stopped and removed.")
        return True
    
    except Exception as e:
        print(f"Error: An exception occurred during container removal: {e}")
        return False

