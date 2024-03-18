cfg = {
    "wlan": {
        "ssid": b"home_s",
        "pswd": b"Sv. apostoli Petar i Pavle"
    },
    "myIP": "",
    
    # Example 2 argv elements are: program, noNodes, nodeId, flSrvId, masterIpAdr
    
    # Test Case 1: node 0 in rp2 at IP '192.168.2.3' and node 1 in PC
    #"argv": ['mp_async_example2_cent_avg.py', '2', '0', '0', '192.168.2.3'],
    
    # Test Case 2: node 0 in rp2 at IP '192.168.2.3' and nodes 1-2 (1 and 2) in PC
    #"argv": ['mp_async_example2_cent_avg.py', '3', '0', '0', '192.168.2.3'],
    
    # Test Case 3: node 0 in PC at IP '192.168.2.4' and nodes 1-2 in two rp2s with respective argvs below.
    # (Note: to setup rp2s, comment/uncomment appropriate lines, save file, and upload project to rp2.)
    #"argv": ['mp_async_example2_cent_avg.py', '3', '1', '0', '192.168.2.4'],  # argv for the node 1 in rp2 no. 1
    "argv": ['mp_async_example2_cent_avg.py', '3', '2', '0', '192.168.2.4'],  # argv for the node 2 in rp2 no. 2
}