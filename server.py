import socket
import sys
import pickle
from random import uniform
from settings import *

SERVER_IP = ""
SERVER_PORT = ""
FILE_NAME = ""
PL_PROB = ""


def prob_random_generator():

    result = uniform(0, 1)

    return result


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def generate_checksum(msg):
    # Assume the msg block is even
    odd = False
    if 1 == len(msg) % 2:
        odd = True

    sumation = 0

    if odd:
        for i in range(0, len(msg), 1):
            w = ord('0') + (ord(msg[i]) << 8)
            sumation = carry_around_add(sumation, w)

    elif not odd:
        for i in range(0, len(msg), 2):
            w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
            sumation = carry_around_add(sumation, w)

    return ~sumation & 0xffff


def main():

    expected_seq_no = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        print("SERVER LISTENING ON PORT "+str(SERVER_PORT))

        while True:

            data, addr = server_socket.recvfrom(10000)

            # Extract client port details
            client_ip = addr[0]
            client_port = addr[1]
            client_ack_port = int(client_port) + 1

            packet = pickle.loads(data)
            randm = prob_random_generator()

            if randm <= PL_PROB:
                print("Packet is dropped due to to probability "+str(randm))

            elif randm > PL_PROB:
                if packet["header"]["fin"] == 1:

                    print("Fin packet received; resetting expected_seq_no to 0")
                    expected_seq_no = 0

                elif packet["header"]["fin"] == 0:
                    if packet["header"]["checksum"] == generate_checksum(packet["data"]):

                        if int(packet["header"]["sequence_number"]) == expected_seq_no:

                            print("Correct packet received with sequence number : "+str(packet["header"]["sequence_number"]))
                            #print("Data : "+ packet["data"])

                            ack = {"header": {}}
                            ack["header"]["data_type"] = int('0101010101010101', 2)
                            ack["header"]["bit_field"] = int('0000000000000000', 2)
                            ack["header"]["ack_number"] = packet["header"]["sequence_number"]

                            # Send the data and close this connection
                            server_socket.sendto(pickle.dumps(ack), (client_ip, client_ack_port))

                            # Write the data into the file
                            with open("server_data/"+FILE_NAME, "ab+") as f:
                                f.write(packet["data"])

                            expected_seq_no += 1

                        else:
                            print("Packet with unexpected sequence number receiver -- out of order / duplicate packet")
                            #print("Discarded the packet : " + str(packet["data"]))
                            print("\n")

                    else:
                        print("Packet is discarded due to incorrect checksum value")

    except socket.error as msg:
        print(msg)
        sys.exit(1)

    except Exception as e:
        print(e)

    finally:
        server_socket.close()
        sys.exit(1)

if __name__ == "__main__":
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FILE_NAME = sys.argv[3]
    PL_PROB = float(sys.argv[4])

    main()
