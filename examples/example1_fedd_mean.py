#
#   Example 1: Averaging the number of sensors readings that are above the given treshold
#
#   Description:
#   See the description of this example in the ZINC 2023 paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch example1_fedd_mean.py 3 id 0
#
from ptbfla_pkg.ptbfla import *

def main():
    # Parse command line arguments
    if len(sys.argv) != 4:
        # Args:
        #   noNodes - number of nodes, nodeId - id of a node, flSrvId - id of the FL server
        print('Program usage: python example1_fedd_mean.py noNodes nodeId flSrvId')
        print('Example: noNodes==3, nodeId=0..2, flSrvId==0, i.e. 3 nodes (id=0,1,2), server is node 0:')
        print('python example1_fedd_mean.py 3 0 0, python example1_fedd_mean.py 3 1 0, python example1_fedd_mean.py 3 2 0')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    flSrvId = int( sys.argv[3] )
    print(noNodes, nodeId, flSrvId)
    
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId, flSrvId)
    
    # Set localData for FL server/clients as follows
    if nodeId == flSrvId:
        # Set threshold
        localData = 69.5
    else:
        # Set clients' readings
        localData = 68.0
        if nodeId == noNodes-1:
            localData = 70.5
    
    # Call fl_centralized with noIterations = 1 (default)
    ret = ptb.fl_centralized(fl_server_fun, fl_client_fun, localData, None)
    print('the final localData =', ret)
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')

def fl_client_fun(localData, privateData, msg):
    clientReading = localData
    threshold = msg
    tmp = 0.0
    if clientReading > threshold:
        tmp = 1.0
    return tmp

def fl_server_fun(privateData, msgs):
    listOfIsOverAsFloat = msgs
    tmp = sum(listOfIsOverAsFloat) / len(listOfIsOverAsFloat)
    return tmp

if __name__ == '__main__':
    main()
