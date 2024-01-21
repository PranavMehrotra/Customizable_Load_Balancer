import sys
import socketserver
import http.server
import threading
import sys
import os
import json
import random

# add the path to the parent directory to the sys.path list
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from consistent_hashing.RWLock import RWLock
from consistent_hashing import consistent_hashing
from utils import generate_new_hostname
from docker_utils import spawn_server_cntnr, kill_server_cntnr

class LoadBalancer:
    def __init__(self, port=None):
        
        self.port = port
        self.servers = {} # dictionary of active servers (key: hostname, value: port)
        self.rw_lock = RWLock()  # reader-writer lock to protect the self.servers dictionary
        self.socket = None
        
        # spawn the initial set of servers
        for hostname in ['server1', 'server2', 'server3']:
            port = spawn_server_cntnr(hostname)
            if (port == -1):
                print("<Error> Server: '" + hostname + "' could not be spawned!")
                return
            self.rw_lock.acquire_writer()
            self.servers[hostname] = port
            self.rw_lock.release_writer()
        
        self.consistent_hashing = consistent_hashing.ConsistentHashing(server_hostnames=['server1', 'server2', 'server3'])

    def add_servers(self, num_add, hostnames:list):
        error=""
        temp_new_servers = set()
        # Make hostnames list unique(basically a set)
        hostnames = set(hostnames)
        if (len(hostnames) > num_add):
            print("<Error> Length of hostname list is more than newly added instances")
            error = "<Error> Length of hostname list is more than newly added instances"
            return -1, [], error
            
        else:
            # add the servers whose hostnames are provided, to the set
            for hostname in hostnames:
                self.rw_lock.acquire_reader()
                if (hostname in self.servers):
                    print("<Error> Hostname: '" + hostname + "' already exists in the active list of servers!") 
                    self.rw_lock.release_reader()
                    continue
                self.rw_lock.release_reader()
                temp_new_servers.add(hostname)
            
            # add the remaining servers to the list by generating new random hostnames for them
            for i in range(num_add - len(temp_new_servers)):
                new_hostname = generate_new_hostname()
                self.rw_lock.acquire_reader()
                while (new_hostname in self.servers or new_hostname in temp_new_servers):
                    new_hostname = generate_new_hostname()
                self.rw_lock.release_reader()
                temp_new_servers.add(new_hostname)
        
        final_add_server_dict = {}        
        
        ### TO-D0: Call the server spawning module to spawn the new servers:
        for server in temp_new_servers:
            print("Spawning server: " + server)
            port = spawn_server_cntnr(server) ## function from docker_utils.py
            ### TO-DO: Add error handling here in case the server could not be spawned
            if (port == -1):
                print("<Error> Server: '" + server + "' could not be spawned!")

            else:     # add the newly spawned server to the dictionary of servers
                final_add_server_dict[server] = port
            
        
          
        # send the temorary list of new servers to be added to the consistent hashing module
        # the consistent hasing module will finally return the list of servers that were finally added
        new_servers = self.consistent_hashing.add_servers([server for server in final_add_server_dict.keys()])
        

        # # add the newly added servers to the dictionary of servers
        self.rw_lock.acquire_writer()
        for server in new_servers:
            self.servers[server] = final_add_server_dict[server] # port number
        self.rw_lock.release_writer()
        
        ### TO-DO: For the servers that couldn't be added to the CH module (possibly due to lack of space), remove them from the list of servers to be added
        ### Also, close the docker containers and corresponding threads  
        for server in final_add_server_dict.keys() - new_servers:
            kill_server_cntnr(server)
            
        # final_add_server_dict = {server: final_add_server_dict[server] for server in new_servers}
        
        return len(new_servers), new_servers, error
    
    def remove_servers(self, num_rem, hostnames:list):
        error = ""
        self.rw_lock.acquire_reader()
        if (len(self.servers) == 0):
            print("<Error> No servers to remove!")
            self.rw_lock.release_reader()
            error = "<Error> No servers to remove!"
            return -1, [], error
        if (num_rem > len(self.servers)):
            print("<Error> Number of servers to remove is more than the number of active servers!")
            self.rw_lock.release_reader()
            error = "<Error> Number of servers to remove is more than the number of active servers!"
            return -1, [], error
        self.rw_lock.release_reader()
        
        temp_rm_servers = set()  # Use set instead of dictionary for faster additions and subtractions
        # Make hostname list unique(basically a set)
        hostnames = set(hostnames)
        if (len(hostnames) > num_rem):
            print("<Error> Length of hostname list is more than removable instances")
            error = "<Error> Length of hostname list is more than removable instances"
            return -1, [], error
        else:
            for hostname in hostnames:
                self.rw_lock.acquire_reader()
                if (hostname not in self.servers):
                    print("<Error> Hostname: '" + hostname + "' does not exist in the active list of servers!")    
                else:
                    # temp_rm_servers[hostname] = 1
                    temp_rm_servers.add(hostname)          ## FASTER
                self.rw_lock.release_reader()
                    
            ## VERY SLOW:
            # remove remaining servers from the list by randomly selecting them from the list of active servers
            # for i in range(num_rem - len(hostnames)):
            #     self.rw_lock.acquire_reader()
            #     if (len(self.servers) == 0):
            #         print("<Error> No active server left. Can't remove any more servers!")
            #         # error = "<Error> No active server left. Can't remove any more servers!"
            #         self.rw_lock.release_reader()
            #         break
            #     while(True):
            #         rm_hostname = random.choice(list(self.servers.keys() - temp_rm_servers.keys()))
            #         if (rm_hostname not in temp_rm_servers):
            #             temp_rm_servers[rm_hostname] = 1
            #             break
            #     self.rw_lock.release_reader()
            
            ## FASTER: (No need for random selection)
            if num_rem > len(temp_rm_servers):
                self.rw_lock.acquire_reader()
                if num_rem == len(self.servers):
                    # Extend the list of servers to be removed with all the remaining servers
                    temp_rm_servers = set(self.servers.keys())
                else:
                    left = num_rem - len(temp_rm_servers)
                    tem_set = set(self.servers.keys()) - temp_rm_servers
                    # Extend the list of servers to be removed with randomly selected servers
                    temp_rm_servers = temp_rm_servers.union(random.sample(tem_set, left))  # This random.sample can also be removed, just take the first 'left' no. of servers :)
                self.rw_lock.release_reader()
                
            
       # servers_rem_f is the list of servers that were finally removed from CH module
        servers_rem_f = self.consistent_hashing.remove_servers([server for server in temp_rm_servers])
        
        # remove the newly removed servers from the dictionary of servers
        # self.rw_lock.acquire_writer()
        # for server in temp_rm_servers:
        #     if (server in servers_dne): # this is for the case when server got down before it could be removed
        #         # assert(server not in self.servers)
        #         if (server in self.servers): # this should never happen
        #             print("<Error> This shoudn't happen! Server should have already been removed!")
        #             self.servers.pop(server)
        #     else:
        #         self.servers.pop(server)
    
        # self.rw_lock.release_writer()
        
        # remove the final list of servers from the dictionary of servers
        self.rw_lock.acquire_writer()
        for server in servers_rem_f:
            self.servers.pop(server)
            # print("Server: " + server + " removed!")
        self.rw_lock.release_writer()
        
        # close the docker containers and corresponding threads for the servers that were finally removed
        for server in servers_rem_f:
            kill_server_cntnr(server)
        
        return len(servers_rem_f), servers_rem_f, error 
                
               
        
        
                
        
        
