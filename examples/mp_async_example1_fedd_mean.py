#
#   Example 1: Averaging the number of sensors readings that are above the given treshold
#
#   Description:
#   This example is based on the 1st example in the MPT-FLA paper, see link in README.md.
#
#   Run this example (after: cd src/examples):
#       launch mp_async_example1_fedd_mean.py 3 id 0 192.168.0.2
#
import sys
import asyncio
if sys.platform == 'rp2':
    import machine
    import utime
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)

from ptbfla_pkg.mp_async_ptbfla import *

async def main():
    # Parse command line arguments
    if len(sys.argv) != 5:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node, flSrvId - id of the FL server, masterIpAdr - master's IP address
        print('Program usage: python example1_fedd_mean.py noNodes nodeId flSrvId masterIpAdr')
        print('Example: noNodes==3, nodeId=0..2, flSrvId==0, masterIpAdr, i.e. 3 nodes (id=0,1,2), server is node 0:')
        print('python mp_async_example1_fedd_mean.py 3 0 0 192.168.0.2, python mp_async_example1_fedd_mean.py 3 1 0 192.168.0.2,\n',
              'python mp_async_example1_fedd_mean.py 3 2 0 192.168.0.2')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    flSrvId = int( sys.argv[3] )
    masterIpAdr = sys.argv[4]
    print(noNodes, nodeId, flSrvId, masterIpAdr)
    
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId, flSrvId, masterIpAdr)
    await ptb.start()
    
    # Set localData for FL server/clients as follows
    if nodeId == flSrvId:
        # Set threshold. Formula Fahrenheit to Celsius: y = (x−32)×5/9, where x[°F] and y[°C].
        localData = 20.83   # i.e., 69.5°F
    else:
        # Set clients' readings
        localData =  20.00  # i.e., 68.0°F
        if nodeId == noNodes-1:
            localData = 21.39   # i.e., 70.50°F
    
    # Call fl_centralized with noIterations = 1 (default)
    ret = await ptb.fl_centralized(fl_server_fun, fl_client_fun, localData, None)
    print('the final localData =', ret)
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')


def fl_client_fun(localData, privateData, msg):
    clientReading = localData
    if sys.platform == 'rp2':
        reading = sensor_temp.read_u16() * conversion_factor
        clientReading = 27 - (reading - 0.706)/0.001721
        print('clientReading=', clientReading)
    threshold = msg
    tmp = 0.0
    if clientReading > threshold:
        tmp = 1.0
    return tmp

def fl_server_fun(privateData, msgs):
    listOfIsOverAsFloat = msgs
    tmp = sum(listOfIsOverAsFloat) / len(listOfIsOverAsFloat)
    return tmp

def run_main():
    #asyncio.run(main()) # this riases RuntimeError: Event loop is closed
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main()) # this reports "Task was destroyed but it is pending!" two times

if __name__ == '__main__':
    run_main()
