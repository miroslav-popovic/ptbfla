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
        self.localPort = allPorts[nodeId]
        
        # Set the local server's address
        self.localServerAddress = ('localhost', self.localPort)
        
        # Set the lst of the addresses of all node's servers
        self.allServerAddresses = [('localhost', port) for port in allPorts]
        
        # Create and start server process
        self.server = Process(target=server_fun, args=(self.localPort, queue))
        self.server.start()
        
        # Manual start-up
        #pkey = input('press any key to continue...')
        
        # Automatic system start-up:
        #   - assumption 1: node 0 starts first;
        #   - assumption 2: for nodes not 0, allServerAddresses[0] is the remote address of node 0;
        #   - node 0 waits for hello from all other nodes and then says hello to all other nodes;
        #   - all other nodes say hello to node 0 and wait for hello from node 0;
        #   - this algorithm will not work only if node 0 does not start first;
        print('system is comming up...')
        if self.nodeId == 0:
            rcvMsgs(self.noNodes-1)
            broadcastMsg(self.allServerAddresses, 'Hello', self.nodeId)
        else:
            # Give some time to the node 0 to be the first one to start
            time.sleep(1)
            sendMsg(self.allServerAddresses[0], 'Hello')
            rcvMsg()
        print('system is up and running')
    
    # Destructor
    def __del__(self):
        # Send 'exit' to local server
        print('node is shutting down...')
        sendMsg(self.localServerAddress, 'exit')
        self.server.join()
        
        # Delete server
        del self.server
    
    def fl_centralized(self, fl_cent_server_processing, fl_cent_client_processing, localData, privateData, noIterations=1):
        # Save initial localData and privateData
        self.localData = localData
        self.privateData = privateData
        
        for k in range(noIterations):
            if self.nodeId == self.flSrvId:
                # Server
                broadcastMsg(self.allServerAddresses, self.localData self.nodeId)
                msgs = rcvMsgs(self.noNodes-1)
                print('server received:', msgs)
                self.localData = fl_cent_server_processing(self.privateData, msgs)
                print('new server localData=', self.localData)
            
            else:
                # Client
                msg = rcvMsg()
                print('client received:', msg)
                self.localData = fl_cent_client_processing(self.localData, self.privateData, msg)
                sendMsg(self.allServerAddresses[flSrvId], self.localData)
        
        # Return the final localData
        return self.localData
    
    def fl_decentralized(self, fl_decent_server_processing, fl_decent_client_processing, localData, privateData, noIterations=1):
        # Save initial localData and privateData
        self.localData = localData
        self.privateData = privateData
        
        #   The nodes within this function exchange messages, which are lists with 4 elements:
        #       msgIterNo, msgSeqNo, msgSrcAdr, and msgData.
        #   The indices of these message elements are the following:
        msgIterNo = 0
        msgSeqNo = 1
        msgSrcAdr = 2
        msgData = 3
        #   The msgSeqNo mssage field can have two values for the phases 1 and 2 respectively:
        PHASE1 = 1
        PHASE2 = 2
        
        # Set the number of neighbors
        noNeighbors = noNodes - 1
        dataFromClients1 = []
        
        for iterNo in range(noIterations):
            # This node is initially acting as a server - phase 1
            broadcastMsg(self.allServerAddresses, [iterNo, PHASE1, self.localServerAddress, self.localData], self.nodeId)
            
            # This node now acts as a client - phase 2
            noRcvdMsgs = 0
            dataFromClients2 = []
            
            # First drain the buffer dataFromClients1
            assert len(dataFromClients1) <= noNeighbors
            while len(dataFromClients1) > 0:
                msg = dataFromClients1.pop(0)
                print('as a client, received from the buffer dataFromClients1:', msg)
                assert (msg[msgIterNo] == iterNo) and (msg[msgSeqNo] == PHASE1)
                noRcvdMsgs = noRcvdMsgs + 1
                tmpLocalData = fl_decent_client_processing(self.localData, self.privateData, msg[msgData])
                sendMsg(tuple(msg[msgSrcAdr]), [iterNo, PHASE2, self.localServerAddress, tmpLocalData])
            
            # Process the rest of the messages coming from the local server queue (see module mpapi.py)
            while noRcvdMsgs != 2*noNeighbors:
                msg = rcvMsg()
                
                # Is it a message from a client that already entered the treration iterNo+1? If yes, store it for the next itertion.
                if msg[msgIterNo] != iterNo:
                    assert (msg[msgIterNo] == iterNo+1) and (msg[msgSeqNo] == PHASE1)
                    print('as a client, received the message from a node that already entered the next iteration:', msg)
                    dataFromClients1.append(msg)
                    continue
                
                noRcvdMsgs = noRcvdMsgs + 1
                if msg[msgSeqNo] == PHASE1:
                    # The 1st msg from a neighbor acting as a server
                    # This node takes the role of a client
                    print('as a client received:', msg)
                    tmpLocalData = fl_decent_client_processing(self.localData, self.privateData, msg[msgData])
                    # JSON converts tuples to lists, so msg[msgSrcAdr] must be converted back to a tuple(msg[msgSrcAdr])
                    sendMsg(tuple(msg[msgSrcAdr]), [iterNo, PHASE2, self.localServerAddress, tmpLocalData])
                else:
                    # The 2nd msg from a neighbor acting as client
                    # This node takes the role of a server
                    dataFromClients2.append(msg[msgData])
            
            # All 2*noNeighbors messages have been processed
            # This node takes the final role of a server - phase 3
            print('as server received:', dataFromClients2)
            self.localData = fl_decent_server_processing(self.privateData, dataFromClients2)
            print('new server localData=', self.localData)
        
        # Return the final localData
        return self.localData
