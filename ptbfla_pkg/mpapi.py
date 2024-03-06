import sys
import socket
from multiprocessing import Process, Queue
from multiprocessing.connection import Client, Listener
from array import array
import json
import time

def server_fun(localPort, queue):
    # Set the address of the local node's server
    localServerAddress = ('localhost', localPort)
    
    # Send fixed message
    #with Listener(localServerAddress, authkey=b'Lets work together') as listener:
    with Listener(localServerAddress) as listener:    # without authentication
        
        while True:
            with listener.accept() as conn:
                #print('connection accepted from', listener.last_accepted)
                bmsg = conn.recv()
                msg = json.loads(bmsg)
                #print(msg)
                
                # Forward msg to local node's process
                queue.put(msg)
                
                # Exit if msg is 'exit'
                if msg == 'exit':
                    break

def sendMsg(remoteServerAddress, msg):
    MAX_RETRY_COUNT = 100
    counter = 0
    while counter < MAX_RETRY_COUNT:
        try:
            #with Client(remoteServerAddress, authkey=b'Lets work together') as conn:
            with Client(remoteServerAddress) as conn:    # without authentication
                bmsg = json.dumps(msg).encode('utf-8')
                conn.send(bmsg)
                break
        except OSError as e:   # former socket.error exception
            print(f'Modlule msg_passing_api, Function sendMsg: An exectption {e} occured, the operation will be retried...')
            # This was tested with apps with up to 200 nodes, on Dell Latitude 3420 laptop. Be sure to exit all apps and disconnect from Internet.
            time.sleep(0.2) # wait for 200 ms
            counter += 1
    if counter >= MAX_RETRY_COUNT:
        sys.exit()

def rcvMsg(queue):
    return queue.get()

def broadcastMsg(listOfRemoteServerAddress, msg):
    for remoteServerAddress in listOfRemoteServerAddress:
        sendMsg(remoteServerAddress, msg)

def rcvMsgs(queue, noOfMessagesToReceive):
    msgs = []
    
    for i in range(noOfMessagesToReceive):
        msgs.append( rcvMsg(queue) )
    
    return msgs
