#
#   Example 3: Simple decentralized FL on single element lists
#
#   Description:
#   This example is based on the 3rd example in the ZINC 2023 paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch mp_async_example3_decent_avg.py 3 id 192.168.0.2
#
import asyncio

from ptbfla_pkg.mp_async_ptbfla import *

async def main():
    # Parse command line arguments
    if len(sys.argv) != 4:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node, masterIpAdr - master's IP address
        print('Program usage: python mp_async_example3_decent_avg.py noNodes nodeId masterIpAdr')
        print('Example: noNodes==3, nodeId=0..2, i.e. 3 nodes (id=0,1,2):')
        print('python mp_async_example3_decent_avg.py 3 0 192.168.0.2, python mp_async_example3_decent_avg.py 3 1 192.168.0.2,\n',
              'python mp_async_example3_decent_avg.py 3 2 192.168.0.2')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    masterIpAdr = sys.argv[3]
    print(noNodes, nodeId, masterIpAdr)
    
    # Start-up: create PtbFla object; note: flSrvId is set to 0, but not used by fl_decentralized.
    ptb = PtbFla(noNodes, nodeId, 0, masterIpAdr)
    await ptb.start()
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 3
    ret = await ptb.fl_decentralized(fl_decent_server_processing, fl_decent_client_processing, [nodeId+1], None, 3)
    print('the final localData =', ret)
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')

def fl_decent_client_processing(localData, privateData, msg):
    return [(localData[0] + msg[0])/2]

def fl_decent_server_processing(privateData, msgs):
    tmp = 0.0
    for lst in msgs:
        tmp = tmp + lst[0]
    tmp = tmp / len(msgs)
    return [tmp]

def run_main():
    #asyncio.run(main()) # this riases RuntimeError: Event loop is closed
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main()) # this reports "Task was destroyed but it is pending!" two times

if __name__ == '__main__':
    run_main()
