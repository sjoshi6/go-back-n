
import socket
import sys

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
MESSAGE = "Amey Atul Patwardhan!"
FTP_FILE_NAME = sys.argv[3]
WINDOW_SIZE = int(sys.argv[4])
MSS = sys.argv[5]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE.encode('utf-8'), (SERVER_IP, SERVER_PORT))
