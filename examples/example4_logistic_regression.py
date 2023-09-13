#
#   Example 4: Centralized HFL using the logistic regression model
#                         (HFL = Horizontal Fedreated Learining) 
#
#   Description:
#   See the description of this example in the ECBS 2023 paper, see link in README.md
#
#   Run this example (after: cd src/examples):
#       launch example4_logistic_regression.py 3 id 2
#
#   Below are the supplementary functions and the 4 main functions corresponding to the
#   development phases of this example:
#       1. seq_base_case() - Sequential base case
#       2. seq_horizontal_federated() - Sequential HFL:
#       3. seq_horizontal_federated_with_callbacks() - Sequential HFL with callbacks
#       4. main() - PTB-FLA code with the same callbacks as in the pase 3.
#
# Source of dataset: https://www.kaggle.com/rakeshrau/social-network-ads
# Download data from: https://drive.google.com/uc?id=15WAD9_4CpUK6EWmgWVXU8YMnyYLKQvW8&export=download
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from math import exp

# The logistic regression model

# Normalize data
def normalize(X):
    return X - X.mean()

# Make predictions
def predict(X, b0, b1):
    return np.array([1 / (1 + exp(-1*b0 + -1*b1*x)) for x in X])

# Train the model, which comprises 2 coefficents: b0, b1
def logistic_regression(X, Y, b0=0., b1=0., L=0.001, epochs=300):
    # Normalize X
    X = normalize(X)
    
    # Update the model
    for epoch in range(epochs):
        y_pred = predict(X, b0, b1)
        # Derivatives of loss wrt b0 and wrt b1, respectively
        D_b0 = -2 * sum((Y - y_pred) * y_pred * (1 - y_pred))
        D_b1 = -2 * sum(X * (Y - y_pred) * y_pred * (1 - y_pred))
        # Update b0 and b1
        b0 = b0 - L * D_b0
        b1 = b1 - L * D_b1
    
    # Return the updated model
    return b0, b1

# Test the model
def evaluate(X_test, y_test, b0, b1):
    # Make predictions
    X_test_norm = normalize(X_test)
    y_pred = predict(X_test_norm, b0, b1)
    y_pred = [1 if p >= 0.5 else 0 for p in y_pred]
    
    # Calculate accuracy
    accuracy = 0.
    for i in range(len(y_pred)):
        if y_pred[i] == y_test.iloc[i]:
            accuracy += 1.
    accuracy = accuracy / len(y_pred)
    
    # Return predictions and accuracy
    return y_pred, accuracy

def seq_base_case():
    # Load the data
    data = pd.read_csv("Social_Network_Ads.csv")
    #data.head()

    # Visualizing the dataset
    '''
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.scatter(data['Age'], data['Purchased'])
    plt.show()
    '''
    # Divide the data to training set and test set. For reproducible set random_state=42.
    X_train, X_test, y_train, y_test = train_test_split(data['Age'], data['Purchased'], test_size=0.20, random_state=42)
    #print(f"X_train=\n{X_train}\ny_train=\n{y_train}")

    # Training the model
    b0, b1 = logistic_regression(X_train, y_train)
    print(f"Training on all the training records (origninal sequential code): b0={b0}, b1={b1}")

    # Test the model
    y_pred, accuracy = evaluate(X_test, y_test, b0, b1)
    '''
    plt.clf()
    plt.scatter(X_test, y_test)
    plt.scatter(X_test, y_pred, c="red")
    plt.show()
    '''
    print(f"Accuracy = {accuracy}")
    # For 300 epohes: b0=-0.928081834533905, b1=0.18206495679230542, Accuracy = 0.9

