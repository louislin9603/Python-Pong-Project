# Python-Pong-Project
2D Singleplayer or Multiplayer Pong game using Socket programming TCP client/server

## Creating and Running
```bash
cd College/Python
git clone git@github.com:louislin9603/Python-Pong-Project.git
pip3 install -r requirements.txt
```


Contact Info
============

Group Members & Email Addresses:

    Isaiah Huffman [irhu224@uky.edu]
    Louis Lin      [lli241@uky.edu]
    Gyunghyun Moon [gmo239@uky.edu]


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
- The server doesn't work because the logic isn't yet written.
- The client doesn't speak to the server
- If the player runs the client code and does not input the server’s IP address and port accurately, the client code will crash.
- Say client 1 is the first client to connect to the server. If client 1’s process stops before the second client has the opportunity to join, then the server will break and must be reset.


