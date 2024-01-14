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
from utils import generate_new_hostname

class LoadBalancer:
    def __init__(self, port):
        self.port = port
        self.servers = {} # dictionary of active servers (key: hostname, value: port)
        self.rw_lock = RWLock()  # reader-writer lock to protect the self.servers dictionary
        self.socket = None

    def add_servers(self, num_add, hostnames:list):
        error=""
        temp_new_servers = {}
        if (hostnames.len() > num_add):
            print("<Error> Length of hostname list is more than newly added instances")
            error = "<Error> Length of hostname list is more than newly added instances"
            return -1, [], error
            
        else:
            # add the servers whose hostnames are provided to the list
            for hostname in hostnames:
                self.rw_lock.acquire_reader()
                if (hostname in self.servers):
                    print("<Error> Hostname: '" + hostname + "' already exists in the active list of servers!") 
                else:
                    temp_new_servers[hostname] = 1
                self.rw_lock.release_reader()
            
            # add the remaining servers to the list by generating new random hostnames for them
            for i in range(num_add - hostnames.len()):
                new_hostname = generate_new_hostname()
                self.rw_lock.acquire_reader()
                while (new_hostname in self.servers or new_hostname in temp_new_servers):
                    new_hostname = generate_new_hostname()
                self.rw_lock.release_reader()
                temp_new_servers[new_hostname] = 1
          
        # send the temorary list of new servers to be added to the consistent hashing module
        # the consistent hasing module will finally return the list of servers that were finally added
        num_added, new_servers = self.consistent_hashing.add_servers([server for server in temp_new_servers])
              
        # # add the newly added servers to the dictionary of servers
        self.rw_lock.acquire_writer()
        for server in new_servers:
            self.servers[server] = 1 # value kept as 1 for now, will be changed to port no later when server is set up
        self.rw_lock.release_writer()
        
        return num_added, new_servers, error
    
    def remove_servers(self, num_rem, hostnames:list):
        error = ""
        self.rw_lock.acquire_reader()
        if (len(self.servers) == 0):
            print("<Error> No servers to remove!")
            self.rw_lock.release_reader()
            error = "<Error> No servers to remove!"
            return -1, [], error
        self.rw_lock.release_reader()
        
        temp_rm_servers = {}
        if (hostnames.len() > num_rem):
            print("<Error> Length of hostname list is more than removable instances")
            error = "<Error> Length of hostname list is more than removable instances"
            return -1, [], error
        else:
            for hostname in hostnames:
                self.rw_lock.acquire_reader()
                if (hostname not in self.servers):
                    print("<Error> Hostname: '" + hostname + "' does not exist in the active list of servers!")    
                else:
                    temp_rm_servers[hostname] = 1
                self.rw_lock.release_reader()
                    
            # remove remaining servers from the list by randomly selecting them from the list of active servers
            for i in range(num_rem - hostnames.len()):
                self.rw_lock.acquire_reader()
                if (len(self.servers) == 0):
                    print("<Error> No active server left. Can't remove any more servers!")
                    # error = "<Error> No active server left. Can't remove any more servers!"
                    self.rw_lock.release_reader()
                    break
                self.rw_lock.release_reader()
                    
                self.rw_lock.acquire_reader()
                while(True):
                    rm_hostname = random.choice(list(self.servers.keys() - temp_rm_servers.keys()))
                    if (rm_hostname not in temp_rm_servers):
                        temp_rm_servers[rm_hostname] = 1
                        break
                self.rw_lock.release_reader()
            
        # servers_dne is the list of servers that were not found in the list of active servers (dne for does not exist) when trying to remove them
        # this could be because the server got down before it could be removed, and was replaced by a new server of different hostname
        num_rem, servers_dne = self.consistent_hashing.remove_servers([server for server in temp_rm_servers])
        
        # remove the newly removed servers from the dictionary of servers
        self.rw_lock.acquire_writer()
        for server in temp_rm_servers:
            if (server in servers_dne): # this is for the case when server got down before it could be removed
                # assert(server not in self.servers)
                if (server in self.servers): # this should never happen
                    print("<Error> This shoudn't happen! Server should have already been removed!")
                    self.servers.pop(server)
            else:
                self.servers.pop(server)
    
        self.rw_lock.release_writer()
    
    
        # return num_rem, [server for server in [temp_rm_servers - servers_dne]], error
        return len(temp_rm_servers), [server for server in temp_rm_servers], error # can simply keep this to not make it complicated as compared to above return 
    
    def list_active_servers(self):
        
        self.rw_lock.acquire_reader()
        active_servers = [server for server in self.servers]
        self.rw_lock.release_reader()
        
        return len(active_servers), active_servers
        
    def create_new_server(self):
        pass
    
    def probe_servers(self):
        pass
    
    def process_client_request(self, req_type, req_dict={}):
        response_code = 0
        response_dict = {}
        
        ### ADD request type
        if (req_type == "add"):
            num_add, hostnames = req_dict["n"], req_dict["hostnames"]
            num_added, new_servers, error = self.add_servers(num_add, hostnames)
            if (num_added == -1):
                response_code = 400
                response_dict["message"] = error
                response_dict["status"] = "failure"
            
            else:
                response_code = 200
                # message to be shown: final active server list, not just those added
                self.rw_lock.acquire_writer() # given writer priority here to prevent any other writer to add/rm server while this is waiting to read the servers
                response_dict["message"] = {"N": self.servers.len(), "replicas": [server for server in self.servers]}
                self.rw_lock.release_writer()
                response_dict["status"] = "success"
                
                ### need to add additional messages here regarding servers that could not be added (maybe cause already existing)
                response_dict["additional-info"] = "Successfully added " + str(num_added) + " servers!"
          
        ### REMOVE request type      
        elif (req_type == "remove"):
            num_rem, hostnames = req_dict["n"], req_dict["hostnames"]
            num_removed, removed_servers, error = self.remove_servers(num_rem, hostnames)
            if (num_removed == -1):
                response_code = 400
                response_dict["message"] = error
                response_dict["status"] = "failure"
            
            else:
                response_code = 200
                self.rw_lock.acquire_writer() # given writer priority here to prevent any other writer to add/rm server while this is waiting to read the servers
                response_dict["message"] = {"N": self.servers.len(), "replicas": [server for server in self.servers]}
                self.rw_lock.release_writer()
                response_dict["status"] = "success"
                
                ### need to add additional messages here regarding servers that could not be removed (maybe cause name not found)
                response_dict["additional-info"] = "Successfully removed " + str(num_removed) + " servers!"
         
        ### LIST ACTIVE SERVERS request type       
        elif (req_type == "list"):
                response_code = 200
                self.rw_lock.acquire_writer() # given writer priority here to prevent any other writer to add/rm server while this is waiting to read the servers
                response_dict["message"] = {"N": self.servers.len(), "replicas": [server for server in self.servers]}
                self.rw_lock.release_writer()
                response_dict["status"] = "success"
          
        ### PATH request type (not clear what it means)
        elif (req_type == "path"):
            pass
           
        ### INVALID request type     
        else:
            response_code = 400
            response_dict["message"] = "Invalid request type!"
            response_dict["status"] = "failure"
        
        
        return response_code, response_dict
                
               
        
        
                
        
        
