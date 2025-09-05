import sys
import copy
import subprocess

def run():
    # Check whether the sys.platform is supported
    if sys.platform != 'win32' and sys.platform != 'linux':
        print('Error:', sys.platform, 'is not supported!')
        exit(0)

    no_terminal=False
    if '--no_terminal' in sys.argv:
        no_terminal=True
        sys.argv.remove('--no_terminal')

    out_dev=None #default value inherits from parent
    if '--silent' in sys.argv:
        out_dev=subprocess.DEVNULL
        sys.argv.remove('--silent')

    # Check the number of argv elements - must be at least 4 of them
    # print('sys.argv=', sys.argv)
    if(len(sys.argv) < 4):
        print('Error: At least 4 arguments are required.')
        print('Usage example: launch example1_fedd_mean.py 3 * 0')
        print('If you want to run scripts without opening separate terminals add --no_terminal argument \n'
            '(argument --silent is optional if you also want no prints from the application)')
        exit(0)

    print("#~ launcher starting ~#")
    # Set Python interpreter executable path
    newArgv = copy.deepcopy(sys.argv)
    newArgv[0] = sys.executable

    # Set noNodes
    noNodes = int(sys.argv[2])      # 3rd arg is the number of nodes

    # There are 2 cases:
    # 1. ids may be an interval of IDs in the format 'lwId-hiId' e.g., '5-7'
    # 2. if ids is not an interval of IDs, then launch noNodes processes with IDs fom 0 to noNode-1
    # First, assume case 2, i.e., set default values
    lwId = 0
    hiId = noNodes - 1

    # Parese ids and set lwId hiId
    ids = sys.argv[3]
    if '-' in ids:
        lids = ids.split('-')
        if len(lids) == 2:
            lwId = int(lids[0])
            hiId = int(lids[1])
            if hiId < lwId:
                print('Error: The higest node ID is smaller than the lowest node ID!')
                exit(0)
    # print('lwId=', lwId, 'hiId=', hiId)

    # Create a list of argvs for all the nodes
    lstArgv = []
    for nodeId in range(lwId, hiId+1):
        newArgv[3] = str(nodeId)    # 4th arg is the node's id
        lstArgv.append(copy.deepcopy(newArgv))
    # print(lstArgv)

    # Launch nodes
    pids = [0] * (hiId - lwId + 1)

    for p in range(len(pids)):
        # print('lstArgv[p]=', lstArgv[p])
        if not no_terminal:
            if sys.platform == 'win32':
                pids[p] = subprocess.Popen(lstArgv[p], creationflags=subprocess.CREATE_NEW_CONSOLE).pid
            if sys.platform == 'linux':
                pids[p] = subprocess.Popen(['gnome-terminal','--']+lstArgv[p]).pid
        else:
            pids[p] = subprocess.Popen(lstArgv[p],stdout=out_dev,stderr=out_dev)

    if no_terminal:
        for pid in pids:
            pid.wait()
        print('## all subprocesses finished ##')

    print('#~ launcher finished ~#')