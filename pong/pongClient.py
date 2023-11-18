# =================================================================================================
# Contributing Authors:	    Isaiah Huffman, Louis Lin, Gyunghyun Moon
# Email Addresses:          irhu224@uky.edu, lli241@uky.edu, gmo239@uky.edu
# Date:                     11/17/2023
# Purpose:                  This is the client code file. Connect to the server and run the game loop.
# Misc:                     Do not be shocked by the sync number spamming your terminal while playing the game. We're proud of it.
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import json
import time
import threading

from assets.code.helperCode import *

# Author:        Isaiah Huffman and Louis Lin and Gyunghyun Moon
# Purpose:       Main gameplay loop that hosts the game logic and communicates with server (send and pull paddle/ball location, etc.)
# Pre:           Must have already established connection with server.
# Post:          This is the final function users enter; the game ends after this.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Give the users a couple seconds to process that the game is about to start.
    time.sleep(2)
    print("Game is starting")
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    winMessage = pygame.Rect(0,0,0,0)
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    oppPaddleDirection = "left"
    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
        oppPaddleDirection = "right"
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0

    while True:

        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        
        #Getting the current paddle information and sending it to the server
        try:
            key = "middleClient"        #Cause we're in the middle of the client
            update_data = {
                #player paddle
                "PaddleY": playerPaddleObj.rect.y,
                "paddleYMoving": playerPaddleObj.moving,

                #ball location
                "BallX": ball.rect.x,
                "BallY": ball.rect.y,

                #Score
                "lScore": lScore,
                "rScore": rScore,

                "key": key,

                #current sync number
                "sync": sync
                }
        except:
            print("Could not pull paddle information to send to server, its FUBAR")
        
        #Send our game information to the server
        try:
            updateData = json.dumps(update_data)
            client.send(updateData.encode())
        except Exception as e:
            print(f"Could not send data as JSON to server: {e}")

    
        
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        #Test2

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
        else:

            # ==== Ball Logic =====================================================================
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)

        #pygame.display.update([topWall, bottomWall, ball, leftPaddle, rightPaddle, scoreRect, winMessage])
        pygame.display.update()
        #pygame.display.flip()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        
        #You can comment this out, it was nice to have as a debugging tool though. Also satisfying.
        print(f"{sync}")
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game
        try:
            
            
            # Request to receive update from the server, but simultaneously send our game state as well.
            key = "grab"
            update_data = {
               #player paddle
                "PaddleY": playerPaddleObj.rect.y,
                "paddleYMoving": playerPaddleObj.moving,

                #ball location
                "BallX": ball.rect.x,
                "BallY": ball.rect.y,

                #Score
                "lScore": lScore,
                "rScore": rScore,

                "key": "grab",

                #current sync number
                "sync": sync
                }
            
            # Send out the game state
            try:
                updateServer = json.dumps(update_data)
                client.send(updateServer.encode())
            except Exception as e:
                print("Could not send the grab request to the server: {e}")
           
            # Wait for server response with most updated game state
            try: 
                msg = client.recv(1024)
                updateData = json.loads(msg.decode())
            except Exception as e:
                print(f"Could not retrieve information from key grab: {e}")

            # Update game state (if necessary) with info from server
            if updateData["sync"] >= sync:
                ball.rect.x = updateData["ball"]["X"]
                ball.rect.y = updateData["ball"]["Y"]
                sync = updateData["sync"]
                lScore = updateData["score"]["lScore"]
                rScore = updateData["score"]["rScore"]
                
            # Regardless of whether or not our sync is lower, update enemy game paddle
            opponentPaddleObj.rect.y = updateData[oppPaddleDirection]["Y"]
            opponentPaddleObj.moving= updateData[oppPaddleDirection]["Moving"]
        


        except Exception as e:
            print(f"Error receiving server update: {e}")
        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which


# Authors:       Isaiah Huffman and Louis Lin and Gyunghyun Moon (based off code given by our wonderful TA Alexander Barrera)
# Purpose:       Establish connection with the server
# Pre:           User must have input the correct server IP and port into the GUI that popped up.
# Post:          Go into the main gameplay loop.
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:    
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best

    serverIP = ip

    #Create a socket and connect to the server, information pulled from arguments passed onto function (user puts in IP info in GUI popup)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((serverIP, int(port)))
        print(f"A connection has been made with IP: {serverIP}:{port}")
          
    except Exception as e:
        print(f"Error with connection: {e}")
        # Update the errorLabel widget with an error message
        error_message = f"Some update text. You input: IP: {serverIP}, Port: {port}"
        errorLabel.config(text=error_message)
        errorLabel.update_idletasks()  # Update the label without waiting for events

    # Get the required information from your server (screen width, height & player paddle, "left or right")
    try:
        data = client.recv(1024)
        initialData = json.loads(data.decode())

        #Server sends us initial data. We only expect to be sent the initial data by this point.
        if initialData["key"] == "initialData":
            screenHeight = initialData["screenheight"]
            screenWidth = initialData["screenwidth"]
            playerPaddle = initialData["playerPaddle"] 
            print(f"Retrieved initial data.")
        else:
            print(f"Client expected to be sent the initial data, instead got something else.")

    except Exception as e:
        print(f"Could not pull the initial data from the server, error: {e}")

    #Notify the server that the client is ready to play
    client.send(json.dumps({"key": "ready"}).encode())

    #Wait for both clients to be ready
    try:
        while True:
            data = client.recv(1024)
            message = json.loads(data.decode())
            if message["key"] == "startGame":
                break
    except Exception as e:
        print(f"Error waiting for both clients: {e}")
    
    # Close this window and start the game with the info passed to you from the server    
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(screenWidth, screenHeight, playerPaddle, client)  # User will be either left or right paddle
    print("Disconnected")
    app.quit()         # Kills the window

   
    



# This displays the opening screen, you don't need to edit this (but may if you like)
# This function was given, the only thing we modified is the join button (it's now threaded) so it doesn't crash.
def startScreen() -> threading:
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    # I found that if I didn't thread this, then the join button would crash.
    button_handler = threading.Thread(target=joinGame, args=(app, ipEntry, portEntry, errorLabel))
    button_handler.start()   
     
    app.mainloop()   


# Author:        Louis Lin and Gyunghyun Moon
# Purpose:       "Spawn" the join button on the user's screen so they can type in the server IP address and port
# Pre:           User must have internet connection, must know the server IP address and port, probably needs to be connected to UK VPN 
# Post:          User has GUI join button pop up that prompts them for IP address and port.
def joinGame(app:tk.Tk, ipEntry:str, portEntry:str, errorLabel:tk.Label) -> None:
    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2) 

if __name__ == "__main__":
    startScreen()

    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))