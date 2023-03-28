#
#   Example 3: Simple decentralized FL on single element lists
#
#   Description:
#   See the description of this example in the ZINC 2023 paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch example3_decent_avg.py 3 id
#
from ptbfla_pkg.ptbfla import *

def main():
    # Parse command line arguments
    if len(sys.argv) != 3:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node
        print('Program usage: python example3_decent_avg.py noNodes nodeId')
        print('Example: noNodes==3, nodeId=0..2, i.e. 3 nodes (id=0,1,2):')
        print('python example3_decent_avg.py 3 0, python example3_decent_avg.py 3 1, python example3_decent_avg.py 3 2')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    print(noNodes, nodeId)
    
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId)
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 3
    ret = ptb.fl_decentralized(fl_decent_server_processing, fl_decent_client_processing, [nodeId+1], None, 3)
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

if __name__ == '__main__':
    main()
