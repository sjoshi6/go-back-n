import socket
import sys
import pickle
from random import uniform
from settings import *

SERVER_IP = "localhost"
SERVER_PORT = ""
FILE_NAME = ""
PL_PROB = ""


def prob_random_generator():

    result = uniform(0, 1)
    print(result)

    return result


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        print("SERVER LISTENING ON PORT "+str(SERVER_PORT))

        while True:

            data, addr = server_socket.recvfrom(1024)

            # Extract client port details
            client_ip = addr[0]
            client_port = addr[1]
            client_ack_port = int(client_port) + 1

            packet = pickle.loads(data)
            print(packet["data"])

            ack = {"header": {}}
            ack["header"]["data_type"] = int('0101010101010101', 2)
            ack["header"]["bit_field"] = int('0000000000000000', 2)
            ack["header"]["ack_number"] = packet["header"]["sequence_number"]

            randm = prob_random_generator()

            if randm > PL_PROB:
                print("Discarded this packet")
            else:
                # Send the data and close this connection
                server_socket.sendto(pickle.dumps(ack), (client_ip, client_ack_port))

    except socket.error as msg:
        print(msg)
        sys.exit(1)

    finally:
        server_socket.close()
        sys.exit(1)

if __name__ == "__main__":

    SERVER_PORT = int(sys.argv[1])
    FILE_NAME = sys.argv[2]
    PL_PROB = float(sys.argv[3])
    main()
