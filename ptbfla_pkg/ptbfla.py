#
#  Python Test Bed for Federated Learning Algorithms based on Python Multiprocessing package
#
import sys
import time
from multiprocessing import Process, Queue
from . mpapi import *

class PtbFla:
    # Constructor
    def __init__(self, noNodes, nodeId, flSrvId=0):
        self.noNodes = noNodes
        self.nodeId = nodeId
        self.flSrvId = flSrvId
        
        # Creat list of all ports - TODO: add to self.
        allPorts = [6000+k for k in range(noNodes)]
        
        # Set ports
        self.localPort =   allPorts[nodeId]
        remotePorts = [x for x in allPorts if x != self.localPort]
        
        # Set the local server's address
        self.localServerAddress = ('localhost', self.localPort)
        
        # Set the lst of the addresses of the peer node's servers
        self.remoteServerAddresses = [('localhost', port) for port in remotePorts]
        
        # Algorithm for Centralized FL
        # Set FL server address
        self.flSrvAddress = ('localhost', allPorts[flSrvId])
        
        # Create queue for messages from the local server
        self.queue = Queue()
        
        # Create and start server process
        self.server = Process(target=server_fun, args=(self.localPort,self.queue))
        self.server.start()
        
        # Manual start-up
        #pkey = input('press any key to continue...')
        
        # Automatic system start-up:
        #   - assumption 1: node 0 starts first;
        #   - assumption 2: for nodes not 0, remoteServerAddresses[0] is the remote addres of node 0;
        #   - node 0 waits for hello from all other nodes and then says hello to all other nodes;
        #   - all other nodes say hello to node 0 and wait for hello from node 0;
        #   - this algorithm will not work only if node 0 does not start first;
        print('system is comming up...')
        if self.nodeId == 0:
            rcvMsgs(self.queue, self.noNodes-1)
            broadcastMsg(self.remoteServerAddresses, 'Hello')
        else:
            # Give some time to the node 0 to be the first one to start
            time.sleep(1)
            sendMsg(self.remoteServerAddresses[0], 'Hello')
            rcvMsg(self.queue)
        print('system is up and running')
    
    # Destructor
    def __del__(self):
        # Send 'exit' to local server
        print('node is shutting down...')
        sendMsg(('localhost', self.localPort), 'exit')
        self.server.join()
        
        # Delete queue and server
        del self.queue
        del self.server
    
    def fl_centralized(self, fl_cent_server_processing, fl_cent_client_processing, localData, privateData, noIterations=1):
        # Save initial localData and privateData
        self.localData = localData
        self.privateData = privateData
        
        for k in range(noIterations):
            if self.nodeId == self.flSrvId:
                # Server
                broadcastMsg(self.remoteServerAddresses, self.localData)
                msgs = rcvMsgs(self.queue, self.noNodes-1)
                print('server received:', msgs)
                self.localData = fl_cent_server_processing(self.privateData, msgs)
                print('new server localData=', self.localData)
            
            else:
                # Client
                msg = rcvMsg(self.queue)
                print('client received:', msg)
                self.localData = fl_cent_client_processing(self.localData, self.privateData, msg)
                sendMsg(self.flSrvAddress, self.localData)
        
        # Return the final localData
        return self.localData
    
    def fl_decentralized(self, fl_decent_server_processing, fl_decent_client_processing, localData, privateData, noIterations=1):
        # Save initial localData and privateData
        self.localData = localData
        self.privateData = privateData
        
        # The nodes within this function exchange messages, which are lists with 3 elements: msgSeqNo, msgSrcAdr, and msgData.
        # The indices of these message elements are the following:
        msgSeqNo = 0
        msgSrcAdr = 1
        msgData = 2
        
        # Set the number of neighbors
        noNeighbors = len(self.remoteServerAddresses)
        
        for k in range(noIterations):
            # This node is initially acting as a server
            broadcastMsg(self.remoteServerAddresses, [1, self.localServerAddress, self.localData])
            noRcvdMsgs = 0
            dataFromClients = []
            while noRcvdMsgs != 2*noNeighbors:
                msg = rcvMsg(self.queue)
                noRcvdMsgs = noRcvdMsgs + 1
                if msg[msgSeqNo] == 1:
                    # The 1st msg from a neighbor acting as a server
                    # This node takes the role of a client
                    print('as a client received:', msg)
                    tmpLocalData = fl_decent_client_processing(self.localData, self.privateData, msg[msgData])
                    # JSON converts tuples to lists, so msg[msgSrcAdr] must be converted back to a tuple(msg[msgSrcAdr])
                    sendMsg(tuple(msg[msgSrcAdr]), [2, self.localServerAddress, tmpLocalData])
                else:
                    # The 2nd msg from a neighbor acting as client
                    # This node takes the role of a server
                    dataFromClients.append(msg[msgData])
            # All 2*noNeighbors messages have been processed
            # This node takes the final role of a server
            print('as server received:', dataFromClients)
            self.localData = fl_decent_server_processing(self.privateData, dataFromClients)
            print('new server localData=', self.localData)
        
        # Return the final localData
        return self.localData


