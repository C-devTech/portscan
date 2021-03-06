#!python3
# This program demonstrates the use of sockets in python by scanning ports.

import json
import logging
import socket
import sys
import threading
from queue import Queue

def loadPortsFile():
    try:
        with open("ports.json") as settings_file:
            ports = json.load(settings_file)
            return ports
    except:
        print('Error: ', sys.exc_info()[0], ' - ', sys.exc_info()[1])
        return None


# Scan a single an computer for a single of ports.
def portscan(target, port_no):
    s = None
    try:
        # Create new socket for each port tested.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Don't spend too long waiting for a connection.
        s.settimeout(0.5)
        # Reuse a local socket in TIME_WAIT state.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((target, port_no))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        if s is not None:
            s.close()

# Worker for multi-threaded port scan
def worker(print_lock, ports, q):
    while True:
        # Block until an item is available.
        (target, port_no) = q.get()
        if target is None or port_no is None:
            break
        if portscan(target, port_no):
            port_str = str(port_no)
            try:
                if str(port_str) in ports.keys():
                    port = ports[port_str]
                    if type(port) is dict:
                        if port['tcp'] == True:
                            description = '{'+port['description']+'}'
                    elif type(port) is list:
                        description = ''
                        for dic in port:
                            if dic['tcp'] == True:
                                description += '{'+dic['description']+'} or '
                        if len(description) > 3:
                            description = description[:-3]
                    else:
                        description = '{Unknown}'
                else:
                    description  = '{Unknown}'
                with print_lock:
                    print('   Port %s is open! \t\t%s' % (port_no, description))
            except:
                pass
        # If a join() is currently blocking, will resume when all
        # items have been processed.
        q.task_done()

# Multi-threaded scan of a single computer for a range of ports.
def scanports(target, start_port, end_port):
    # Thread safe queue dependent on threading module.
    q = Queue()
    print_lock = threading.Lock()
    # Load ports file
    ports_list = loadPortsFile()

    # Create and start the worker thread objects.
    worker_threads = []                 # A list of all the Thread objects
    for i in range(100):                # Number of worker threads.
        worker_thread = threading.Thread(target=worker, \
                args=(print_lock, ports_list['ports'], q))
        worker_thread.daemon = True     # Will die if/when main thread dies.
        worker_threads.append(worker_thread)
        worker_thread.start()

    print("Scanning <%s>..." % target)
    logging.debug("")
    for port in range (start_port, end_port):    # Create the activity queue
        q.put((target, port))
    # Blocks until all items in the queue have been gotten and processed.
    q.join()

    # Stop worker threads
    for i in range(len(worker_threads)):
        q.put((None, None))
    for worker_thread in worker_threads:
        worker_thread.join()
    logging.debug("Finished.")

# Multi-threaded scan of entire subnet which is passed in as '192.168.1.'
# for a range of ports.
def subnet_scanports(subnet, start_port, end_port):
    # Thread safe queue dependent on threading module.
    q = Queue()
    print_lock = threading.Lock()
    # Load ports file
    ports_list = loadPortsFile()

    # Create and start the worker thread objects.
    worker_threads = []                     # A list of all the Thread objects
    for i in range(500):                    # Number of worker threads.
        worker_thread = threading.Thread(target=worker, \
                args=(print_lock, ports_list['ports'], q))
        worker_threads.append(worker_thread)
        worker_thread.start()

    for x in range(1, 255):
        target = subnet + str(x)
        print("Scanning <%s>..." % target)
        logging.debug("")
        for port in range(start_port, end_port):   # Create the activity queue
            q.put((target, port))
        # Blocks until all items in the queue have been gotten and processed.
        q.join()

    # Stop worker threads
    for i in range(len(worker_threads)):
        q.put((None, None))
    for worker_thread in worker_threads:
        worker_thread.join()
    logging.debug("Finished.")

# Uncomment for testing speed of scan
# logging.basicConfig(level=logging.DEBUG, \
#                    format='%(asctime)s - %(levelname)s - %(message)s')

# Examples of using scans
subnet_scanports('192.168.1.', 1, 65556)
# scanports('127.0.0.1', 1, 1000)
# scanports('pythonprogramming.net', 1, 65556)




