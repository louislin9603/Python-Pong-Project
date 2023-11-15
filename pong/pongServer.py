# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
import select
import sys
import json
import time
import uuid

gameState = {}
gameStateLock = threading.Lock()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games


# Focused on a single client
def handle_client(clientSocket, clientAddress):
    global gameState, gameStateLock
    clientID = str(uuid.uuid4())
    print(f"Client ID for {clientAddress} is: {clientID}")

    with gameStateLock:
       gameState[clientID] = {'sync': 0, 'gameData': {}}

    try:
        while True:
            #Retrieve message from client
            try:
                message = clientSocket.recv(1024)
            except:
                print("Could not retrieve message from client")

            if not message:
                break

            #Pull updated data from client
            try:
                updateData = json.loads(message.decode())
                print("Got data from client")
            except Exception as e:
                print(f"There was an issue unloading update information from client: {e}")

          #Compare the syncs here
          #Establish which sync is most updated, then take the gameData of the updated sync and ship them out

            try:
                with gameStateLock:
                    # Update this client's state
                    gameState[clientID]['sync'] = updateData['sync']
                    gameState[clientID]['gameData'] = updateData
            except:
                print("Failure updating gameData and sync")
            
            # Compare sync values
            try:
                other_client_id = [id for id in gameState if id != clientID][0]  # Assuming only two clients
            except:
                print("The line that I didn't think would work didn't work")

            try:
                    if gameState[clientID]['sync'] < gameState[other_client_id]['sync']:
                        # This client is lagging, send it the most updated data
                        serverUpdate = gameState[other_client_id]['gameData']
                        print(f"most_recent_data: {serverUpdate}")
                        clientSocket.sendall(json.dumps(serverUpdate).encode())
            except:
                print("Failure determining game sync and sending it to clients")
        
    except Exception as f:
      print(f"error with handling client: {f}")
    finally:
        clientSocket.close()
        print(f"Connection to client {clientAddress[0]} closed.")

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
            server.listen(5)
            print(f"Listening on {serverIP}: {port}")     #Waiting for connections

            #Initalize player(s)
            noOfClients = 0             #number of clients connected
            paddleHolder = "left"

            while True:
                # Accepts a client from the connection
                clientSocket, clientAddress = server.accept()

                print(f"Accepted connection from {clientAddress[0]}:{clientAddress[1]}")

                noOfClients += 1        #increase client[i]

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
                client_handler = threading.Thread(target=handle_client, args=(clientSocket, clientAddress,))
                client_handler.start()        
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



