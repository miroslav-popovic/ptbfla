#
#   Example 6: ODTS (Orbit Determination and Time Synchronization)
#
#   Description:
#   TODO
#
#   Run this example:
#       1. First change directory with this command: cd src/examples
#       2. For the case 2 Svs (2 SVs, 1 blok, 1 t_slots) enter: launch mp_async_example6_odts.py 2 id 1 1 192.168.0.2
#       3. For the case 4 Svs (4 SVs, 1 blok, 3 t_slots) enter: launch mp_async_example6_odts.py 4 id 1 3 192.168.0.2
#
import asyncio

from ptbfla_pkg.mp_async_ptbfla import *

async def main():
    # Parse command line arguments
    if len(sys.argv) != 6:
        # Args:
        #   no_nodes - number of nodes, node_id - id of a node, N - number of blocks, n - number of time slots, masterIpAdr - master's IP address
        print('Program usage: python mp_async_example6_odts.py no_nodes node_id N n masterIpAdr')
        print('Note: no_nodes must be even integer.')
        exit()
    
    # Process command line arguments
    no_nodes = int( sys.argv[1] )
    node_id = int( sys.argv[2] )
    if no_nodes%2 != 0:
        print('no_nodes must be even integer!')
        exit()
    print(no_nodes, node_id)
    
    # Set the number of blocks N (i.e., the number of iterations), the number of time slots (or just slots n), and masterIpAdr
    N = int( sys.argv[3] )
    n = int( sys.argv[4] )
    masterIpAdr = sys.argv[5]
    flSrvId = 0     # flSrvId is not used by the method get1Meas, still is required by the constructor
    
    # Start-up: create PtbFla object
    ptb = PtbFla(no_nodes, node_id, flSrvId, masterIpAdr)
    await ptb.start()
    
    #settings = setParameters() # establish parameters settings for the ODTS simulation
    #orbital_data = getOrbitalData(orbit_data_file) # getting satellites orbital data
    orbital_data = [1.0+i for i in range(no_nodes)]  # In this mockup, each satellite data is a simple float
    odata = orbital_data[node_id]                    # This satellite's data
    print('orbital_data =', orbital_data)
    print('odata =', odata)
    
    state = odata  # In this mockup, the initial satellite sate is equal to its odata
    
    #connections = islScheduling(orbital_data) # establish inter-satellite connections over time
    connections = islScheduling(no_nodes, n)       # In this mockup, islScheduling's args are number of nodes and slots
    
    for block_number in range(N): # iterate over blocks; block_number counts from 0 to N-1
        
        for t_slot in range(n):   # iterate over time slots
            
            print('.')
            # obs = ptb.getMeas(node_id, connections(t_slot), orbital_data, settings) # simulate measurements
            peer_id = connections[(t_slot, node_id)]
            obs = await ptb.get1Meas(peer_id, odata) # simulate measurements
            
            state_update = odts(state, obs) # performing ODTS
            
            state = state_update
            print('state =', state)
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')

#from random import shuffle  # this could be used to generate a file that all the nodes would read

# In this mockup, we use the deterministic rotate the list l by n postions, here 1 position
def rotate(l, n):
    return l[n:] + l[:n]

def islScheduling(no_nodes, n):
    """
    This function returns a dictionary (map) comprising key-value pairs,
    where the key (tslot, nodex) and the corresponding value nodey mean that
    in the time slot tslot the pair of nodes nodex and nodey will communicate
    to exchange their ods data.
    """
    assert no_nodes%2 == 0
    noPairs = int(no_nodes/2)
    dict = {}
    
    all_node_ids = [id for id in range(no_nodes)]  # list of all node ids
    
    for tslot in range(n):  # for each time slot
        
        #shuffle(all_node_ids)  # random shuffel the list all_node_ids
        all_node_ids = rotate(all_node_ids, 1)
        print('tslot =', tslot, ', shuffled all_node_ids =', all_node_ids)
        
        for i in range(noPairs):  # for each node pair
            i1 = 2*i              # set even-odd pair indices
            i2 = i1 + 1
            id1 = all_node_ids[i1]  # set even-odd node IDs
            id2 = all_node_ids[i2]
            dict[(tslot, id1)] = id2  # set the dict's key-value pairs for the even-odd node pairs
            dict[(tslot, id2)] = id1
    
    print('dict =', dict)
    return dict

def odts(state, obs):
    # In this mockup, odts just averages state and obs
    return (state + obs)/2.0

def run_main():
    #asyncio.run(main()) # this riases RuntimeError: Event loop is closed
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main()) # this reports "Task was destroyed but it is pending!" two times

if __name__ == '__main__':
    run_main()
