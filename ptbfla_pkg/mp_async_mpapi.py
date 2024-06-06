import asyncio
import sys
import json

# Simple list queue and the event
listQueue = []
msgReceived = asyncio.Event()

async def server_fun(reader, writer):

    # Step 1.
    data = await reader.read(4)   # Read the length of the message
    if not data:
        return
    length = int.from_bytes(data, "big")
    segments = []
    remaining_length = length
    while remaining_length > 0:
        segment = await reader.read(1024)
        segments.append(segment)
        remaining_length -= len(segment)
    msg = b"".join(segments)
    jmsg = msg.decode()
    msg = json.loads(jmsg)
    addr = writer.get_extra_info('peername')
    
    # Send acknowledgment back to client
    ack_msg = {"status": "received"}
    jmsg_ack = json.dumps(ack_msg)
    msg_length = len(jmsg_ack).to_bytes(4, "big")
    writer.write(msg_length)
    writer.write(jmsg_ack.encode())
    await writer.drain()
    
    # Step 3.
    #print("Close the connection")
    writer.close()
    await writer.wait_closed()
    
    # Step 4.
    global listQueue, msgReceived
    # Append the msg and set the event
    listQueue.append(msg)
    msgReceived.set()

async def sendMsg(remote_server_address, msg) -> None:
    # Step 1.
    reader, writer = await asyncio.open_connection(remote_server_address[0], remote_server_address[1])
    
    # Step 2.
    jmsg = json.dumps(msg)
    msg_length = len(jmsg).to_bytes(4, "big")
    writer.write(msg_length)
    
    # Send the message in segments
    for i in range(0, len(jmsg), 1024):
        segment = jmsg[i:i+1024].encode()
        writer.write(segment)
        await writer.drain()
        
        
    data = await reader.read(4)   # Read the length of the message
    if not data:
        return
    length = int.from_bytes(data, "big")
    segments = []
    remaining_length = length
    while remaining_length > 0:
        segment = await reader.read(1024)
        segments.append(segment)
        remaining_length -= len(segment)        
    ack_msg = b"".join(segments)
    jmsg_ack = ack_msg.decode()
    ack_msg = json.loads(jmsg_ack)
    
    # Step 4.
    #print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def rcvMsg():
    global listQueue, msgReceived
    retval = None
    while retval is None:
        if len(listQueue) > 0:
            retval = listQueue.pop(0)
            break
        await msgReceived.wait()
        msgReceived.clear()
    return retval

async def broadcastMsg(list_of_remote_server_address, msg) -> None:
    for remote_server_address in list_of_remote_server_address:
        await sendMsg(remote_server_address, msg)

async def rcvMsgs(no_of_messages_to_receive):
    msgs = []
    
    for i in range(no_of_messages_to_receive):
        msg = await rcvMsg()
        msgs.append(msg)
    
    return msgs

