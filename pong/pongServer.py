# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

#Function that is called for each client that is logged in
#Handles the information received and sent
def handleClient(client, address):

    #The below "try" sequence is to pull the playerPaddle location, the ball, and the score from the client
    try:
        while True:
            # receive and print client messages
            data = client.recv(1024).decode()

            try:
                playerPaddleObj, ball, lScore, rScore = map(int, data.split(','))
                print(f"Received data - Player Paddle Object: {playerPaddleObj}, Ball: {ball}, lScore: {lScore}, rScore: {rScore}")
            except ValueError:
                print("Received data is in an incorrect format")

            

    except Exception as e:
        print(f"Error when handling client: {e}")
    finally:
        client.close()
        print(f"Connection to client ({address[0]}:{address[1]}) closed")


#Makes initial
def run_server():
    server_ip = "10.113.33.94" #Assuming Isaiah Huffman hosting
    port = 12321               #Let's just use this port

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server.bind((server_ip, port)) #connect to local socket on server laptop
        server.listen(2) #specify we want 2 clients to be speaking to this server
        print(f"Listening on {server_ip}:{port}")

        while True:

            client_socket, address = server.accept() #establishing connection with client
            print(f"Accepted connection from {address[0]}:{address[1]}")
        
            #Launch a thread to process each client
            thread = threading.Thread(target=handleClient, args=(client_socket, address,))
            thread.start()
    except Exception as e:
            print(f"Error: {e}")
    finally:
            server.close()


        


run_server()