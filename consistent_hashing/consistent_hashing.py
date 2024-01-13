import os
import sys
import threading
import bisect
import numpy as np

from RWLock import RWLock

class ConsistentHashing:
    def __init__(self, server_hostnames: list, num_servers=3, num_replicas=9, num_slots=512):
        if len(server_hostnames) < num_servers:
            print("Number of servers is greater than number of server hostnames provided")
            return
        self.num_servers = num_servers
        self.num_replicas = num_replicas
        self.num_slots = num_slots
        self.lock = RWLock()
        self.hash_map = []
        self.id_to_hostname = {}
        self.num_virtual_servers = 0
        self.next_server_id = 0
        self.init_hash_map(server_hostnames)

    
    def init_hash_map(self, server_hostnames: list):
        self.lock.acquire_writer()
        self.hash_map = []
        for i in range(self.num_servers):
            self.id_to_hostname[i] = server_hostnames[i]
            for j in range(self.num_replicas):
                self.hash_map.append((self.server_hash_func(i, j), i))
        self.hash_map.sort(key=lambda x: x[0])
        self.num_virtual_servers = len(self.hash_map)
        self.next_server_id = self.num_servers
        self.lock.release_writer()

    def server_hash_func(self, server_id, replica_id):
        hash = (server_id*server_id) % self.num_slots
        hash += (replica_id*replica_id) % self.num_slots
        hash += (2*replica_id + 25) % self.num_slots
        return hash % self.num_slots
    
    def request_hash_func(self, request_id):
        hash = (request_id*request_id) % self.num_slots
        hash += (2*request_id + 17) % self.num_slots
        return hash % self.num_slots
    
    def get_server(self, request_id):
        self.lock.acquire_reader()
        server_id = self.hash_map[bisect.bisect_left(self.hash_map, (self.request_hash_func(request_id),))][1]
        self.lock.release_reader()
        return self.id_to_hostname[server_id]
    
    def linear_probing(self, idx):
        assert self.hash_map[(idx+1)%self.num_virtual_servers][0] != self.hash_map[idx][0]
        while self.hash_map[(idx+1)%self.num_virtual_servers][0] == self.hash_map[idx][0] + 1:
            idx = (idx+1)%self.num_virtual_servers
        return idx+1


    def add_server(self, server_hostname):
        if self.num_virtual_servers + self.num_replicas > self.num_slots:
            print("No more servers can be added, all slots are full")
            return
        self.lock.acquire_writer()
        server_id = self.next_server_id
        self.next_server_id += 1
        self.id_to_hostname[server_id] = server_hostname
        for i in range(self.num_replicas):
            replica_hash = self.server_hash_func(server_id, i)
            temp_idx = bisect.bisect_left(self.hash_map, (replica_hash,))
            if self.hash_map[temp_idx][0] == replica_hash:
                temp_idx = self.linear_probing(temp_idx)
            if temp_idx == self.num_virtual_servers:
                self.hash_map.append((replica_hash, server_id))
            else:
                self.hash_map.insert(temp_idx, (replica_hash, server_id))
            self.num_virtual_servers += 1
        self.lock.release_writer()
