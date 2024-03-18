import asyncio
import sys
import json

# Simple list queue and the event
listQueue = []
msgReceived = asyncio.Event()

async def server_fun(reader, writer):
    # Step 1.
    data = await reader.read(1024)   # Magic number 1024
    jmsg = data.decode()
    msg = json.loads(jmsg)
    addr = writer.get_extra_info('peername')

    #print(f"Received {msg!r} from {addr!r}")
    
    # Step 2.
    #print(f"Send: {msg!r}")
    writer.write(data)
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
    #print(f'Send: {msg!r}')
    jmsg = json.dumps(msg)
    writer.write(jmsg.encode())
    await writer.drain()
    
    # Step 3.
    data = await reader.read(1024)   # Magic number 1024
    jmsg2 = data.decode()
    msg2 = json.loads(jmsg)
    #print(f'Received: {msg2!r}')
    
    # Step 4.
    #print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def rcvMsg():
    global listQueue, msgReceived
    retval = None
    while retval == None:
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
        msgs.append( msg )
    
    return msgs
