from socket import *
import sys
import commands
import os

import send_receive_funcs


MAX_MESSAGE_SIZE = 128 #maximum size for a control message
ACK_MESSAGE_SIZE = 32 #maximum size for an ACK message

serverPort = int(sys.argv[1])


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

#accept connection for control
connectionSocket, addr = serverSocket.accept()

while 1:
	#get a message from the client

	command = receive_message(connectionSocket, MAX_MESSAGE_SIZE)
	command_tokenized = command.split()

	if len(command_tokenized) == 2: #the command received is a ls or quit command
		serverDataPort = int(command_tokenized[1])
	else:
		serverDataPort = int(command_tokenized[2])

	if command_tokenized[0] == "get":

		if not os.path.exists(command_tokenized[1]): #the file is not found, tell the client
			response_msg = "NACK"
			send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)
			print ("GET: FAILURE")
			continue
		else:
			bytes = os.path.getsize(command_tokenized[1])#get the file size in bytes
			response_msg = "ACK" + " " + str(bytes)
			send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)

			#receive another message telling the server the client is listening
			response = receive_message(connectionSocket, ACK_MESSAGE_SIZE)


			#connect to the client and send file
			serverDataSocket = socket(AF_INET, SOCK_STREAM)
			serverDataSocket.connect((addr[0], serverDataPort))

			send_file(serverDataSocket, command_tokenized[1], bytes)
			#get a message from the client, telling us they have the file
			response = receive_message(connectionSocket, ACK_MESSAGE_SIZE)

			serverDataSocket.close()

		print ("GET: SUCCESS")

	if command_tokenized[0] == "put":
		#the command message is going to have a 4th field for the number of bytes the client is going to send
		bytes = int(command_tokenized[3])
		if os.path.exists(str(command_tokenized[1])):#file exists already, send a NACK msg
			response_msg = "NACK"
		else:
			response_msg = "ACK"
			send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)

			#receive another message telling the server the client is listening
			response = receive_message(connectionSocket, ACK_MESSAGE_SIZE)

			#initiate connection to client via data port
			serverDataSocket = socket(AF_INET, SOCK_STREAM)
			serverDataSocket.connect((addr[0], serverDataPort))
			print ("Ready to receive")
			receive_file(serverDataSocket, command_tokenized[1], bytes)
			serverDataSocket.close()
			print ("PUT: SUCCESS")

		if response_msg == "NACK":
			print("PUT: FAILURE")
			send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)
			continue

	if command_tokenized[0] == "ls":
		data = ""
		for line in commands.getstatusoutput('ls -l'):
			data += str(line)
		bytes = len(data)
		#send an "ACK" to the client with the number of bytes to be received
		response_msg = "ACK" + " " + str(bytes)
		send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)

		serverDataSocket = socket(AF_INET, SOCK_STREAM)
		serverDataSocket.connect((addr[0], serverDataPort))

		send_message(serverDataSocket, data, bytes)

		serverDataSocket.close()

		print ("LS: SUCCESS")

	elif command_tokenized[0] == "quit":
		response_msg = "ACK"
		send_message(connectionSocket, response_msg, ACK_MESSAGE_SIZE)
		print ("QUIT: SUCCESS")
		break





connectionSocket.close()
serverSocket.close()
