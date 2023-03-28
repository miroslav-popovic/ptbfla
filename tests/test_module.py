#
# Run this test: python -m unittest src/tests/test_module.py
#
import unittest
from multiprocessing import Queue, Process
from ptbfla_pkg.ptbfla import *

#A unittest class for testing the Queue On PSTM class
class TestPtbFla(unittest.TestCase):
    
    #A dummy function for example and test purposes
    def test_dummy(self):
        self.assertEqual('dummy'.upper(), 'DUMMY')
    
    def test_centralized_1(self):
        # Create the queue for the process results
        qOfRes = Queue()
        
        # Create the processes for 3 nodes
        noNodes = 3
        flSrvId = 0
        nodes = [Process(target=node_centralized_1, args=(qOfRes, noNodes, nodeId, flSrvId)) for nodeId in range(noNodes)]
        
        # Start the processes
        [node.start() for node in nodes]
        
        # Wait for the processes to terminate
        [node.join() for node in nodes]
        
        # Create a dictionary of results
        dictRes = {}
        for ii in range(noNodes):
            resLst = qOfRes.get()
            dictRes[resLst[0]] = resLst[1]
        
        # Set dictMustBe and Assert
        dictMustBe = {0: [1.75], 1: [1.5], 2: [2.0]}
        self.assertEqual(dictRes, dictMustBe)
        
        # Delete qOfRes
        del qOfRes
    
    def test_decentralized_1(self):
        # Create the queue for the process results
        qOfRes = Queue()
        
        # Create the processes for 3 nodes
        noNodes = 3
        nodes = [Process(target=node_decentralized_1, args=(qOfRes, noNodes, nodeId)) for nodeId in range(noNodes)]
        
        # Start the processes
        [node.start() for node in nodes]
        
        # Wait for the processes to terminate
        [node.join() for node in nodes]
        
        # Create a dictionary of results
        dictRes = {}
        for ii in range(noNodes):
            resLst = qOfRes.get()
            dictRes[resLst[0]] = resLst[1]
        
        # Set dictMustBe and Assert
        dictMustBe = {0: [1.75], 1: [2.0], 2: [2.25]}
        self.assertEqual(dictRes, dictMustBe)
        
        # Delete qOfRes
        del qOfRes

def node_centralized_1(qOfRes, noNodes, nodeId, flSrvId):
    #print('noNodes, nodeId, flSrvId =', noNodes, nodeId, flSrvId)
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId, flSrvId)
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 1 (default)
    ret = ptb.fl_centralized(fl_server_processing, fl_client_processing, [nodeId+1], None)
    #print('the final localData =', ret)
    qOfRes.put([nodeId, ret])
    
    # Shutdown
    del ptb
    #pkey = input('press any key to continue...')

def node_decentralized_1(qOfRes, noNodes, nodeId):
    #print('noNodes, nodeId =', noNodes, nodeId)
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId)
    
    # Call fl_centralized with localData=[nodeId+1], noIterations = 1 (default)
    ret = ptb.fl_decentralized(fl_server_processing, fl_client_processing, [nodeId+1], None)
    #print('the final localData =', ret)
    qOfRes.put([nodeId, ret])
    
    # Shutdown
    del ptb
    #pkey = input('press any key to continue...')

def fl_client_processing(localData, privateData, msg):
    return [(localData[0] + msg[0])/2]

def fl_server_processing(privateData, msgs):
    tmp = 0.0
    for lst in msgs:
        tmp = tmp + lst[0]
    tmp = tmp / len(msgs)
    return [tmp]

if __name__ == '__main__':
    # Create the test suite and run it
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPtbFla)
    unittest.TextTestRunner(verbosity=2).run(suite)
