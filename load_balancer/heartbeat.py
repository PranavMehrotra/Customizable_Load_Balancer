import threading
import signal
import sys
import os
import requests
import concurrent.futures
import time
import aiohttp
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from main import active_flag
from consistent_hashing import RWLock, consistent_hashing
from docker_utils import spawn_server_cntnr, kill_server_cntnr


async def check_heartbeat(Lb, server_name, server_ip="127.0.0.1", server_port=5000):
    print("Heartbeat thread started for server: ", server_name)
    
    while True:
        print("Starting a session!")
        async with aiohttp.ClientSession() as session:
            print("Session started!")
            
            try:
                async with session.get(f'http://{server_ip}:{server_port}/heartbeat') as response:
                    print("Connected to server, Response received!")
                    # if response.status != 200 and {await response.text()}['message'] != "ok":
                    if response.status != 200:
                        Lb.active_flag[server_name] += 1
                        if Lb.active_flag[server_name] >= 2:
                            print(f"Server {server_name} is down!")
                            Lb.active_flag[server_name] = 0
                            
                            #remove server from
                            Lb.remove_servers(1, [server_name])
                            
                            # reinstantiate an image of the server
                            Lb.add_servers(1, [server_name])
                            
                            print("Closing session!")
                            await session.close()
                            
                            break
                    else :
                        Lb.active_flag[server_name] = 0        

            # except aiohttp.client_exceptions.ClientConnectorError as e:
            except Exception as e: # this is better as it is more generic and will catch all exceptions
                print(f"Could not connect to server {server_name} due to {str(e.__class__.__name__)}")
                Lb.active_flag[server_name] = 0 
                    
                #remove server from
                num_rem, servers_rem, error = Lb.remove_servers(1, [server_name])
                print(f"Removed {num_rem} servers: {servers_rem}")
                
                # reinstantiate an image of the server
                num_add, servers_add, error = Lb.add_servers(1, [server_name])
                print(f"Added {num_add} servers: {servers_add}")
                
                await session.close()
                print("Closing session!")
                
                break
        
        print("Closing session and sleeping!") 
        await session.close()              
                        
        await asyncio.sleep(0.2)

    return
    

        
    
    