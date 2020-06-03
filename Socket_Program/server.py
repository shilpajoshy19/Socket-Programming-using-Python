import socket
import os
import sys
import hashlib


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Check argument provided by user
def checkArgs():
    if len(sys.argv) != 2:
        print("ERROR: Must supply 1 arguments \nUSAGE: Server port")
        sys.exit()
    if int(sys.argv[1]) < 5000:
        print("ERROR: The port number should be greater than 5000 ")
        sys.exit()
    return int(sys.argv[1])


# the server IP and Port
UDP_IP = '127.0.0.1'
UDP_PORT = checkArgs()

# start the  server
sock.bind((UDP_IP, UDP_PORT))


# Function to send file to client
def getfile():
    c = 0
    data, address = sock.recvfrom(1024)
    fileName = data.decode()
    print("Client asked for " + fileName)
    if os.path.isfile(fileName):
        size = os.path.getsize(fileName)
        hash = hashlib.md5()
        with open(fileName, 'rb') as fh:
            buf = fh.read()
            hash.update(buf)
        Text = "EXISTS" + hash.hexdigest() + str(os.path.getsize(fileName))
        Message = Text.encode()
        sock.sendto(Message, address)
        data, address = sock.recvfrom(1024)
        userR = data.decode()
        if userR == 'OK':
            with open(fileName, 'rb') as f:
                while c <= size:
                    sock.settimeout(0.5)
                    bytesTosend = f.read(1024)
                    sock.sendto(bytesTosend, address)
                    for i in range(0, 2):
                        try:
                            ACK, address = sock.recvfrom(1024)
                            sock.settimeout(None)
                        except socket.timeout:
                            sock.sendto(data, address)
                    c += 1024
                    if c< size:
                        print("Uploading")
                    else:
                        print("Percentage of uploading : " + str(100) + "%")
    else:
        Text = "Not EXISTS"
        Message = Text.encode()
        sock.sendto(Message, address)


# A function to receive file from client
def putfile():
    c = 0
    data, addr = sock.recvfrom(1024)
    fileName = data.decode()
    if fileName != "Error":
        print("Client connected ip: " + str(addr))
        print("Client asked for put " + fileName)
        Text = "The size of file"
        Message = Text.encode()
        sock.sendto(Message, addr)
        data, addr = sock.recvfrom(1024)
        M = data.decode()
        HashFile = M[:32]
        size = M[32:]
        print("The Size of the file "+size)
        print("The Hash of the file "+HashFile)
        fileSize = int(size)
        Text = "OK Ready to upload"
        Message = Text.encode()
        sock.sendto(Message, addr)
        data, addr = sock.recvfrom(1024)
        userR = data.decode()
        if userR == 'OK':
            with open(fileName, 'wb') as f:
                while c <= fileSize:
                    c += 1024
                    if c < fileSize:
                        print("Downloading")
                    else:
                        print("Percentage downloading : " + str(100)+ "%")

                    data, addr = sock.recvfrom(1024)
                    Ack = "1"
                    sock.sendto(Ack.encode(), addr)
                    sock.sendto(Ack.encode(), addr)
                    f.write(data)

        if os.path.isfile(fileName):
            hasher = hashlib.md5()
            with open(fileName, 'rb') as fh:
                buf = fh.read()
                hasher.update(buf)
            if hasher.hexdigest() == HashFile:
                print("The file has been downloaded correctly")
            else:
                print("Error: The file download is interepted!! \nTry again!!")

    else:
        print("Error: No respond from the client")

# Function to rename 
def rename():
    data, addr = sock.recvfrom(1024)
    fileName = data.decode()
    print("Client connected ip: " + str(addr))
    print("Client asked to change the name of the file" + fileName)
    if os.path.isfile(fileName):
        Text = "EXISTS"
        Message = Text.encode()
        sock.sendto(Message, addr)
        data, addr = sock.recvfrom(1024)
        newFilename = data.decode()
        os.rename(fileName, newFilename)
        Text = "Done"
        Message = Text.encode()
        sock.sendto(Message, addr)

    else:
        Text = "Not EXISTS"
        Message = Text.encode()
        sock.sendto(Message, addr)

# Function to list files
def listfile():
    c = 0
    data, addr = sock.recvfrom(1024)
    Message = data.decode()
    print("Client connected ip: " + str(addr))
    print("Client asked to " + Message)
    dirs = os.listdir(os.getcwd())
    Text = str(len(dirs))
    Message = Text.encode()
    sock.sendto(Message, addr)
    while c < len(dirs):
        Message = dirs[c].encode()
        sock.sendto(Message, addr)
        c += 1

# Program

while True:
    print("server started.")
    data, addr = sock.recvfrom(1024)
    s = data.decode()
    if s == '1':
        getfile()
    elif s == '2':
        putfile()
    elif s == '3':
        rename()
    elif s == '4':
        listfile()
    elif s == '5':
        sock.close()
        print("The Server has been shutdown")
        quit()
