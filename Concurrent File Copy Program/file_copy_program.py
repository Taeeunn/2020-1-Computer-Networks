from threading import Thread
import time
import sys


log=open('log.txt', 'w')
start_time=time.time()


def execute(source, destination):

    dest=open(destination, 'wb')
    
    with open(source, 'rb') as f:

        log.write("%0.2f"%(time.time()-start_time)+"\tStart copying "+source+" to "+destination+'\n')

        chunk=f.read(10000)

        while 1:
            dest.write(chunk);
            if len(chunk)<10000:
               break
            chunk=f.read(10000)

        dest.close()
        
        log.write("%0.2f"%(time.time()-start_time)+"\t"+destination+" is copied completely\n")
   


def main():

    while 1:

        source=input('Input the file name: ')

        if source=='exit':
            sys.exit()

        destination=input('Input the new name: ')
        print()

        t=Thread(target=execute, args=(source, destination))
        t.start()



if __name__=="__main__":
    main()


