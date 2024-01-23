import sys
from multiprocessing import Process, Queue
from multiprocessing.connection import Client, Listener
from array import array
import json


queue = Queue()

def server_fun(localPort):
    # Set the address of the local node's server
    localServerAddress = ('localhost', localPort)
    
    # Send fixed message
    with Listener(localServerAddress, authkey=b'Lets work together') as listener:
        
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
    try:
        with Client(remoteServerAddress, authkey=b'Lets work together') as conn:
            bmsg = json.dumps(msg).encode('utf-8')
            conn.send(bmsg)
    except ConnectionRefusedError:
        print('Modlule msg_passing_api, Function sendMsg: ConnectionRefusedError occured - sendMsg will exit...')
        exit()

def rcvMsg():
    return queue.get()

def broadcastMsg(listOfServerAddress, msg, senderId=-1):
    return broadcastMsgHelper(listOfServerAddress, 0, len(listOfServerAddress), msg, senderId)

def broadcastMsgHelper(listOfServerAddress, i, noNodes, msg, senderId):
    if i != senderId:
        sendMsg(listOfServerAddress[i], msg)
    if i < noNodes-1:
        broadcastMsgHelper(listOfServerAddress, i+1, noNodes, msg, senderId)

def broadcastMsgFor(listOfServerAddress, msg, senderId=-1):
    for i in range(len(listOfServerAddress)):
        if i != senderId:
            sendMsg(listOfServerAddress[i], msg)

def rcvMsgs(noOfMessagesToReceive):
    return rcvMsgsHelper(i, noOfMessagesToReceive, [])

def rcvMsgsHelper(i, noOfMessagesToReceive, msgs):
    if i < noOfMessagesToReceive:
        return rcvMsgsHelper(i+1, noOfMessagesToReceive, msgs.append(rcvMsg()))
    return msgs

def rcvMsgsFor(noOfMessagesToReceive):
    msgs = []
    for i in range(noOfMessagesToReceive):
        msgs.append(rcvMsg())
    return msgs
