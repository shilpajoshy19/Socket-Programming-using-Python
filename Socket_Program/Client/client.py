import socket
import os
import sys
import hashlib

# Check the arguments given by the user
def checkArgs():
    if len(sys.argv) != 3:
        print("ERROR: Must have 2 arguments. \nUSE: IP address of the machine and Server port")
        sys.exit()
    if int(sys.argv[2]) < 5000:
        print("ERROR: The port number should be greater than 5000")
        sys.exit()
    return sys.argv[1], int(sys.argv[2])


# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IP and port from arguments
(UDP_IP, UDP_PORT) = checkArgs()


# Get file from server 
def getfile():
    c = 0
    fileName = input("Enter the Filename: ")
    if fileName != 'q':
        file = fileName.encode()
        sock.sendto(file, (UDP_IP, UDP_PORT))
        data, address = sock.recvfrom(1024)
        Message = data.decode()
        if Message[:6] == 'EXISTS':
            fileHash = Message[6:38]
            fileSize = int(Message[38:])
            Text = input("Do you want to download the file?(y/N)")
            if Text == 'y':
                T = "OK"
                sock.sendto(T.encode(), (UDP_IP, UDP_PORT))
                with open("Received_" + fileName, 'wb') as f:
                    while c <= fileSize:
                        data, address = sock.recvfrom(1024)
                        Ack = str(c)
                        sock.sendto(Ack.encode(), (UDP_IP, UDP_PORT))
                        sock.sendto(Ack.encode(), (UDP_IP, UDP_PORT))
                        f.write(data)
                        c += 1024
                        if c< fileSize:
                            print("Downloading")
                        else:
                            print("Download Percentage : " + str(100) + "%")
            else:
                print("Download has been canceled")
    else:
        print("The " + fileName + " does not exist. \nTry again!!!")
    # Check if the file is downloaded correct
    if os.path.isfile(fileName):
        HashFileRecived = hashlib.md5()
        with open(fileName, 'rb') as fh:
            buf = fh.read()
            HashFileRecived.update(buf)
        if HashFileRecived.hexdigest() == fileHash:
            print("The file has been downloaded correctly")
        else:
            print("Error: The file download is interepted!! \nTry again!!")


# A function to put a file in server
def putfile():
    c = 0
    fileName = input("Enter the Filename: ")
    if os.path.isfile(fileName):
        size = os.path.getsize(fileName)
        Text = fileName
        Message = Text.encode()
        sock.sendto(Message, (UDP_IP, UDP_PORT))
        data, addr = sock.recvfrom(1024)
        Message = data.decode()
        print(Message + " : " + str(os.path.getsize(fileName)))
        hash = hashlib.md5()
        with open(fileName, 'rb') as fh:
            buf = fh.read()
            hash.update(buf)
        Text = hash.hexdigest() + str(os.path.getsize(fileName))
        print("The hash Function : " + hash.hexdigest())
        Message = Text.encode()
        sock.sendto(Message, (UDP_IP, UDP_PORT))
        data, addr = sock.recvfrom(1024)
        Message = data.decode()
        print("Server is : " + Message)
        if Message[:2] == 'OK':
            Text = input("Do You want to upload the file (y/N)")
        if Text == 'y':
            T = "OK"
            Message = T.encode()
            sock.sendto(Message, (UDP_IP, UDP_PORT))
            with open(fileName, 'rb') as f:
                while c <= size:
                    c += 1024
                    if c < size:
                        print("Uploading")
                    else:
                        print("Upload percentage : " + str(100) + "%")

                    bytesTosend = f.read(1024)
                    sock.sendto(bytesTosend, (UDP_IP, UDP_PORT))
                    for i in range(0, 2):
                        try:
                            ACK, address = sock.recvfrom(1024)
                            sock.settimeout(None)
                        except socket.timeout:
                            sock.sendto(data, (UDP_IP, UDP_PORT))
        else:
            Text = "Error"
            Message = Text.encode()
            sock.sendto(Message, (UDP_IP, UDP_PORT))
            print("Error: File does not exist in the client directory")


# A function to rename a file im the server
def rename():
    oldFilename = input("Old Filename: ")
    newFilename = input("New Filename: ")
    Message = oldFilename.encode()
    sock.sendto(Message, (UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    Message = data.decode()
    if Message[:6] == 'EXISTS':
        Text = input("Do you want to change" + oldFilename + " to " + newFilename + " ?(y/N) ")
        if Text == 'y':
            Message = newFilename.encode()
            sock.sendto(Message, (UDP_IP, UDP_PORT))
            data, addr = sock.recvfrom(1024)
            Message = data.decode()
            print("The server changes the name of file and the work is " + Message)

    else:
        print("Try something different!!!")


# Function to list files in the local directory of the server
def listfile():
    c = 0
    Text = "List file"
    Message = Text.encode()
    sock.sendto(Message, (UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    y = data.decode()
    za = int(y)
    while c < za:
        data, addr = sock.recvfrom(1024)
        Message = data.decode()
        print(Message)
        c += 1

# Select options
def menu():
    while True:
        print("Select any option given below:")
        print("[1] get file")
        print("[2] put file")
        print("[3] rename file")
        print("[4] list files")
        print("[5] exit")
        select = input(" Enter your selection: ")
        if 1 <= int(select) <= 5:
            return select
        else:
            print("Error!!! Select again")


# Program
while True:
    s = menu()
    Message = s.encode()
    sock.sendto(Message, (UDP_IP, UDP_PORT))
    x = int(s)
    if x == 1:
        getfile()
    elif x == 2:
        putfile()
    elif x == 3:
        rename()
    elif x == 4:
        listfile()
    elif x == 5:
        print("The Server has been Shutdown.")
