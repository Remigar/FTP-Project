def receive_message(sock, size):
	result = ""
	tmpBuffer = ""
	while len(result) != size:
		tmpBuffer = sock.recv(size)
		if not tmpBuffer:
			return -1
		result += tmpBuffer
	return result

def send_message(sock, msg, size):
	#make sure the message is the right size; pad if it isn't
	if len(msg) < size:
		msg += ' ' * (size - len(msg))
	bytes_sent = 0
	while bytes_sent < size:
		bytes_sent += sock.send(msg[bytes_sent:])

def send_file(sock, filename, size):
	bytes_sent = 0
	f = open(filename, 'r')
	while bytes_sent < size:
		temp = f.read(4096)
		bytes_sent += sock.send(temp)

	f.close()
	return bytes_sent
def receive_file(sock, filename, size):
	f = open(filename, 'w')
	bytes_received = 0
	temp = ""
	rcvBuff = ""
	while len(rcvBuff) < size:
		temp = sock.recv(size)
		if not temp:
			break
		rcvBuff += temp
		bytes_received += len(temp)

	f.write(rcvBuff)
	f.close()
	return bytes_received
