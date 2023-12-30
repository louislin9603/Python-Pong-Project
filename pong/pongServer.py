# =================================================================================================
# Contributing Authors:	    Isaiah Huffman, Louis Lin, Gyunghyun Moon
# Email Addresses:          irhu224@uky.edu, lli241@uky.edu, gmo239@uky.edu
# Date:                     11/17/2023
# Purpose:                  This is the server code file. Host the server using this, feed the connecting clients appropriate information.
# Misc:                     For this code to work, you must determine your IP address (more info in initialize_server() 
#                           and manually type it into the serverIP string on line 125
# =================================================================================================


import socket
import threading
import sys
import json


# Global dictionary that our two clients access. All the information of the game frame is stored here.
gameState = {
    "left": {
        "Y":0,
        "Moving":"",
    },
    "right": {
        "Y":0,
        "Moving":"",
    },
    "score": {
        "lScore":0,
        "rScore":0,
    },
    "ball": {
        "X":0,
        "Y":0,
    },
    "ready": {
        "left": False,
        "right": False,
    },
    "sync":0
}

# Our thread lock, which we use to prevent unnecessary nonsense from happening when our threaded clients try...
# ...and access the global dictionary gameState, whose initialization is located above.
gameStateLock = threading.Lock()        



# Author:        Isaiah Huffman and Louis Lin and Gyunghyun Moon
# Purpose:       Threaded function that enables the server to handle both clients at once.
# Pre:           This function expects that both clients are connected to the server. 
# Post:          The server shuts down after this function is over; the only post-condition is that the...
                 #...users had fun
def handle_client(clientSocket:socket.socket, Paddle:str, shutdown:threading.Event, readyClients:list[socket.socket]) -> None:

    print(f"Ready Clients: {readyClients}")
    print(f"Paddle: {Paddle}")
    while not shutdown.is_set():

        #Pull message from client, read it.
        data = clientSocket.recv(1024)
        msg = json.loads(data.decode())
        
        # If no message, let the server know, because it's a problem.
        if msg is None:
            print('Error: No client message')
            shutdown.set()          
            continue
    
        
        # If the key in the received JSON file indicates that the client is in the middle of its functional loop
        if msg['key'] == 'middleClient':
        
            # Compare the msg['sync'] against gameState['sync']
            # If msg['sync'] is greater than gameState['sync'] then:
            # Update the Ball, Score

            if msg['sync'] > gameState['sync']:
                with gameStateLock:
                    gameState["sync"] = msg["sync"]
                    gameState["ball"]["X"] = msg["BallX"]
                    gameState["ball"]["Y"] = msg["BallY"]
                    gameState["score"]["lScore"] = msg["lScore"]
                    gameState["score"]["rScore"] = msg["rScore"]

            
            # Irrespective if sync is greater or not, update the paddle info
            with gameStateLock:
                gameState[Paddle]["Y"] = msg["PaddleY"]     #update your paddle position
                gameState[Paddle]["Moving"] = msg["paddleYMoving"] #update where you are moving it to
        
        # If the client wants to quickly grab the gamestate.
        if msg['key'] == 'grab':
        
            # send back the gameState
            # Continue
            try:
                updateData = json.dumps(gameState)
                clientSocket.send(updateData.encode())
            except Exception as e:
                print(f"Could not send the frame update to the client: {e}")


        # If the clients are asking to start the game
        if msg["key"] == "ready":

            
            readyClients.append(clientSocket)   # Add the client that says its ready into an array
            if len(readyClients) == 2:          # If we have two clients connected
                for client in readyClients:     # Send the clients the "you're good to start" message
                    client.send(json.dumps({"key":"startGame"}).encode())
            


# Author:        Isaiah Huffman and Louis Lin
# Purpose:       Start the server, listen for clients to connect. Begin the game (the game is handled in handle_client, above)
# Pre:           It expects the user will input the IP address on the first try. Also, only two clients can connect.
# Post:          Threads and calls the function (handle_client) that actually deals with the gameloop of the client.

# Start server
def initialize_server() -> None:

    # IMPORTANT, whoever is hosting the server needs to understand their IP address and put it into this string here.
    # We pulled our IP addresses by going into (Windows 10) command prompt and typing "ipconfig/all"
    # We only ever used IPv4 address.
    serverIP = "10.113.33.94"
    port = 12321

    try:
            # Create a socket for the server
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            print("Server started. Waiting on clients...")

            # Bind to the port
            server.bind((serverIP, port))
            server.listen(2)
            print(f"Listening on {serverIP}: {port}")     #Waiting for connections

            #Initalize player(s)
            noOfClients = 0             #number of clients connected
            paddleHolder = "left"       #What side the user is on

            threadHolder = []           #place clients into here to iteratively close when done
            readyClients = []           #array of clients that are ready

            # Loop where we connect to the two clients.
            while noOfClients < 2:

                # Accepts a client from the connection
                clientSocket, clientAddress = server.accept()
                print(f"Accepted connection from {clientAddress[0]}:{clientAddress[1]}")

                # Determine current player paddle position
                if noOfClients == 0:        #Player 1
                    paddleHolder = "left"
                elif noOfClients == 1:      #Player 2
                    paddleHolder = "right"
                
                
                #JSON that holds the initial data to send to the clients
                data = {
                    "screenheight": 400,
                    "screenwidth": 600,
                    "playerPaddle": paddleHolder,
                    "key": "initialData" 
                    }

                #Send initial data to the client
                try:
                    initialData = json.dumps(data)
                    clientSocket.sendall(initialData.encode())
                except Exception as e:
                    print(f"Could not send initial data to client: {e}")
                
                # Passed to the client handler, enables us to shutdown if funny business happens with the threads
                shutdown = threading.Event()
                print(f"shutdown: ")
                print(type(shutdown))
                # Use threads to enable server to handle both clients simultaneously.
                client_handler = threading.Thread(target=handle_client, args=(clientSocket, paddleHolder, shutdown, readyClients))
                client_handler.start()
                threadHolder.append(client_handler)     # add client to array threadHolder
                noOfClients += 1                        # increment number of clients

            # "We're done here, shut it down and let's go home."
            # Close the server and the client sockets.
            server.close()
            for client in threadHolder:
                client.join() 
    except Exception as e:
        print(f"error with initializing server: {e}")
    finally:
        server.close()
        print("Server closing")



# What actually starts the server
if __name__ == "__main__":
   
    # Initalize server
    try:
        initialize_server()
    except KeyboardInterrupt: 
        print("Ctrl C - Stopping Server")
        sys.exit(1)



