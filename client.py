import sys
import os
import commands
from socket import *

from send_receive_funcs import *




MAX_MESSAGE_SIZE = 128
ACK_MESSAGE_SIZE = 32

serverPort = int(sys.argv[2]) #Port is supplied from the command line
serverName = sys.argv[1]


clientSocket = socket(AF_INET, SOCK_STREAM) #control socket

clientSocket.connect((serverName, serverPort))


while 1:
	#start a data transfer socket with an ephemeral port
	clientDataSocket = socket(AF_INET, SOCK_STREAM)
	clientDataSocket.bind(('', 0))
	#get the ephemeral port
	serverDataPort = int(clientDataSocket.getsockname()[1])

	#read from the command line
	command = raw_input("ftp>")
	command += " " + str(serverDataPort)
	command_tokenized = command.split()
	if len(command_tokenized) == 0:#user didnt enter anything
		continue

	if command_tokenized[0] == "lls": #doesn't require any interaction with the server
		for line in commands.getstatusoutput('ls -l'):
			print (line)

	elif command_tokenized[0] == "get":
		if len(command_tokenized) != 3: #user didn't enter command correctly
			print ("format: get <filename>")
			continue

		send_message(clientSocket, command, MAX_MESSAGE_SIZE)
		response = receive_message(clientSocket, ACK_MESSAGE_SIZE)
		response_tokenized = response.split()

		print (response_tokenized[0])
		if response_tokenized[0] == "NACK":
			print ("File not found")
		else:
			bytes = int(response_tokenized[1])

			#start listening for the server
			clientDataSocket = socket(AF_INET, SOCK_STREAM)
			clientDataSocket.bind(('', serverDataPort))
			clientDataSocket.listen(1)
			#:send another control message saying that we're listening
			listenMsg = "ACK"
			send_message(clientSocket, listenMsg, ACK_MESSAGE_SIZE)

			dataStreamSocket, addr = clientDataSocket.accept()

			print ("Downloading {} bytes...".format(bytes))
			byte_get = receive_file(dataStreamSocket, command_tokenized[1], bytes)
			print ("got {} bytes...".format(byte_get))
			#send a message to the server, saying we have the file
			send_message(clientSocket, listenMsg, ACK_MESSAGE_SIZE)

			dataStreamSocket.close()
			clientDataSocket.close()

	elif command_tokenized[0] == "put":
		if len(command_tokenized) != 3:
			print ("format: put <filename>")
			continue
		if not os.path.exists(str(command_tokenized[1])):
			print ("file does not exist")
			continue
		#add on the number of bytes to be sent
		bytes = os.path.getsize(command_tokenized[1])
		command += ' ' + str(bytes)

		send_message(clientSocket, command, MAX_MESSAGE_SIZE)

		response = receive_message(clientSocket, ACK_MESSAGE_SIZE)
		print (response).rstrip()
		if str(response).rstrip() == "NACK":
			print("file already exists")
			continue
		else:


			#listen for the server to connect via data port
			print serverDataPort
			clientDataSocket = socket(AF_INET, SOCK_STREAM)
			clientDataSocket.bind(('', serverDataPort))
			clientDataSocket.listen(1)

			#:send another control message saying that we're listening
			listenMsg = "ACK"
			send_message(clientSocket, listenMsg, ACK_MESSAGE_SIZE)

			dataStreamSocket, addr = clientDataSocket.accept()
			print("Sending {}, {} bytes...".format(command_tokenized[1], bytes))

			bytes_sent = send_file(dataStreamSocket, command_tokenized[1], bytes)

			print("Sent {} bytes.".format(bytes_sent))
			dataStreamSocket.close()
			clientDataSocket.close()

	elif command_tokenized[0] == "ls":
		send_message(clientSocket, command, MAX_MESSAGE_SIZE)
		response = receive_message(clientSocket, ACK_MESSAGE_SIZE)
		response_tokenized = response.split()
		print (response_tokenized[0])
		bytes = int(response_tokenized[1])

		#start listening for the server
		clientDataSocket = socket(AF_INET, SOCK_STREAM)
		clientDataSocket.bind(('', serverDataPort))
		clientDataSocket.listen(1)

		#get the ls output from the server
		dataStreamSocket, addr = clientDataSocket.accept()

		ls = receive_message(dataStreamSocket, bytes)

		dataStreamSocket.close()
		clientDataSocket.close()
		print ls


	elif command_tokenized[0] == "quit":
		send_message(clientSocket, command, MAX_MESSAGE_SIZE)
		response = receive_message(clientSocket, ACK_MESSAGE_SIZE)
		clientSocket.close()
		break

	else:
		print("command not recognized\n")


clientSocket.close()
