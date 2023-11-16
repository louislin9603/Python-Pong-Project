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
gameStateLock = threading.Lock()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

def handle_client(clientSocket, Paddle, shutdown):

    print("Made it to 1")
    while not shutdown.is_set():
        msg = clientSocket.recv()

        if msg is None:
            print('Error: No client message')
            shutdown.set()
            continue
        
        if msg['key'] == 'middleClient':
        
            # Compare the msg['sync'] against gameState['sync']
            # If msg['sync'] is greater than gameState['sync'] then:
            # Update the Ball, Score

            if msg['sync'] > gameState['sync']:
                with gameStateLock:
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
                clientSocket.sendall(json.dumps(gameState).encode())
            except Exception as e:
                print(f"Could not send the frame update to the client: {e}")



        #if request is start
        if msg['key'] == 'start':

            # Set the left and right as ready (depending on which one they are)
            # If both left and right are ready then return a start as 'True'
            # otherwise return 'False' in the send back          
            
            #what is going to happen is that the client is spam requesting to start,
            # when both are ready to start, then we can return True

            #gameState["ready"]["left] = True
            


            #if left and right are ready
            if (gameState["ready"]["left"] and gameState["ready"]["right"]):
            
                #send True
                with gameStateLock:
                    gameState["ready"]["left"] = True
                    gameState["ready"]["right"] = True
                clientSocket.send(json.dumps(gameState).encode())
            else:

                #send False
                clientSocket.send(json.dumps(gameState).encode())



# Start server
def initalize_server():

    serverIP = "10.113.33.94"
    port = 12321

    try:
            # Create a socket for the server
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            print("Server started. Waiting on clients...")

            # Bind to the port
            server.bind((serverIP, port))
            server.listen()
            print(f"Listening on {serverIP}: {port}")     #Waiting for connections

            #Initalize player(s)
            noOfClients = 0             #number of clients connected
            paddleHolder = "left"

            threadHolder = []
            while noOfClients < 2:
                # Accepts a client from the connection
                clientSocket, clientAddress = server.accept()

                print(f"Accepted connection from {clientAddress[0]}:{clientAddress[1]}")

                

                # Determine current player paddle position
                if noOfClients == 1:        #Player 1
                    paddleHolder = "left"
                elif noOfClients == 2:      #Player 2
                    paddleHolder = "right"
                #else:
                    #more than two players, maybe have them wait without crashing

                
                data = {
                    "screenheight": 400,
                    "screenwidth": 600,
                    "playerPaddle": paddleHolder
                    }

                try:
                    initialData = json.dumps(data)
                    clientSocket.sendall(initialData.encode())
                except Exception as e:
                    print(f"Could not send data as JSON: {e}")

                # Create a thread for multiple clients
                shutdown = clientSocket.set()       #This line may not work, delete if crashing randomly
                client_handler = threading.Thread(target=handle_client, args=(clientSocket, paddleHolder, shutdown,))
                client_handler.start()
                threadHolder.append(client_handler)
                noOfClients += 1        #increase client[i]

            server.close()
            for client in threadHolder:
                client.join() 
    except Exception as e:
        print(f"error with initializing server: {e}")
    finally:
        server.close()
        clientAddress.close()
        print("Server closing")


if __name__ == "__main__":
   
    # Initalize server
    try:
        initalize_server()
    except KeyboardInterrupt: 
        print("Ctrl C - Stopping Server")
        sys.exit(1)



