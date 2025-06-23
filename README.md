# Python-Pong-Project
2D Singleplayer or Multiplayer Pong game using Socket programming TCP client/server \
Note: Ensure git, python, and pip3 are properly installed 

## Creating and Running
Go to a desired folder

```
git clone git@github.com:louislin9603/Python-Pong-Project.git
cd .\Python-Pong-Project\
pip3 install -r requirements.txt
```

============

Group Members:

    Isaiah Huffman 
    Louis Lin      
    Gyunghyun Moon 


Versioning
==========

Github Link: https://github.com/louislin9603/Python-Pong-Project/

General Info
============
- Users should connect to the UKY VPN before trying to host the client or server.
- Whoever runs the server must change line 125 of pongServer.py so that it reflects their IP address.
- For best results, have the server be ran on a different computer than either of the clients.

Install Instructions
====================

Run the following line to install the required libraries for this project:

`pip3 install -r requirements.txt`

Known Bugs
==========
- Synchronization issues may occur depending on the connection speed and device.
- If the player runs the client code and does not input the server’s IP address and port accurately, the client code will crash.
- Say client 1 is the first client to connect to the server. If client 1’s process stops before the second client has the opportunity to join, then the server will break and must be reset.


=======
### Result of the pip3
```bash
Collecting pygame==2.5.2 (from -r requirements.txt (line 1))
  Downloading pygame-2.5.2-cp312-cp312-win_amd64.whl.metadata (13 kB)
Downloading pygame-2.5.2-cp312-cp312-win_amd64.whl (10.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.8/10.8 MB 10.1 MB/s eta 0:00:00
Installing collected packages: pygame
Successfully installed pygame-2.5.2
```
