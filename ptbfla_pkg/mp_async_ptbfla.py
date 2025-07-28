#
#  Python Test Bed for Federated Learning Algorithms based on Python Asyncio package
#
import asyncio
import sys
import time
import socket

from .mp_async_mpapi import *


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(
            ("10.255.255.255", 1)
        )  # the address 10.255.255.255 is from the Private IP Address Range
        local_ip = s.getsockname()[0]
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return local_ip
    except Exception as e:
        print("Error:", e)
        return None


class PtbFla:
    # Constructor
    def __init__(self, noNodes, nodeId, flSrvId=0, masterIpAdr="localhost"):
        self.noNodes = noNodes
        self.nodeId = nodeId
        self.flSrvId = flSrvId
        self.masterIpAdr = masterIpAdr

        # Set myIP and myPort
        if sys.platform == "rp2":
            import config

            myIpAdr = config.cfg["myIP"]
        else:
            myIpAdr = get_local_ip()
        print("myIpAdr =", myIpAdr)

        if masterIpAdr == "localhost":
            myIpAdr = "localhost"
        myPort = 6000 + nodeId

        # Set the local server's address
        self.server_task = None
        self.localServerAddress = (myIpAdr, myPort)
        self.myIpAdr = myIpAdr
        self.myPort = myPort

        # Set the initial timeSlot for the function get1Meas
        self.timeSlot = 0

        # Create the time slot queue (in form of a map) to be used by the function getMeas
        # timeSlotsMap is a dictionary whose key is a timeSlot and the value is the peer's msg
        self.timeSlotsMap = {}

        # Create getMeasMap to used by the function getMeas
        self.getMeasMap = {}

    async def start(self) -> None:
        # Setup local server
        self.server = await asyncio.start_server(server_fun, self.myIpAdr, self.myPort)
        self.server_task = asyncio.create_task(self.server.serve_forever())

        # Automatic system start-up:
        #   - assumption 1: node 0 starts first;
        #   - assumption 2: for nodes not 0, remoteServerAddresses[0] is the remote addres of node 0;
        #   - node 0 waits for hello from all other nodes and then says hello to all other nodes;
        #   - all other nodes say hello to node 0 and wait for hello from node 0;
        #   - this algorithm will not work only if node 0 does not start first;
        print("system is comming up...")
        if self.nodeId == 0:
            # This code executes master process only
            msg = await rcvMsgs(self.noNodes - 1)
            msg = [[self.nodeId, self.myIpAdr, self.myPort]] + msg
            # Sort the msg list in nodeId order
            d = {}
            for elem in msg:
                d[elem[0]] = [elem[1], elem[2]]
            msgSorted = [d[k] for k in sorted(d)]

            # Note: we postpone the broadcastMsg until we set the self.remoteServerAddresses

        else:
            # This code execte all other processes
            # Give some time to the node 0 to be the first one to start
            await asyncio.sleep(
                1
            )  # This cannot be called form a non-async function like the constructor
            await sendMsg(
                (self.masterIpAdr, 6000), [self.nodeId, self.myIpAdr, self.myPort]
            )
            msgSorted = await rcvMsg()

        # This code execute all the processes i.e., both the master and other proceses
        print("system is up and running")

        self.allServerAddresses = [(el[0], el[1]) for el in msgSorted]
        print("self.allServerAddresses=", self.allServerAddresses)

        # Set FL server address
        self.flSrvAddress = self.allServerAddresses[self.flSrvId]

        self.remoteServerAddresses = [
            adr for adr in self.allServerAddresses if adr != self.localServerAddress
        ]
        print("self.remoteServerAddresses=", self.remoteServerAddresses)

        if self.nodeId == 0:
            # This code exectues master process only
            await broadcastMsg(self.remoteServerAddresses, msgSorted)

        await asyncio.sleep(10)

    # Destructor
    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if self.server:
                self.server.close()
                loop.call_soon_threadsafe(
                    asyncio.create_task, self.server.wait_closed()
                )
            if self.server_task:
                self.server_task.cancel()
        except Exception as e:
            print(f"Destructor error: {e}")
        print("node is shutting down...")
        # TODO: Terminate asyncio server

    async def fl_centralized(
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
                await broadcastMsg(self.remoteServerAddresses, self.localData)
                msgs = await rcvMsgs(self.noNodes - 1)
                # print('server received:', msgs)
                self.localData = fl_cent_server_processing(self.privateData, msgs)
                # print('new server localData=', self.localData)

            else:
                # Client
                msg = await rcvMsg()
                # print('client received:', msg)
                self.localData = fl_cent_client_processing(
                    self.localData, self.privateData, msg
                )
                await sendMsg(self.flSrvAddress, self.localData)

        # Return the final localData
        return self.localData

    async def fl_decentralized(
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
            await broadcastMsg(
                self.remoteServerAddresses,
                [iterNo, PHASE1, self.localServerAddress, self.localData],
            )

            # This node now acts as a client - phase 2
            noRcvdMsgs = 0
            dataFromClients2 = []

            # First drain the buffer dataFromClients1
            assert len(dataFromClients1) <= noNeighbors
            while len(dataFromClients1) > 0:
                msg = dataFromClients1.pop(0)
                print("as a client, received from the buffer dataFromClients1:", msg)
                assert (msg[msgIterNo] == iterNo) and (msg[msgSeqNo] == PHASE1)
                noRcvdMsgs = noRcvdMsgs + 1
                tmpLocalData = fl_decent_client_processing(
                    self.localData, self.privateData, msg[msgData]
                )
                await sendMsg(
                    tuple(msg[msgSrcAdr]),
                    [iterNo, PHASE2, self.localServerAddress, tmpLocalData],
                )

            # Process the rest of the messages coming from the local server queue (see module mpapi.py)
            while noRcvdMsgs != 2 * noNeighbors:
                msg = await rcvMsg()

                # Is it a message from a client that already entered the treration iterNo+1? If yes, store it for the next itertion.
                if msg[msgIterNo] != iterNo:
                    assert (msg[msgIterNo] == iterNo + 1) and (msg[msgSeqNo] == PHASE1)
                    print(
                        "as a client, received the message from a node that already entered the next iteration:",
                        msg,
                    )
                    dataFromClients1.append(msg)
                    continue

                noRcvdMsgs = noRcvdMsgs + 1
                if msg[msgSeqNo] == PHASE1:
                    # The 1st msg from a neighbor acting as a server
                    # This node takes the role of a client
                    print("as a client received:", msg)
                    tmpLocalData = fl_decent_client_processing(
                        self.localData, self.privateData, msg[msgData]
                    )
                    # JSON converts tuples to lists, so msg[msgSrcAdr] must be converted back to a tuple(msg[msgSrcAdr])
                    await sendMsg(
                        tuple(msg[msgSrcAdr]),
                        [iterNo, PHASE2, self.localServerAddress, tmpLocalData],
                    )
                else:
                    # The 2nd msg from a neighbor acting as client
                    # This node takes the role of a server
                    dataFromClients2.append(msg[msgData])

            # All 2*noNeighbors messages have been processed
            # This node takes the final role of a server - phase 3
            print("as server received:", dataFromClients2)
            self.localData = fl_decent_server_processing(
                self.privateData, dataFromClients2
            )
            print("new server localData=", self.localData)

        # Return the final localData
        return self.localData

    async def get1Meas(self, peerId, odata):
        assert self.nodeId != peerId

        # If this node wants to skip this time slot, just increment timeSlot and return None
        if odata == None:
            self.timeSlot += 1  # Increment time slot
            return None

        # Send own odata to the peer and then receive peer odata
        await sendMsg(
            self.allServerAddresses[peerId], [self.timeSlot, self.nodeId, odata]
        )

        if self.timeSlot in self.timeSlotsMap:
            msg = self.timeSlotsMap[self.timeSlot]
            del self.timeSlotsMap[self.timeSlot]
        else:
            while True:
                msg = await rcvMsg()
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

    async def getMeas(self, peerIds, odata):
        print(peerIds)
        assert self.nodeId not in peerIds  # Was: assert self.nodeId != peerId

        # If this node wants to skip this time slot, just increment timeSlot and return None
        if odata == None:
            self.timeSlot += 1  # Increment time slot
            return None

        # Send own odata to the peers and then receive peers odata
        for peerId in peerIds:
            await sendMsg(
                self.allServerAddresses[peerId],
                [self.timeSlot, self.nodeId, odata],
            )

        peerOdatas = []
        for peerId in peerIds:
            if (
                self.timeSlot,
                peerId,
            ) in self.timeSlotsMap:  # Was: if self.timeSlot in self.timeSlotsMap:
                msg = self.timeSlotsMap[
                    (self.timeSlot, peerId)
                ]  # Was: msg = self.timeSlotsMap[self.timeSlot]
                del self.timeSlotsMap[
                    (self.timeSlot, peerId)
                ]  # Was: del self.timeSlotsMap[self.timeSlot]
            else:
                while True:
                    msg = await rcvMsg()
                    peerTimeSlot, peerNodeId, peerOdata = msg
                    if (peerTimeSlot, peerNodeId) != (
                        self.timeSlot,
                        peerId,
                    ):  # Was: if peerTimeSlot != self.timeSlot:
                        self.timeSlotsMap[(peerTimeSlot, peerNodeId)] = (
                            msg  # Was: self.timeSlotsMap[peerTimeSlot] = msg
                        )
                        continue
                    else:
                        break

            # Unpack msg, do the asserts, and add peerOdata to peerOdatas
            peerTimeSlot, peerNodeId, peerOdata = msg
            assert (self.timeSlot == peerTimeSlot) and (
                peerId in peerIds
            ), f"self.timeSlot={self.timeSlot}, peerTimeSlot={peerTimeSlot}, peerId={peerId}, peerNodeId={peerNodeId}"

            # Add peerOdata to peerOdatas
            peerOdatas.append(peerOdata)

        self.timeSlot += 1  # Increment time slot
        return peerOdatas
        
