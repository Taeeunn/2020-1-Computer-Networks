from socket import *
from threading import Thread, Timer


registerList = {}
privateList = {}
stop = False


def keepTimer():
    global timer

    clientSocket.sendto((clientID + "@keepalive").encode(), (serverAddr, 10080))
    timer = Timer(10, keepTimer)
    timer.start()


def cmdExecute(clientSocket, clientID):
    global stop

    while True:
        command = input("")

        if command == '@exit':
            clientSocket.sendto((clientID + " " + command).encode(), (serverAddr, 10080))
            stop = True
            timer.cancel()
            return

        elif command == '@show_list':
            for i in range(0, len(registerList)):
                print(list(registerList.keys())[i] + " " + list(registerList.values())[i])

        elif "@chat" in command:
            msgID = command.split(" ")[1]
            content = command.split(msgID + " ")[1]

            # under the same NAT
            if msgID in privateList:
                addr = privateList.get(msgID)
                clientSocket.sendto((clientID + '@chat ' + content).encode(), (addr, 10081))

            else:
                if msgID in registerList:
                    addrport = registerList.get(msgID)
                    addr = addrport.split(':')[0]
                    port = int(addrport.split(':')[1])
                    clientSocket.sendto((clientID + '@chat ' + content).encode(), (addr, port))

                else:
                    print("There is no " + msgID + " in registration list.")


def recvExecute(clientSocket, clientID):
    global stop

    while True:
        if stop == True: return

        message, serverAddr = clientSocket.recvfrom(2048)

        #print(message.decode())

        if "unregistered" in message.decode() or "off-line" in message.decode():
            if clientID not in message.decode():
                userID=message.decode().split("is")[0][:-1]
                del registerList[userID]
                if userID in privateList:
                    del privateList[userID]

        elif "@chat" in message.decode():
            fromID = message.decode().split("@chat")[0]
            msg = message.decode().split("@chat ")[1]
            print("From " + fromID + " [" + msg + "]")

        elif "@private" in message.decode():
            userID = message.decode().split("@private:")[0]
            privateAddr = message.decode().split("@private:")[1]
            privateList[userID] = privateAddr

        else:
            msgID = message.decode().split(" ")[0]
            msgAddr = message.decode().split(" ")[1]
            registerList[msgID] = msgAddr



def main():

    recvThread = Thread(target=recvExecute, args=(clientSocket, clientID))
    cmdThread = Thread(target=cmdExecute, args=(clientSocket, clientID))

    recvThread.start()
    cmdThread.start()


if __name__ == '__main__':
    clientID=input("Enter client ID: ")
    serverAddr=input("Enter server IP address: ")

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(("", 10081))

    # get private IP address
    ipSocket = socket(AF_INET, SOCK_DGRAM)
    ipSocket.connect((serverAddr, 80))
    privateIP = ipSocket.getsockname()[0]
    #print(privateIP)

    clientSocket.sendto((clientID + " " + privateIP).encode(), (serverAddr, 10080))

    timer = Timer(10, keepTimer)
    timer.start()

    main()