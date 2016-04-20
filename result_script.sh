
echo -n "Enter server address> "
read server_addr

echo -n "Enter server port > "
read server_port

echo -n "Enter client address>"
read client_addr

python client.py $server_addr $server_port smaller.txt 1 500 $client_addr
python client.py $server_addr $server_port smaller.txt 2 500 $client_addr
python client.py $server_addr $server_port smaller.txt 4 500 $client_addr
python client.py $server_addr $server_port smaller.txt 8 500 $client_addr
python client.py $server_addr $server_port smaller.txt 16 500 $client_addr
python client.py $server_addr $server_port smaller.txt 32 500 $client_addr
python client.py $server_addr $server_port smaller.txt 64 500 $client_addr
python client.py $server_addr $server_port smaller.txt 128 500 $client_addr
python client.py $server_addr $server_port smaller.txt 256 500 $client_addr
python client.py $server_addr $server_port smaller.txt 512 500 $client_addr
python client.py $server_addr $server_port smaller.txt 1024 500 $client_addr
