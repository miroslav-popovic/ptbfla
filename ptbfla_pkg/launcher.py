import sys
import copy
import subprocess

def run():
    # Check whether the sys.platform is supported
    if sys.platform != 'win32' and sys.platform != 'linux':
        print('Error:', sys.platform, 'is not supported!')
        exit(0)
    
    # Check the number of argv elements - must be at least 4 of them
    #print('sys.argv=', sys.argv)
    if(len(sys.argv) < 4):
        print('Error: At least 4 arguments are required.')
        print('Usage example: launch example1_fedd_mean.py 3 * 0')
        exit(0)
    
    # Set Python interpreter executable path
    newArgv = copy.deepcopy(sys.argv)
    newArgv[0] = sys.executable
    
    # Create a list of argvs for all the nodes
    noNodes = int(sys.argv[2])      # 3rd arg is the number of nodes
    lstArgv = []
    for nodeId in range(noNodes):
        newArgv[3] = str(nodeId)    # 4th arg is the node's id
        lstArgv.append(copy.deepcopy(newArgv))
    #print(lstArgv)
    
    # Launch nodes
    pids = [0] * noNodes
    for nodeId in range(noNodes):
        if sys.platform == 'win32':
            pids[nodeId] = subprocess.Popen(lstArgv[nodeId], creationflags=subprocess.CREATE_NEW_CONSOLE).pid
        if sys.platform == 'linux':
            pids[nodeId] = subprocess.Popen(['gnome-terminal','--']+lstArgv[nodeId]).pid


