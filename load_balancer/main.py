import sys
import time
import os
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from consistent_hashing import consistent_hashing
from server import server
from load_balancer import LoadBalancer
from heartbeat import check_heartbeat
import aiohttp
import asyncio


if __name__ == "__main__":
    Lb = LoadBalancer()
    Lb.active_flag = {}
    Lb.active_flag['server1'] = 0
    Lb.active_flag['server2'] = 0
    Lb.active_flag['server3'] = 0
    # Lb.add_servers(2, ['server1', 'server2'])
    t1 = threading.Thread(target=asyncio.run(check_heartbeat(Lb, 'server1')), args=[])
    t1.start()
    t1.join()