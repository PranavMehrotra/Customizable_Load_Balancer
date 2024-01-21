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


from consistent_hashing import RWLock, consistent_hashing
from docker_utils import spawn_server_cntnr, kill_server_cntnr

class HeartBeat(threading.Thread):
    def __init__(self, lb, server_name, server_port=5000):
        super(HeartBeat, self).__init__()
        self._lb = lb
        self._server_name = server_name
        self._server_port = server_port
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    async def run(self):
        lb = self._lb
        server_name = self._server_name
        server_port = self._server_port
        print("Heartbeat thread started for server: ", server_name)
        
        cntr = 0
        while True:
            # Check if the thread is stopped
            if self.stopped():
                print("Stopping heartbeat thread for server: ", server_name)
                return
            # print("Starting a session!")
            async with aiohttp.ClientSession() as session:
                print("Session started!")
                
                try:
                    async with session.get(f'http://{server_name}:{server_port}/heartbeat') as response:
                        # print("Connected to server, Response received!")
                        # if response.status != 200 and {await response.text()}['message'] != "ok":
                        
                        ## To-Do: Check for timeout also
                        
                        if response.status != 200 and response.status != 400:
                            cntr += 1
                            if cntr >= 2:
                                # Check if the thread is stopped
                                if self.stopped():
                                    print("Stopping heartbeat thread for server: ", server_name)
                                    await session.close()
                                    return
                                print(f"Server {server_name} is down!")
                                print(f"Spawning a new server: {server_name}!")
                                cntr = 0
                                
                                #remove server from
                                lb.remove_servers(1, [server_name])
                                
                                # reinstantiate an image of the server
                                lb.add_servers(1, [server_name])
                                
                                # print("Closing session!")
                                # await session.close()
                                
                                # break
                        else :
                            cntr = 0

                # except aiohttp.client_exceptions.ClientConnectorError as e:
                except Exception as e: # this is better as it is more generic and will catch all exceptions
                    print(f"Could not connect to server {server_name} due to {str(e.__class__.__name__)}")
                    cntr = 0 
                    # Check if the thread is stopped
                    if self.stopped():
                        print("Stopping heartbeat thread for server: ", server_name)
                        await session.close()
                        return
                    print(f"Server {server_name} is down!")
                    print(f"Spawning a new server: {server_name}!")
                    #remove server from
                    num_rem, servers_rem, error = lb.remove_servers(1, [server_name])
                    print(f"Removed {num_rem} servers: {servers_rem}")
                    
                    # reinstantiate an image of the server
                    num_add, servers_add, error = lb.add_servers(1, [server_name])
                    print(f"Added {num_add} servers: {servers_add}")
                    
                    # await session.close()
                    # print("Closing session!")
                    
                    # break

            print("Closing session and sleeping!")
            await session.close()
            await asyncio.sleep(0.2)

# async def check_heartbeat(Lb, server_name, server_ip="127.0.0.1", server_port=5000):
#     print("Heartbeat thread started for server: ", server_name)
    
#     cntr = 0
#     while True:
#         # print("Starting a session!")
#         async with aiohttp.ClientSession() as session:
#             print("Session started!")
            
#             try:
#                 async with session.get(f'http://{server_ip}:{server_port}/heartbeat') as response:
#                     # print("Connected to server, Response received!")
#                     # if response.status != 200 and {await response.text()}['message'] != "ok":
                    
#                     ## To-Do: Check for timeout also
                    
#                     if response.status != 200 and response.status != 400:
#                         cntr += 1
#                         if cntr >= 2:
#                             print(f"Server {server_name} is down!")
#                             print(f"Spawning a new server: {server_name}!")
#                             cntr = 0
                            
#                             #remove server from
#                             Lb.remove_servers(1, [server_name])
                            
#                             # reinstantiate an image of the server
#                             Lb.add_servers(1, [server_name])
                            
#                             # print("Closing session!")
#                             # await session.close()
                            
#                             # break
#                     else :
#                         cntr = 0       

#             # except aiohttp.client_exceptions.ClientConnectorError as e:
#             except Exception as e: # this is better as it is more generic and will catch all exceptions
#                 print(f"Could not connect to server {server_name} due to {str(e.__class__.__name__)}")
#                 cntr = 0 
                
#                 print(f"Server {server_name} is down!")
#                 print(f"Spawning a new server: {server_name}!")
#                 #remove server from
#                 num_rem, servers_rem, error = Lb.remove_servers(1, [server_name])
#                 print(f"Removed {num_rem} servers: {servers_rem}")
                
#                 # reinstantiate an image of the server
#                 num_add, servers_add, error = Lb.add_servers(1, [server_name])
#                 print(f"Added {num_add} servers: {servers_add}")
                
#                 # await session.close()
#                 # print("Closing session!")
                
#                 # break
        
#         print("Closing session and sleeping!") 
#         await session.close()              
                        
#         await asyncio.sleep(0.2)

#     return
    

        
    
    