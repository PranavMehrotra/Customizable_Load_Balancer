import bisect
import time
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
        self.hash_array = np.zeros(self.num_slots)
        self.id_to_hostname = {}
        self.hostname_to_id = {}
        self.num_virtual_servers = 0
        self.next_server_id = 1
        self.init_hash_map(server_hostnames)

    
    def init_hash_map(self, server_hostnames: list):
        self.lock.acquire_writer()
        for i in range(self.num_servers):
            self.id_to_hostname[self.next_server_id] = server_hostnames[i]
            self.hostname_to_id[server_hostnames[i]] = self.next_server_id
            for j in range(self.num_replicas):
                replica_hash = self.server_hash_func(self.next_server_id, j)
                replica_hash = self.linear_probing(replica_hash)
                self.hash_map.append(replica_hash)
                self.hash_array[replica_hash] = self.next_server_id
            self.next_server_id += 1
        self.hash_map.sort()
        self.num_virtual_servers = len(self.hash_map)
        self.lock.release_writer()
        # self.__unique_checker()

    def server_hash_func(self, server_id, replica_id):
        hash = (server_id*server_id) % self.num_slots
        hash += (replica_id*replica_id) % self.num_slots
        hash += (2*replica_id + 25) % self.num_slots
        print(f"Server: {server_id}, Replica: {replica_id}, Hash: {hash}")
        return hash % self.num_slots
    
    def request_hash_func(self, request_id):
        hash = (request_id*request_id) % self.num_slots
        hash += (2*request_id + 17) % self.num_slots
        print(f"Request: {request_id}, Hash: {hash}")
        return hash % self.num_slots
    
    def get_server(self, request_id):
        self.lock.acquire_reader()
        server_id = self.hash_array[self.hash_map[bisect.bisect_left(self.hash_map, self.request_hash_func(request_id)) % self.num_virtual_servers]]
        server = self.id_to_hostname[server_id]
        self.lock.release_reader()
        return server
    
    def linear_probing(self, replica_hash):
        i = replica_hash
        if self.hash_array[i] != 0:
            print(f"Collision while adding at hash {replica_hash}, performing linear probing")
        while self.hash_array[i] != 0:
            i = (i+1) % self.num_slots
            if i == replica_hash:
                # Should never happen
                BufferError("No more slots available")
                return
        if i != replica_hash:
            print(f"Linear probing completed at hash {i}")
        return i

    def linear_probing_delete(self, replica_hash, server_id):
        i = replica_hash
        if self.hash_array[i] != server_id:
            print(f"Collision while removing at hash {replica_hash}, performing linear probing")
        while self.hash_array[i] != server_id:
            i = (i+1) % self.num_slots
            if i == replica_hash:
                # Should never happen
                BufferError(f"Replica does not exist of server {server_id}")
                return
        if i != replica_hash:
            print(f"Linear probing completed at hash {i}")
        return i

    def add_server(self, server_hostname):
        if self.num_virtual_servers + self.num_replicas > self.num_slots:
            print("No more servers can be added, all slots are full")
            return
        self.lock.acquire_writer()
        server_id = self.next_server_id
        self.next_server_id += 1
        self.id_to_hostname[server_id] = server_hostname
        self.hostname_to_id[server_hostname] = server_id
        for i in range(self.num_replicas):
            replica_hash = self.server_hash_func(server_id, i)
            replica_hash = self.linear_probing(replica_hash)
            bisect.insort(self.hash_map, replica_hash)
            self.hash_array[replica_hash] = server_id
            self.num_virtual_servers += 1
        self.lock.release_writer()
        # self.__unique_checker()

    def remove_server(self, server_hostname):
        # Check if server exists
        if server_hostname not in self.hostname_to_id:
            print("Server does not exist")
            return
        self.lock.acquire_writer()
        server_id = self.hostname_to_id[server_hostname]
        del self.hostname_to_id[server_hostname]
        del self.id_to_hostname[server_id]
        for i in range(self.num_replicas):
            replica_hash = self.server_hash_func(server_id, i)
            replica_hash = self.linear_probing_delete(replica_hash, server_id)
            self.hash_array[replica_hash] = 0
            idx = bisect.bisect_left(self.hash_map, replica_hash)
            if idx >= len(self.hash_map) or self.hash_map[idx] != replica_hash:
                # Should never happen
                # print(f"Replica {i} of server {server_id} does not exist")
                self.lock.release_writer()
                BufferError(f"Replica {i} of server {server_id} does not exist")
            del self.hash_map[idx]
            self.num_virtual_servers -= 1
        self.lock.release_writer()
        # self.__unique_checker()

    def print_hash_map(self):
        self.lock.acquire_reader()
        print(f"Number of virtual servers: {self.num_virtual_servers}\n Hash map: ", end="")
        print(self.hash_map)
        # print(self.hash_array)
        self.lock.release_reader()

    def __unique_checker(self):
        # Check if sorted list is unique
        print("Checking uniqueness of hash map: ", end="")
        self.lock.acquire_reader()
        for i in range(len(self.hash_map)-1):
            if self.hash_map[i] == self.hash_map[i+1]:
                print("Not unique")
                print(f"Duplicate: {self.hash_map[i]} at index {i} and {i+1}")
                print(self.hash_map)
                self.lock.release_reader()
                exit()
        self.lock.release_reader()
        print("Unique")


if __name__ == "__main__":
    server_hostnames = ["server1", "server2", "server3"]
    consistent_hashing = ConsistentHashing(server_hostnames)
    consistent_hashing.print_hash_map()
    # time.sleep(5)
    consistent_hashing.add_server("server4")
    consistent_hashing.print_hash_map()
    # time.sleep(5)
    consistent_hashing.remove_server("server2")
    consistent_hashing.print_hash_map()
    # time.sleep(5)
    # consistent_hashing.add_server("server5")
    # consistent_hashing.print_hash_map()
    # consistent_hashing.remove_server("server3")
    # consistent_hashing.print_hash_map()
    # consistent_hashing.add_server("server6")
    # consistent_hashing.print_hash_map()
    # consistent_hashing.remove_server("server1")
    # consistent_hashing.print_hash_map()
    print(consistent_hashing.get_server(1))
    print(consistent_hashing.get_server(2))
    print(consistent_hashing.get_server(5))