echo -n "Enter server address> "
read server_addr

echo -n "Enter server port > "
read server_port

echo -n "Enter Client address>"
read client_addr

python client.py $server_addr $server_port smaller.txt 64 100 $client_addr
python client.py $server_addr $server_port smaller.txt 64 200 $client_addr
python client.py $server_addr $server_port smaller.txt 64 300 $client_addr
python client.py $server_addr $server_port smaller.txt 64 400 $client_addr
python client.py $server_addr $server_port smaller.txt 64 500 $client_addr
python client.py $server_addr $server_port smaller.txt 64 600 $client_addr
python client.py $server_addr $server_port smaller.txt 64 700 $client_addr
python client.py $server_addr $server_port smaller.txt 64 800 $client_addr
python client.py $server_addr $server_port smaller.txt 64 900 $client_addr
python client.py $server_addr $server_port smaller.txt 64 1000 $client_addr
