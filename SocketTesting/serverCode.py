import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

def handle_client(client_socket, address):
    try:
        while True:
            # receive and print client messages
            request = client_socket.recv(1024).decode("utf-8")
            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            print(f"Received: {request}")
            # convert and send accept response to the client
            response = "accepted"
            client_socket.send(response.encode("utf-8"))
    except Exception as e:
        print(f"Error when hanlding client: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client ({address[0]}:{address[1]}) closed")



def run_server():
    server_ip = "10.113.33.94"
    port = 12321

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server.bind((server_ip, port)) #connect to local socket
        server.listen(5) #specify we want 2 clients to be speaking to this server
        print(f"Listening on {server_ip}:{port}")

        while True:

            client_socket, address = server.accept() #establishing connection with client
            print(f"Accepted connection from {address[0]}:{address[1]}")
        
            thread = threading.Thread(target=handle_client, args=(client_socket, address,))
            thread.start()
    except Exception as e:
            print(f"Error: {e}")
    finally:
            server.close()


        


run_server()