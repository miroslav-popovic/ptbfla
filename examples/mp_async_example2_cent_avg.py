#
#   Example 2: Simple centralized FL on single element lists
#
#   Description:
#   This example is based on the 2nd example in the MPT-FLA paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch mp_async_example2_cent_avg.py 3 id 0 192.168.0.2
#
import asyncio

from ptbfla_pkg.mp_async_ptbfla import *

async def main():
    # Parse command line arguments
    if len(sys.argv) != 5:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node, flSrvId - id of the FL server, masterIpAdr - master's IP address
        print('Program usage: python mp_async_example2_cent_avg.py noNodes nodeId flSrvId masterIpAdr')
        print('Example: noNodes==3, nodeId=0..2, flSrvId==0, i.e. 3 nodes (id=0,1,2), server is node 0:')
        print('python mp_async_example2_cent_avg.py 3 0 0 192.168.0.2, python mp_async_example2_cent_avg.py 3 1 0 192.168.0.2,\n',
              'python mp_async_example2_cent_avg.py 3 2 0 192.168.0.2')
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
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 10
    ret = await ptb.fl_centralized(fl_cent_server_processing, fl_cent_client_processing, [nodeId+1], None, 10)
    print('the final localData =', ret)
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')

def fl_cent_client_processing(localData, privateData, msg):
    return [(localData[0] + msg[0])/2]

def fl_cent_server_processing(privateData, msgs):
    tmp = 0.0
    for lst in msgs:
        tmp = tmp + lst[0]
    tmp = tmp / len(msgs)
    return [tmp]

def run_main():
    asyncio.run(main())

if __name__ == '__main__':
    run_main()
