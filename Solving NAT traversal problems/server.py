from socket import *
from threading import Timer
import time

registerList={}  # registration list
privateList={}  # private IP address of client
recvTime={}  # keep-alive message receiving time

def keepTimer():

    for i in range(0, len(recvTime)):

        if i>=len(recvTime): break

        # detect client termination without receiving an unregistration request
        if time.time()-list(recvTime.values())[i] > 30:
            clientID=list(recvTime.keys())[i]
            sendMsg = clientID + " is off-line "
            sendMsg+=registerList.get(clientID)[0]+":"+str(registerList.get(clientID)[1])
            print(sendMsg)

            del registerList[clientID]
            del recvTime[clientID]
            del privateList[clientID]

            for j in range(0, len(registerList)):
                serverSocket.sendto(sendMsg.encode(), (list(registerList.values())[j][0], list(registerList.values())[j][1]))

    timer=Timer(10, keepTimer)
    timer.start()


if __name__ == '__main__':

    serverSocket=socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', 10080))
    print("server program starts....")

    timer=Timer(10, keepTimer)
    timer.start()

    clientID=""
    sendMsg=""
    privateAddr=""

    while True:
        message, clientAddr = serverSocket.recvfrom(2048)
        #print(message.decode())
        if "@keepalive" in message.decode():
            clientID=message.decode().split("@")[0]
            recvTime[clientID]=time.time()  # update receiving time
            continue

        elif "@exit" in message.decode():
            clientID=message.decode().split(" ")[0]
            sendMsg=clientID+" is unregistered "
            sendMsg+=registerList.get(clientID)[0]+":"+str(registerList.get(clientID)[1])

        else:
            clientID = message.decode().split(" ")[0]
            privateAddr = message.decode().split(" ")[1]
            sendMsg = clientID + " " + clientAddr[0] + ":" + str(clientAddr[1])


        print(sendMsg)


        if "@exit" not in message.decode():

            for i in range(0, len(registerList)):
                registerMsg=list(registerList.keys())[i]+" "+list(registerList.values())[i][0]+":"+str(list(registerList.values())[i][1])
                serverSocket.sendto(registerMsg.encode(), clientAddr)

            for i in range(0, len(privateList)):
                if clientAddr[0]==list(privateList.values())[i][0]:
                    cmp1 = list(privateList.values())[i][1].split(".")
                    cmp2 = privateAddr.split(".")
                    if cmp1[0] + "." + cmp1[1] + "." + cmp1[2] == cmp2[0] + "." + cmp2[1] + "." + cmp2[2]:
                        privateMsg = list(privateList.keys())[i] + "@private:" + list(privateList.values())[i][1]
                        serverSocket.sendto(privateMsg.encode(), clientAddr)

            registerList[clientID]=clientAddr
            recvTime[clientID]=time.time()
            privateList[clientID] = (clientAddr[0], privateAddr)
            #print(privateList)

        for i in range(0, len(registerList)):
            serverSocket.sendto(sendMsg.encode(), (list(registerList.values())[i][0], list(registerList.values())[i][1]))
            if "@exit" not in message.decode():
                if list(registerList.values())[i][0] == privateList.get(clientID)[0]:
                    cmp1 = privateList.get(clientID)[1].split(".")
                    cmp2 = privateList.get(list(registerList.keys())[i])[1].split(".")
                    if cmp1[0] + "." + cmp1[1] + "." + cmp1[2] == cmp2[0] + "." + cmp2[1] + "." + cmp2[2]:
                        privateMsg = clientID + "@private:" + privateList.get(clientID)[1]
                        serverSocket.sendto(privateMsg.encode(), (list(registerList.values())[i][0], list(registerList.values())[i][1]))

        if "@exit" in message.decode():
            del registerList[clientID]
            del recvTime[clientID]
            del privateList[clientID]