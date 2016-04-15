import socket
import sys
from random import uniform

SERVER_IP = "localhost"
SERVER_PORT = int(sys.argv[1])
FILE_NAME = sys.argv[2]
PL_PROB = sys.argv[3]


def prob_random_generator():
	result=uniform(0,1)
	print (result)




server_socket= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

try:
	server_socket.bind((SERVER_IP,SERVER_PORT))
	print ("SERVER LISTENING ON PORT 7735")
except socket.error as msg:
	print (msg)
	sys.exit()

while 1:
	info,addr = server_socket.recvfrom(1024)
	print ('Peer connected  ' + addr[0] + ':' + str(addr[1]))
	print (info)
	prob_random_generator()
s.close()
