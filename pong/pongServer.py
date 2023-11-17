# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
import sys
import json
import uuid

# Global dictionary that our two clients access.
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



def handle_client(clientSocket, Paddle, shutdown, readyClients):

    print(f"Ready Clients: {readyClients}")
    print(f"Paddle: {Paddle}")
    while not shutdown.is_set():
        data = clientSocket.recv(1024)

        #parse thoruhg received message
        msg = json.loads(data.decode())
        
        #if no message, break out of loop
        if msg is None:
            print('Error: No client message')
            shutdown.set()          
            continue
    
        
        #if message received by client == key (middleClient, start, or grab)
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
            # Continue
            #I need to figure out how to determine how to interpret paddle data so I put it in the right spot
            with gameStateLock:
                gameState[Paddle]["Y"] = msg["PaddleY"]     #update your paddle position
                gameState[Paddle]["Moving"] = msg["paddleYMoving"] #update where you are moving it to
        
        #if request is send
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

        
            readyClients.append(clientSocket)
            if len(readyClients) == 2:
                for client in readyClients:
                    client.send(json.dumps({"key":"startGame"}).encode())
            



# Start server
def initialize_server():

    # IMPORTANT, whoever is hosting the server needs to understand their IP address and put it into this string here.
    # We pulled our IP addresses by going into (Windows 10) command prompt and typing "ipconfig/all"
    # We only ever used IPv4 address.
    serverIP = "10.113.33.94"
    port = 12321

    try:
            # Create a socket for the server
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
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



