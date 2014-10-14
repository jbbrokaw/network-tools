network-tools
=============

* echo_server.py can be run from the command line (as "./echo_server.py > log.txt &" if you do not want to run it in a separate terminal) to listen for connections on 127.0.0.1:50000
* client_server.py can be run with a message argument (as "./echo_client.py 'message'") to send a message to that server
* The server will echo back the message, and client will print the response to stdout
