#
#  Python Test Bed for Federated Learning Algorithms based on Python Multiprocessing package
#
import sys
import time
from multiprocessing import Process, Queue
from .mpapi import *


MSG_ITER_NO = "msgIterNo"
MSG_SEQ_NO = "msgSeqNo"
MSG_SRC_ADR = "msgSrcAdr"
MSG_DATA = "msgData"
MSG_REMOTE_FLAG = "remote"


class PtbFla:
    # Constructor

    def __init__(self, noNodes, nodeId, flSrvId=0):
        self.noNodes = noNodes
        self.nodeId = nodeId
        self.flSrvId = flSrvId

        # Creat list of all ports - TODO: add to self.
        allPorts = [6000 + k for k in range(noNodes)]
        self.allServerAddresses = [("localhost", port) for port in allPorts]

        # Set ports
        self.localPort = allPorts[nodeId]
        remotePorts = [x for x in allPorts if x != self.localPort]

        # Set the local server's address
        self.localServerAddress = ("localhost", self.localPort)

        # Set the lst of the addresses of the peer node's servers
        self.remoteServerAddresses = [("localhost", port) for port in remotePorts]

        # Algorithm for Centralized FL
        # Set FL server address
        self.flSrvAddress = ("localhost", allPorts[flSrvId])

        # Set the initial timeSlot for the function get1Meas
        self.timeSlot = 0

        # Create the time slot queue (in form of a map) to be used by the function getMeas
        # timeSlotsMap is a dictoinary whose key is a timeSlot and the value is the peer's msg
        self.timeSlotsMap = {}

        # Create queue for messages from the local server
        self.queue = Queue()

        # Create and start server process
        self.server = Process(target=server_fun, args=(self.localPort, self.queue))
        self.server.start()

        # Manual start-up
        # pkey = input('press any key to continue...')

        # Automatic system start-up:
        #   - assumption 1: node 0 starts first;
        #   - assumption 2: for nodes not 0, remoteServerAddresses[0] is the remote addres of node 0;
        #   - node 0 waits for hello from all other nodes and then says hello to all other nodes;
        #   - all other nodes say hello to node 0 and wait for hello from node 0;
        #   - this algorithm will not work only if node 0 does not start first;
        print("system is comming up...")
        if self.nodeId == 0:

            rcvMsgs(self.queue, self.noNodes - 1)

            broadcastMsg(
                self.remoteServerAddresses,
                {
                    MSG_DATA: "Hello",
                    MSG_SRC_ADR: self.localServerAddress,
                    MSG_REMOTE_FLAG: 0,
                },
            )
        else:
            # Give some time to the node 0 to be the first one to start
            time.sleep(1)
            sendMsg(
                self.remoteServerAddresses[0],
                {
                    MSG_DATA: "Hello",
                    MSG_SRC_ADR: self.localServerAddress,
                    MSG_REMOTE_FLAG: 0,
                },
            )
            rcvMsg(self.queue)
        print("system is up and running")

    # Destructor
    def __del__(self):
        # Send 'exit' to local server
        print("node is shutting down...")
        sendMsg(("localhost", self.localPort), "exit")
        self.server.join()

        # Delete queue and server
        del self.queue
        del self.server

    def fl_centralized(
        self,
        fl_cent_server_processing,
        fl_cent_client_processing,
        localData,
        privateData,
        noIterations=1,
    ):
        # Save initial localData and privateData
        self.localData = localData
        self.privateData = privateData

        for k in range(noIterations):
            if self.nodeId == self.flSrvId:
                # Server
                broadcastMsg(
                    self.remoteServerAddresses,
                    {
                        MSG_DATA: self.localData,
                        MSG_SRC_ADR: self.localServerAddress,
                        MSG_REMOTE_FLAG: 0,
                    },
                )
                msgs = rcvMsgs(self.queue, self.noNodes - 1)
                msgsPayload = list(map(lambda item: item[MSG_DATA], msgs))
                print("server received:", msgs)
                self.localData = fl_cent_server_processing(
                    self.privateData, msgsPayload
                )
                print("new server localData=", self.localData)

            else:
                # Client
                msg = rcvMsg(self.queue)
                print("client received:", msg)
                self.localData = fl_cent_client_processing(
                    self.localData, self.privateData, msg[MSG_DATA]
                )
                sendMsg(
                    self.flSrvAddress,
                    {
                        MSG_DATA: self.localData,
                        MSG_SRC_ADR: self.localServerAddress,
                        MSG_REMOTE_FLAG: 0,
                    },
                )

        # Return the final localData
        return self.localData

    def fl_decentralized(
        self,
        fl_decent_server_processing,
        fl_decent_client_processing,
        localData,
        privateData,
        noIterations=1,
    ):
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
        noNeighbors = len(self.remoteServerAddresses)
        dataFromClients1 = []

        for iterNo in range(noIterations):
            # This node is initially acting as a server - phase 1
            broadcastMsg(
                self.remoteServerAddresses,
                {
                    MSG_ITER_NO: iterNo,
                    MSG_SEQ_NO: PHASE1,
                    MSG_SRC_ADR: self.localServerAddress,
                    MSG_DATA: self.localData,
                    MSG_REMOTE_FLAG: 0,
                },
            )

            # This node now acts as a client - phase 2
            noRcvdMsgs = 0
            dataFromClients2 = []

            # First drain the buffer dataFromClients1
            assert len(dataFromClients1) <= noNeighbors
            while len(dataFromClients1) > 0:
                msg = dataFromClients1.pop(0)
                print("as a client, received from the buffer dataFromClients1:", msg)
                assert (msg[MSG_ITER_NO] == iterNo) and (msg[MSG_SEQ_NO] == PHASE1)
                noRcvdMsgs = noRcvdMsgs + 1
                tmpLocalData = fl_decent_client_processing(
                    self.localData, self.privateData, msg[MSG_DATA]
                )
                sendMsg(
                    tuple(msg[MSG_SRC_ADR]),
                    {
                        MSG_ITER_NO: iterNo,
                        MSG_SEQ_NO: PHASE2,
                        MSG_SRC_ADR: self.localServerAddress,
                        MSG_DATA: tmpLocalData,
                        MSG_REMOTE_FLAG: 0,
                    },
                )

            # Process the rest of the messages coming from the local server queue (see module mpapi.py)
            while noRcvdMsgs != 2 * noNeighbors:
                msg = rcvMsg(self.queue)

                # Is it a message from a client that already entered the treration iterNo+1? If yes, store it for the next itertion.
                if msg[MSG_ITER_NO] != iterNo:
                    assert (msg[MSG_ITER_NO] == iterNo + 1) and (
                        msg[MSG_SEQ_NO] == PHASE1
                    )
                    print(
                        "as a client, received the message from a node that already entered the next iteration:",
                        msg,
                    )
                    dataFromClients1.append(msg)
                    continue

                noRcvdMsgs = noRcvdMsgs + 1
                if msg[MSG_SEQ_NO] == PHASE1:
                    # The 1st msg from a neighbor acting as a server
                    # This node takes the role of a client
                    print("as a client received:", msg)
                    tmpLocalData = fl_decent_client_processing(
                        self.localData, self.privateData, msg[MSG_DATA]
                    )
                    # JSON converts tuples to lists, so msg[msgSrcAdr] must be converted back to a tuple(msg[msgSrcAdr])
                    sendMsg(
                        tuple(msg[MSG_SRC_ADR]),
                        {
                            MSG_ITER_NO: iterNo,
                            MSG_SEQ_NO: PHASE2,
                            MSG_SRC_ADR: self.localServerAddress,
                            MSG_DATA: tmpLocalData,
                            MSG_REMOTE_FLAG: 0,
                        },
                    )
                else:
                    # The 2nd msg from a neighbor acting as client
                    # This node takes the role of a server
                    dataFromClients2.append(msg[MSG_DATA])

            # All 2*noNeighbors messages have been processed
            # This node takes the final role of a server - phase 3
            print("as server received:", dataFromClients2)
            self.localData = fl_decent_server_processing(
                self.privateData, dataFromClients2
            )
            print("new server localData=", self.localData)

        # Return the final localData
        return self.localData

    def get1Meas(self, peerId, odata):
        assert self.nodeId != peerId

        # If this node wants to skip this time slot, just increment timeSlot and return None
        if odata == None:
            self.timeSlot += 1  # Increment time slot
            return None

        # Send own odata to the peer and then receive peer odata
        sendMsg(
            self.allServerAddresses[peerId],
            {
                MSG_SRC_ADR: self.localServerAddress,
                MSG_DATA: [self.timeSlot, self.nodeId, odata],
                MSG_REMOTE_FLAG: 0,
            },
        )

        if self.timeSlot in self.timeSlotsMap:
            msg = self.timeSlotsMap[self.timeSlot]
            del self.timeSlotsMap[self.timeSlot]
        else:
            while True:
                msg = rcvMsg(self.queue)[MSG_DATA]
                peerTimeSlot, peerNodeId, peerOdata = msg
                if peerTimeSlot != self.timeSlot:
                    self.timeSlotsMap[peerTimeSlot] = msg
                    continue
                else:
                    break

        # Unpack msg, do the asserts, and return peerOdata
        peerTimeSlot, peerNodeId, peerOdata = msg
        assert (self.timeSlot == peerTimeSlot) and (
            peerId == peerNodeId
        ), f"self.timeSlot={self.timeSlot}, peerTimeSlot={peerTimeSlot}, peerId={peerId}, peerNodeId={peerNodeId}"

        self.timeSlot += 1  # Increment time slot
        return peerOdata
