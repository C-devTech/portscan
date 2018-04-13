#!python3
# This program demonstrates the use of sockets in python by scanning ports.

import logging
import socket
import threading
from queue import Queue

# Scan a single an computer for a single of ports.
def portscan(target, port):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Create new socket for each port tested.
        s.settimeout(0.5)                                       # Don't spend too long waiting for a connection.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse a local socket in TIME_WAIT state.
        s.connect((target, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        if s is not None:
            s.close()

# Worker for multi-threaded port scan
def worker(print_lock, q):
    while True:
        (target, port) = q.get()              # Block until an item is available.
        if target is None or port is None:
            break
        if portscan(target, port):
            with print_lock:
                print("\tPort", port, "is open!")
        q.task_done()               # If a join() is currently blocking, will resume when all items have been processed.

# Multi-threaded scan of a single computer for a range of ports.
def scanports(target, start_port, end_port):
    q = Queue()                             # Thread safe queue dependent on threading module.
    print_lock = threading.Lock()

    # Create and start the worker thread objects.
    worker_threads = []                     # A list of all the Thread objects
    for i in range(100):                    # Number of worker threads.
        worker_thread = threading.Thread(target=worker, args=(print_lock, q))
        worker_thread.daemon = True         # Will die if/when the main thread dies.
        worker_threads.append(worker_thread)
        worker_thread.start()

    print("Scanning <%s>..." % target)
    logging.debug("")
    for port in range (start_port, end_port):       # Create the activity queue
        q.put((target, port))
    q.join()                                # Blocks until all items in the queue have been gotten and processed.

    # Stop worker threads
    for i in range(len(worker_threads)):
        q.put((None, None))
    for worker_thread in worker_threads:
        worker_thread.join()
    logging.debug("Finished.")

# Multi-threaded scan of entire subnet which is passed in as '192.168.1.' for a range of ports.
def subnet_scanports(subnet, start_port, end_port):
    q = Queue()                             # Thread safe queue dependent on threading module.
    print_lock = threading.Lock()

    # Create and start the worker thread objects.
    worker_threads = []                     # A list of all the Thread objects
    for i in range(500):                    # Number of worker threads.
        worker_thread = threading.Thread(target=worker, args=(print_lock, q))
        worker_threads.append(worker_thread)
        worker_thread.start()

    for x in range(1, 255):
        target = subnet + str(x)
        print("Scanning <%s>..." % target)
        logging.debug("")
        for port in range(start_port, end_port):    # Create the activity queue
            q.put((target, port))
        q.join()                            # Blocks until all items in the queue have been gotten and processed.

    # Stop worker threads
    for i in range(len(worker_threads)):
        q.put((None, None))
    for worker_thread in worker_threads:
        worker_thread.join()
    logging.debug("Finished.")

# Uncomment for testing speed of scan
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Examples of using scans
# subnet_scanports('192.168.1.', 1, 65556)
# scanports('127.0.0.1', 1, 1000)
scanports('pythonprogramming.net', 1, 65556)


