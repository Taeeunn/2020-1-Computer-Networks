from socket import *
from threading import Thread, Lock, Timer
import time
import sys
import math


lock=Lock()
sending=0
drop=False
dropPkt=0
timeout=1
ackSeq=0
startTimer=0


"Use this method to write Packet log"
def writePkt(logFile, procTime, pktNum, event):
    logFile.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))

"Use this method to write ACK log"
def writeAck(logFile, procTime, ackNum, event):
    logFile.write('{:1.3f} ACK: {} | {}\n'.format(procTime, ackNum, event))

"Use this method to write final throughput log"
def writeEnd(logFile, throughput, avgRTT):
    logFile.write('\n\nFile transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms\n'.format(avgRTT))

def writeTimeout(logFile, procTime, ackNum, sendTime, timeout):
    logFile.write('{:1.3f} pkt: {} | timeout since {:1.3f}(timeout value {:1.3f})\n'.format(procTime, ackNum, sendTime, timeout))
    
def writeRetransmit(logFile, procTime, ackNum):
    logFile.write('{:1.3f} pkt: {} | retransmitted\n'.format(procTime, ackNum))

def writeDuplicate(logFile, procTime, ackNum):
    logFile.write('{:1.3f} pkt: {} | 3 duplicated ACKs\n'.format(procTime, ackNum))


def singleTimer():
    
    global startTimer, timeout, ackSeq, drop, dropPkt
    

    timeoutnow=timeout
    if sendTime[startTimer]!=0 and time.time()-sendTime[startTimer]>timeoutnow:
        nowTime=time.time()
        
        drop=True
        dropPkt=startTimer  
              
        writeTimeout(log, nowTime-startTime, startTimer, sendTime[startTimer]-startTime, timeoutnow)
        seq='%20d'%(startTimer)
        sendSocket.sendto(seq.encode()+filePkt[startTimer], (recvAddr, recvPort))
        sendTime[startTimer]=nowTime
        writeRetransmit(log, sendTime[startTimer]-startTime, startTimer)
        
    
    timer=Timer(0.0000000001, singleTimer)
    
    
    if ackSeq<pktNum-1: timer.start()
    else: return
    
    
          
def sendPkt(sendSocket):
   
    global sending, startTime, sendTime, drop
    cnt=0
    sendTime=[0.0]*pktNum
   
    startTime=time.time()
    
    while True:
        if drop==True:
            continue        
        while sending<windowSize:
            if drop==True: continue  
            seq='%20d'%(cnt) 
            sendSocket.sendto(seq.encode()+filePkt[cnt], (recvAddr, recvPort))
            
            sendTime[cnt]=time.time()
            writePkt(log, sendTime[cnt]-startTime, cnt, "sent")
            
            cnt+=1
            
            lock.acquire()
            sending+=1
            lock.release()

             
            if cnt==pktNum: return

   
    
def recvAck(sendSocket):
    
    global sending, avgRTT, drop, dropPkt, startTimer, timeout, ackSeq
   
    ackPkt=[0]*pktNum
    
    chk=0
    ackTime=0
    devRTT=0
    avgRTT=0
    timeout=1
    preSeq=-1
   

    singleTimer()

    while True:      
        
        ackMsg, recvAddress=sendSocket.recvfrom(20)
        
        ackTime=time.time()
        ackSeq=int(ackMsg.decode())

        # dstFilename packet drop       
        if ackSeq==-100:
            seq='%20d'%(-100)
            sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
            sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
            continue
                  
        writeAck(log, ackTime-startTime, ackSeq, "received")
        
        if ackSeq==-1:
            seq='%20d'%(0)
            sendSocket.sendto(seq.encode()+filePkt[0], (recvAddr, recvPort))
            continue
            
        ackPkt[ackSeq]+=1

        if ackPkt[ackSeq]==1:
           if ackSeq>preSeq:
                lock.acquire()
                sending-=abs(ackSeq-preSeq)
                lock.release()
          
                             
                  
        #3 Duplicated ACKs
        if ackPkt[ackSeq]==4:
          
            drop=True
            dropPkt=ackSeq+1
                
            writeDuplicate(log, time.time()-startTime, ackSeq)
            seq='%20d'%(ackSeq+1)
            sendSocket.sendto(seq.encode()+filePkt[ackSeq+1], (recvAddr, recvPort))
            sendTime[ackSeq+1]=time.time()
            writeRetransmit(log, sendTime[ackSeq+1]-startTime, ackSeq+1)
            
        
        if ackPkt[ackSeq]>1:
            if ackSeq>preSeq:
                preSeq=ackSeq
            continue        
        
    
        if drop==False:
            # first RTT measurement        
            if chk==0:
                avgRTT=ackTime-sendTime[ackSeq]
                devRTT=avgRTT/2
                chk=1
            # subsequent RTT measurement
            else:
                avgRTT=0.875*avgRTT+0.125*(ackTime-sendTime[ackSeq])
                devRTT=0.75*devRTT+0.25*abs(ackTime-sendTime[ackSeq]-avgRTT)
          

        # all packet is successfully transmitted
        if ackSeq==pktNum-1: 
            return
                
        timeout=avgRTT+4*devRTT

        # max of timeout: 60 secods
        if timeout>60:
            timeout=60

        # set timeout start -> oldest unacked packet
        startTimer=ackSeq+1
            
        if ackSeq>preSeq:
            preSeq=ackSeq
        
        if drop==True and ackSeq>=dropPkt:
            drop=False

   
def fileSender():
   

    seq='%20d'%(-100)
    sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
    sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
    sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
    sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort))
    sendSocket.sendto(seq.encode()+pktNumstr.encode()+dstFilename.encode(), (recvAddr, recvPort)) 

    sendThread=Thread(target=sendPkt, args=(sendSocket,))
    recvThread=Thread(target=recvAck, args=(sendSocket,))

    
    sendThread.start()
    recvThread.start()


    sendThread.join()    
    recvThread.join()
    

    writeEnd(log,  pktNum/(time.time()-startTime), avgRTT*1000)
    
  

if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name
    recvPort=10080
    
    sendSocket=socket(AF_INET, SOCK_DGRAM)
    sendSocket.bind(('', 0))
    #print('sender program starts...')
    
    filePkt=[]
    f=open(srcFilename, "rb")
    data=f.read(1400)
    while True:
        filePkt.append(data)
        if len(data)<1400: break
        data=f.read(1400)
      
    pktNum=len(filePkt)   
    pktNumstr='%20d'%(pktNum)    
               
    log=open(srcFilename+"_sending_log.txt", "w")

    fileSender()

    log.close()
    sendSocket.close()

