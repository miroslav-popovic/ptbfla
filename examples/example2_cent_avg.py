#
#   Example 2: Simple centralized FL on single element lists
#
#   Description:
#   See the description of this example in the ZINC 2023 paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch example2_cent_avg.py 3 id 0
#
from ptbfla_pkg.ptbfla import *

def main():
    # Parse command line arguments
    if len(sys.argv) != 4:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node, flSrvId - id of the FL server
        print('Program usage: python example2_cent_avg.py noNodes nodeId flSrvId')
        print('Example: noNodes==3, nodeId=0..2, flSrvId==0, i.e. 3 nodes (id=0,1,2), server is node 0:')
        print('python example2_cent_avg.py 3 0 0, python example2_cent_avg.py 3 1 0, python example2_cent_avg.py 3 2 0')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    flSrvId = int( sys.argv[3] )
    print(noNodes, nodeId, flSrvId)
    
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId, flSrvId)
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 10
    ret = ptb.fl_centralized(fl_cent_server_processing, fl_cent_client_processing, [nodeId+1], None, 10)
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

if __name__ == '__main__':
    main()
