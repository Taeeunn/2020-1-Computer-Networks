from socket import *
import time
import sys
import os


"Use this method to write Packet log"
def writePkt(logFile, procTime, pktNum, event):
    logFile.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))

"Use this method to write ACK log"
def writeAck(logFile, procTime, ackNum, event):
    logFile.write('{:1.3f} ACK: {} | {}\n'.format(procTime, ackNum, event))

"Use this method to write final throughput log"
def writeEnd(logFile, throughput):
    logFile.write('\n\nFile transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))


def fileReceiver():

    recvSocket=socket(AF_INET, SOCK_DGRAM)
    recvSocket.setsockopt(SOL_SOCKET, SO_SNDBUF, 100000000)
    recvSocket.bind(('', 10080))
    #print('receiver program starts...') 

    filename=""
    pktNumint=0
    
    log=open("log.txt", "w") # after rename

   
    cnt=0
    chk=0
    init=0
    ackNum=0
    startTime=0
    ackPkt=[]
    bufPkt=[]
    

    
    while True:
        message, sendAddress=recvSocket.recvfrom(2048)
        seq=int(message[:20].decode())

        if seq==-100:
            if init==1: continue
            filename=message[40:].decode()
            pktNumint=int(message[20:40].decode())

            ackPkt=[0]*(pktNumint+1)
            bufPkt=[""]*(pktNumint)
            os.rename("log.txt", filename+"_receiving_log.txt")

            init=1
            continue

        # dstFilename packet drop
        if init==0:
            seq='%20d'%(-100)
            recvSocket.sendto(seq.encode(), sendAddress)

            continue

        if chk==0:
            startTime=time.time()
            chk=1

       
        data=message[20:]
        writePkt(log, time.time()-startTime, seq, "received")

        if bufPkt[seq]=="": 
            bufPkt[seq]=data
        
        
        if cnt!=seq:            
            ackPkt[seq]=1
            for i in range(ackNum, pktNumint+1):
                if ackPkt[i]==0: break
            ackNum=i-1
            cnt=ackNum+1       
          
        else:
            ackPkt[cnt]=1
            for i in range(ackNum, pktNumint+1):
                if ackPkt[i]==0: break
            ackNum=i-1 
            cnt+=1


        ackNumstr='%20d'%(ackNum)
        recvSocket.sendto(ackNumstr.encode(), sendAddress)
        writeAck(log, time.time()-startTime, ackNum, "sent")
 

        if ackNum==pktNumint-1: 
            recvSocket.sendto(ackNumstr.encode(), sendAddress)
      
            f=open(filename, "wb")

            for i in range(0, pktNumint):
                f.write(bufPkt[i])
            break
       
        
       
    writeEnd(log, pktNumint/(time.time()-startTime))

    f.close()
    log.close()
    recvSocket.close()



if __name__=='__main__':
    fileReceiver()
