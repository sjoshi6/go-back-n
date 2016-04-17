import socket
import sys
import pickle
from threading import Thread, Lock
from settings import *
import signal
from time import time

SERVER_IP = ""
SERVER_PORT = ""
FTP_FILE_NAME = ""
WINDOW_SIZE = ""
MSS = ""
# Create a lock to share within threads main / ack handler
lock = Lock()


def read_file(file_name):
    file_byte_arr = []
    with open(file_name, 'rb') as data_file:
        while True:

            one_byte = data_file.read(1)
            if not one_byte:
                break

            file_byte_arr.append(one_byte)

    return file_byte_arr


def rdt_send(bytes_arr, mss):
    for i in range(0, len(bytes_arr), mss):
        yield bytes_arr[i:i + mss]


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


def create_packets(bytes_arr, mss):
    all_packets = []
    sequence_no = 0

    for segment in rdt_send(bytes_arr, mss):

        data = ""
        for part in segment:
            data += part

        packet = {"header": {}}
        packet["header"]["sequence_number"] = sequence_no
        packet["header"]["checksum"] = generate_checksum(segment)
        packet["header"]["data_type"] = int('0101010101010101', 2)
        packet["header"]["fin"]=0
        packet["data"] = data
        all_packets.append(packet)
        sequence_no += 1

    return all_packets


def ack_handler(ack_recv_sock, lock, last_received_ack_p, final_sequence_no_p):

    global last_received_ack, finished, final_sequence_no
    last_received_ack = last_received_ack_p
    final_sequence_no = final_sequence_no_p
    finished = False

    while not finished and int(last_received_ack) < int(final_sequence_no):

        data, addr = ack_recv_sock.recvfrom(1024)

        ack_data = pickle.loads(data)

        with lock:
            last_received_ack = ack_data["header"]["ack_number"]
            print(last_received_ack)

        signal.alarm(0)
        signal.setitimer(signal.ITIMER_REAL, 2)

    ack_recv_sock.close()


def move_back(signum, frame):

    print("Time out detected ; move back in time to the last received ack packet")

    global last_received_ack, last_sent_sequence_number

    with lock:
        # Reset the last sent sequence number to the last acknowledged packet
        signal.alarm(0)

        last_sent_sequence_number = last_received_ack

        signal.setitimer(signal.ITIMER_REAL, 2)


def main(lock, packets,final_sequence_no_p):

    try:
        global final_sequence_no, last_sent_sequence_number, next_sequence_number, last_ack_number, current_window_size
        global last_received_ack, finished

        # Setting the timer for packet 1
        signal.setitimer(signal.ITIMER_REAL, 2)

        finished = False
        last_sent_sequence_number = -1
        next_sequence_number = 0
        last_ack_number = -1
        last_received_ack = -1
        final_sequence_no = final_sequence_no_p

        # Create a socket to connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('152.46.20.210', CLIENT_SEND_PORT))

        # Start the time when sending started
        start_time = time()

        # Unless we have reached the last packet
        while int(last_received_ack) < int(final_sequence_no):

            while ((int(last_sent_sequence_number) - int(last_received_ack)) < int(WINDOW_SIZE)) and int(last_sent_sequence_number) < int(final_sequence_no):

                with lock:
                    packet = packets[last_sent_sequence_number+1]
                    last_sent_sequence_number += 1

                    data = pickle.dumps(packet)
                    sock.sendto(data, (SERVER_IP, SERVER_PORT))

        packet = {"header": {}}
        packet["header"]["sequence_number"] = final_sequence_no+1
        packet["header"]["checksum"] = "0000000000000000"
        packet["header"]["data_type"] = int('0101010101010101', 2)
        packet["header"]["fin"]=1
        packet["data"] = ""

        data = pickle.dumps(packet)
        sock.sendto(data,(SERVER_IP, SERVER_PORT))

        # Record time when process ended
        end_time = time()
        time_taken = end_time - start_time
        with open('results.txt', 'ab+') as data_file:
            data_file.write("#--------------------------#\n")
            data_file.write("MSS is "+ str(MSS)+"\n")
            data_file.write("Window size is " + str(WINDOW_SIZE)+"\n")
            data_file.write("Time for file Transfer = " + str(time_taken)+"\n")
            data_file.write("#--------------------------#\n")

    finally:
        # Once all acks are received close all
        finished = True
        sock.close()
        sys.exit(1)


def launcher():

    # create the signals for transmission
    signal.signal(signal.SIGALRM, move_back)

    # Create a byte array of data to be sent
    file_byte_arr = read_file(FTP_FILE_NAME)
    packets = create_packets(file_byte_arr, MSS)
    last_sequence_number = len(packets) - 1

    ack_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ack_recv_sock.bind(('152.46.20.210', CLIENT_ACK_PORT))

    # Launch the ack handler in a separate thread
    t = Thread(target=ack_handler, args=(ack_recv_sock, lock, -1, last_sequence_number))
    t.start()

    # Then start the main function to send file from the current thread
    main(lock, packets, last_sequence_number)


if __name__ == "__main__":
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    FTP_FILE_NAME = sys.argv[3]
    WINDOW_SIZE = int(sys.argv[4])
    MSS = int(sys.argv[5])
    launcher()
