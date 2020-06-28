from threading import Thread
from socket import *
import time


def execute(connectionSocket):

    count=100
    while count>0: # Keep-alive: max=100

        start_time=0.0  # cookie creation time (login post)
        userid=""  # userid in cookie
        vTime=31   # valid time (time since cookie creation)

        try:
            msg=connectionSocket.recv(1024).decode()

            if not msg:
                connectionSocket.close()
                break
            
           #print('received: '+msg)

        
            reset=0
            if "userid" in msg and "passwd" in msg and "login" in msg:
                userid=msg.split('\nuserid=')[1]
                userid=userid.split('&')[0]
                start_time=time.time()
                vTime=time.time()-start_time
                reset=1
                 

            elif '\nCookie: ' in msg:
                c=msg.split('\nCookie: ')[1]
                c=c.split('\n')[0]
                start_time=float(c.split('=')[1])
                vTime=time.time()-start_time


            if msg.split()[1]=='/': 
                fname='index.html'
            else:  
                filename=msg.split()[1]
                fname=filename[1:]


            if vTime>=30:
                if fname!='index.html': raise ValueError


            if fname=='index.html' and vTime<30:
                fname='secret.html'
    

            f=open(fname, 'rb')
            data=f.read()
            f.close()
        
            ext=fname.split('.')[1]
            header=''

            
            if reset==1:
                header='HTTP/1.1 200 OK\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=%d\r\nContent-Length: %d\r\nSet-Cookie: %s=%d; Max-Age=30\r\nContent-Type: text/html\r\n\r\n'%(count, len(data), userid, start_time)
            
            elif ext=='html':
                header='HTTP/1.1 200 OK\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=%d\r\nContent-Length: %d\r\nContent-Type: text/html\r\n\r\n'%(count, len(data))
            
            else:
                if ext=='jpg' or ext=='jpe': ext='jpeg'
                mime='image/'+ext
                header='HTTP/1.1 200 OK\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=%d\r\nContent-Length: %d\r\nContent-Type: %s\r\n\r\n'%(count, len(data), mime)
            

            connectionSocket.send(header.encode()+data)

            #print('sent: '+header+'\n')
        
    

        except ValueError:

            f=open('403.html', 'rb')
            data=f.read()
            f.close()

            header="HTTP/1.1 403 Forbidden\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=%d\r\nContent-Length: %d\r\nContent-Type: text/html\r\n\r\n"%(count, len(data))

            connectionSocket.send(header.encode()+data)

        
            #print('sent: '+header+'\n')

        except IOError:
        
            f=open('404.html', 'rb')
            data=f.read()
            f.close()

            header="HTTP/1.1 404 Not Found\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=%d\r\nContent-Length: %d\r\nContent-Type: text/html\r\n\r\n"%(count, len(data))

            connectionSocket.send(header.encode()+data)
            
            #print('sent: '+header+'\n')
        

        count=count-1
        if count==0: connectionSocket.close()
            



def main():

    serverSocket=socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', 10080))
    serverSocket.listen(100)
    #print('The TCP server is ready to receive.\n')

    while True:
    
        connectionSocket, addr=serverSocket.accept()

        t=Thread(target=execute, args=(connectionSocket, ))
        t.start()

    serverSocket.close()


if __name__=='__main__':
    main()
    
