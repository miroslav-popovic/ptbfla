cfg = {
    "wlan": {
        "ssid": b"SSID",
        "pswd": b"Password"
    },
    "myIP": "",
    
    # Example 3 argv elements are: program, noNodes, nodeId, N, n, masterIpAdr
    
    # Test Case 1: node 0 in PC at IP '192.168.2.4' and nodes 1-2 in two rp2s with respective argvs below.
    # (Note: to setup rp2s, comment/uncomment appropriate lines, save file, and upload project to rp2.)
    #"argv": ['mp_async_example6_odts.py', '4', '1', '1', '3', '192.168.2.4'],  # argv for the node 1 in rp2 no. 1
    "argv": ['mp_async_example6_odts.py', '4', '2', '1', '3', '192.168.2.4'],  # argv for the node 2 in rp2 no. 2
}