import socket
import threading


def cnctserverTest():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "10.113.33.94"
    port = 12321
    client.connect((server_ip, port)) #Connect to server
    try:

        while True:
            #input message and send it to the server
            msg = input("Enter message: ")
            client.send(msg.encode())
    

            # receive message from the server
            response = client.recv(1024)
            response = response.decode()

            # if server sent us "closed" in the payload, we break out of the loop and close our socket
            if response.lower() == "closed":
                break

            print(f"Received: {response}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Connection to server closed")

cnctserverTest()