def seq_horizontal_federated():
    # Load the data (data has 400 records).
    data = pd.read_csv("Social_Network_Ads.csv")
    
    # Divide the data into the training set and the test set. For the result reproducible, set random_state=42.
    # X_train and y_train have 320 records each, whereas X_test and y_test have 80 records each.
    X_train, X_test, y_train, y_test = train_test_split(data['Age'], data['Purchased'], test_size=0.20, random_state=42)
    
    # Split X-train (320 records) into the two halves X_train_0 and X_train_1 (160 records each)
    X_train_0 = X_train.iloc[:160]
    X_train_1 = X_train.iloc[160:]
    y_train_0 = y_train[:160]
    y_train_1 = y_train[160:]
    
    # Train the model on two halves of training records - iteration by iteration
    # In bij: i - partition (or client) index, j - coefficeint index (0 for b0, 1 for b1)
    b0 = 0.; b1 = 0.
    b00 = 0.; b01 = 0.
    b10 = 0.; b11 = 0.
    for i in range(300):
        b00, b01 = logistic_regression(X_train_0, y_train_0, b0, b1, 0.001, 1)
        b10, b11 = logistic_regression(X_train_1, y_train_1, b0, b1, 0.001, 1)
        
        b0 = (b00 + b10)/2.
        b1 = (b01 + b11)/2.
        '''
        if i%10 == 0:
            print(f"i={i}, b0={b0}, b1={b1}")
        '''
    print(f"Training on two halves of records, iteration by iteration: i={i}, b0={b0}, b1={b1}")
    y_pred, accuracy = evaluate(X_test, y_test, b0, b1)
    print(f"Accuracy = {accuracy}")
    # i=299, b0=-0.8289785999293539, b1=0.17404838481420798, Accuracy = 0.9    
    
    # Train the model on two halves of the training records - iteration block by iteration block
    # In bij: i - partition (or client) index, j - coefficeint index (0 for b0, 1 for b1)
    b00, b01 = logistic_regression(X_train_0, y_train_0)
    b10, b11 = logistic_regression(X_train_1, y_train_1)
    b0 = (b00 + b10)/2.
    b1 = (b01 + b11)/2.
    print(f"Training on two halves of records, iteration block by iteration block: epochs=300, b0={b0}, b1={b1}")
    # epochs=300, b0=-0.8455539121726542, b1=0.1752408762629523, Accuracy = 0.9  - This is similar and a little better    
    
    y_pred, accuracy = evaluate(X_test, y_test, b0, b1)
    print(f"Accuracy = {accuracy}")
    return [b0, b1]

def seq_horizontal_federated_with_callbacks():
    # Load the data (data has 400 records).
    data = pd.read_csv("Social_Network_Ads.csv")
    
    # Divide the data to training set and test set. For reproducible set random_state=42.
    # X_train and y_train have 320 records each, whereas X_test and y_test have 80 records each.
    X_train, X_test, y_train, y_test = train_test_split(data['Age'], data['Purchased'], test_size=0.20, random_state=42)
    
    # Split X-train (320 records) into the two halves X_train_0 and X_train_1 (160 records each)
    X_train_0 = X_train.iloc[:160]
    X_train_1 = X_train.iloc[160:]
    y_train_0 = y_train[:160]
    y_train_1 = y_train[160:]
    
    # Train the model on two halves of training records - iteration block by iteration block
    # In bij: i - partition (or client) index, j - coefficeint index (0 for b0, 1 for b1)
    ''' This block of code from the function seq_horizontal_federated() is replaced with the next block of code.
    b0 = 0.; b1 = 0.
    epochs = 300
    b00, b01 = logistic_regression(X_train_0, y_train_0, b0, b1, 0.001, epochs)
    b10, b11 = logistic_regression(X_train_1, y_train_1, b0, b1, 0.001, epochs)
    '''
    localData = [0., 0.]
    msgsrv = [0., 0.]
    # msg0 = [b00, b01], msg1 = [b10, b11]
    msg0 = fl_cent_client_processing(localData, [X_train_0, y_train_0], msgsrv)
    msg1 = fl_cent_client_processing(localData, [X_train_1, y_train_1], msgsrv)
    ''' This block of code from the function seq_horizontal_federated() is replaced with the next block of code.
    b0 = (b00 + b10)/2.
    b1 = (b01 + b11)/2.
    '''
    msgs = [msg0, msg1]
    avg_model = fl_cent_server_processing(None, msgs)
    b0 = avg_model[0]
    b1 = avg_model[1]
    print(f"Training on two halves of records, iteration block by iteration block: b0={b0}, b1={b1}")
    # epochs=300, b0=-0.8455539121726542, b1=0.1752408762629523, Accuracy = 0.9  - This is similar and a little better   
    
    y_pred, accuracy = evaluate(X_test, y_test, b0, b1)
    print(f"Accuracy = {accuracy}")
    
    refbs = seq_horizontal_federated()
    assert refbs[0] == b0 and refbs[1] == b1, "b0 and b1 must be equal to ref_b0 and ref_b1, respectively!"

