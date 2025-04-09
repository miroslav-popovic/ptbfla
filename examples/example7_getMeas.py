from ptbfla_pkg.ptbfla import *


N_NODES_TEST2 = 11
N_NODES_TEST3 = 4


def get_peer_ids(all_node_ids, node_id):
    all_node_ids.remove(node_id)

    return all_node_ids


G1 = 0
S1 = 1
S2 = 2
S3 = 3
S4 = 4
S5 = 5
S6 = 6
S7 = 7
S8 = 8
S9 = 9
S10 = 10


def get_peer_ids_custom_t3(node_id):
    # gs 0 , sv 1 2 3 4 5 6 7 8 9 10 #11 members

    # looks like all must initialy talk to the first that starts, later that hypothesis was rejected
    if node_id == G1:
        return [S1, S2, S3, S4, S5]
    if node_id == S1:
        return [G1, S7, S9]
    if node_id == S2:
        return [G1, S8, S6]
    if node_id == S3:
        return [G1, S6, S5]
    if node_id == S4:
        return [G1, S5]
    if node_id == S5:
        return [G1, S3, S4, S6]
    if node_id == S6:
        return [S2, S3, S5, S8]
    if node_id == S7:
        return [S8, S10, S9, S1]
    if node_id == S8:
        return [S7, S10, S6, S2]
    if node_id == S9:
        return [S10, S7, S1]
    if node_id == S10:
        return [S9, S7, S8]


def get_peer_ids_custom_3_attime(node_id, number_of_nodes):
    if number_of_nodes < 2:
        raise ValueError("Number of nodes must be at least 2.")

    peers = {i: [0] for i in range(number_of_nodes)}  # Every node connects to 0
    peers[0] = list(range(1, number_of_nodes))  # Node 0 connects to all others

    for i in range(1, number_of_nodes):
        if i - 1 > 0:
            peers[i].append(i - 1)  # Connect to previous node
        if i + 1 < number_of_nodes:
            peers[i].append(i + 1)  # Connect to next node

    return peers.get(node_id, [])


def main_1(no_nodes, node_id):
    if len(sys.argv) != 3:
        print(
            "Incorect number of arguments...  program should be caled with no_nodes id ; example: launch example7.py 170 id"
        )

    ptb = PtbFla(no_nodes, node_id)
    print(ptb.nodeId)
    orbital_data = [1.0 + i for i in range(no_nodes + 1)]
    odata = orbital_data[node_id]  # This satellite's data
    print("orbital_data =", orbital_data)
    print("odata =", odata)

    # In this mockup, the initial satellite sate is equal to its odata

    # connections = islScheduling(orbital_data) # establish inter-satellite connections over time
    all_node_ids = [id for id in range(no_nodes)]

    peer_ids = get_peer_ids_custom_3_attime(node_id, no_nodes)
    obs = ptb.getMeas(peer_ids, odata)  # simulate measurements

    print(obs)

    # Shutdown
    del ptb

    time.sleep(WAIT_TIME)


def main_2(node_id):

    no_nodes = N_NODES_TEST2

    ptb = PtbFla(no_nodes, node_id)
    print(ptb.nodeId)
    orbital_data = [1.0 + i for i in range(no_nodes)]
    odata = orbital_data[node_id]  # This satellite's data
    print("orbital_data =", orbital_data)
    print("odata =", odata)

    # In this mockup, the initial satellite sate is equal to its odata

    # connections = islScheduling(orbital_data) # establish inter-satellite connections over time
    all_node_ids = [id for id in range(no_nodes)]

    peer_ids = get_peer_ids_custom_t3(node_id)
    peer_ids.sort()
    obs = ptb.getMeas(peer_ids, odata)  # simulate measurements

    print(obs)

    # Shutdown
    del ptb

    time.sleep(WAIT_TIME)


def main_3(node_id):

    if len(sys.argv) != 3:
        print(
            "Incorect number of arguments...  program should be caled with id  ,example: launch example7.py id"
        )

    no_nodes = N_NODES_TEST3

    ptb = PtbFla(no_nodes, node_id)
    print(ptb.nodeId)
    orbital_data = [1.0 + i for i in range(no_nodes)]
    odata = orbital_data[node_id]  # This satellite's data
    print("orbital_data =", orbital_data)
    print("odata =", odata)

    # In this mockup, the initial satellite sate is equal to its odata

    # connections = islScheduling(orbital_data) # establish inter-satellite connections over time
    all_node_ids = [id for id in range(no_nodes)]

    peer_ids = get_peer_ids(all_node_ids, node_id)
    obs = ptb.getMeas(peer_ids, odata)  # simulate measurements

    print(obs)

    # Shutdown
    del ptb

    pkey = input("press any key to continue...")


WAIT_TIME = 10  # This value controls how long the wait between the examples is

if __name__ == "__main__":
    # activate venv
    # select the test

    # position yourself into the dir where this example is located

    no_nodes = int(sys.argv[1])
    if no_nodes < 11:
        print(
            "number of nodes should be at least 11 so that all examples would run properly"
        )
        exit()

    node_id = int(sys.argv[2])

    """
    call as launch example7_getMeas.py no_nodes id
    ex.:
        launch example7_getMeas.py 11 id
        launch example7_getMeas.py 20 id
        launch example7_getMeas.py 170 id
    """

    # example will be performed for the specified number of nodes
    print("\n######## case 1  chain of nodes talking with one GS #######\n")
    main_1(
        no_nodes, node_id
    )  # most like the case described in the usecase, every satelite talks to the groundstation 0 and to its neighbours in the chain

    if node_id >= N_NODES_TEST2:
        exit()

    # example  will be performed for 11 nodes
    print("\n######## case 2  arbitrary graf #######\n")
    main_2(
        node_id
    )  # arbitrary graf containing 11 nodes everyone talks to a different number of satelites

    if node_id >= N_NODES_TEST3:
        exit()

    # example  will be performed for 4 nodes after which the user will be prompted to press any button to continue
    print("\n######## case 3  broadcast #######\n")
    main_3(node_id)  # every satelite talks to everyone except itself, broadcast like