# localData = [locb0, locb1], privateData = [X_train, y_train], msg = [srvb0, srvb1]
def fl_cent_client_processing(localData, privateData, msg):
    X_train = privateData[0]
    y_train = privateData[1]
    b0 = msg[0]
    b1 = msg[1]
    b0, b1 = logistic_regression(X_train, y_train, b0, b1)
    return [b0, b1]

# msgs = [[b00, b01], [b10, b11], ...]. In bij: i - partion (or client) index, j - coefficent index.
def fl_cent_server_processing(privateData, msgs):
    b0 = 0.; b1 = 0.
    for lst in msgs:
        b0 = b0 + lst[0]
        b1 = b1 + lst[1]
    b0 = b0 / len(msgs)
    b1 = b1 / len(msgs)
    return [b0, b1]

from ptbfla_pkg.ptbfla import *

#   Run this example (after: cd src/examples): launch example4_logistic_regression.py 3 id 2
def main():
    # Parse command line arguments
    if len(sys.argv) != 4:
        # Args: noNodes nodeId flSrvId
        #   noNodes - number of nodes, nodeId - id of a node, flSrvId - id of the FL server
        print('Program usage: python example4_logistic_regression.py noNodes nodeId flSrvId')
        print('Example: noNodes==3, nodeId=0..2, flSrvId==2, i.e. 3 nodes (id=0,1,2), server is node 2:')
        print('python example4_logistic_regression.py 3 0 2',
              '\npython example4_logistic_regression.py 3 1 2\npython example4_logistic_regression.py 3 2 2')
        exit()
    
    # Process command line arguments
    noNodes = int( sys.argv[1] )
    nodeId = int( sys.argv[2] )
    flSrvId = int( sys.argv[3] )
    print(noNodes, nodeId, flSrvId)
    
    # Load the data (data has 400 records).
    data = pd.read_csv("Social_Network_Ads.csv")
    
    # Divide the data to training set and test set. For reproducible set random_state=42.
    # X_train and y_train have 320 records each, whereas X_test and y_test have 80 records each.
    X_train, X_test, y_train, y_test = train_test_split(data['Age'], data['Purchased'], test_size=0.20, random_state=42)
    
    # Split X-train (320 records) in two halves X_train_0 and X_train_1 (160 records each)
    X_train_0 = X_train.iloc[:160]
    X_train_1 = X_train.iloc[160:]
    y_train_0 = y_train[:160]
    y_train_1 = y_train[160:]
    
    # Start-up: create PtbFla object
    ptb = PtbFla(noNodes, nodeId, flSrvId)
    
    # Set local data (initial model) with b0=0., b1=0.
    lData = [0., 0.]
    
    # Set private data (training data for the clients and None for the server)
    if nodeId == 0:
        pData = [X_train_0, y_train_0]
    elif nodeId == 1:
        pData = [X_train_1, y_train_1]
    else:
        pData = None
    
    # Call fl_centralized with noIterations = 1
    ret = ptb.fl_centralized(fl_cent_server_processing, fl_cent_client_processing, lData, pData, 1)
    print('the final localData =', ret)
    
    b0 = ret[0]; b1 = ret[1]
    print(f"PTB-FLA training on two halves, iteration block by block: b0={b0}, b1={b1}")
    y_pred, accuracy = evaluate(X_test, y_test, b0, b1)
    print(f"Accuracy = {accuracy}")
    
    # Must be
    if nodeId == flSrvId:
        refbs = seq_horizontal_federated()
        assert refbs[0] == b0 and refbs[1] == b1, "b0 and b1 must be equal to ref_b0 and ref_b1, respectively!"
    
    # Shutdown
    del ptb
    pkey = input('press any key to continue...')
    

if __name__ == '__main__':
    #seq_base_case()
    #seq_horizontal_federated()
    #seq_horizontal_federated_with_callbacks()
    main()
