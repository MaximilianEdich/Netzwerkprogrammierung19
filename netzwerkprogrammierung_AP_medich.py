#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 10:30:31 2019

@author: medich
"""

import sys
import socket
import threading
import time

class Server:
    """
    
    """
    
    connections= []
    #adress family und Protokollfestlegung
    sSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    
    def __init__(self, pIp, pPort):
        """ Initialisiert Standartwerte des Servers und macht die Verbindung
        zugaenglich.
        """
        
        self.startTime = time.time()
        self.ip = pIp
        self.port = pPort
        self.sSock.bind((self.ip, self.port))
        self.sSock.listen(socket.SOMAXCONN)
        self.myMaster = None
        self.running = 1
        
    def isMaster(self):
        """ Gibt zurueck, ob dieser Server Master des Netzwerks ist.
        """
        return self.myMaster == self
    
    def getMasterVoteValue(self):
        return self.startTime
    
    def masterVoteFunction(self, thisServerValue, remoteServerValue):
        return self.convertMVValue(thisServerValue) < self.convertMVValue(remoteServerValue)
    
    def convertMVValue(self, value):
        return float(value)
    
    

    def connectionHandler (self, inSocket, addr):
        """ Regelt die beidseitige Verbindung zwischen zwei Servern.
        Tauscht Nachrichten aus und bestimmt neue Master.
        """
        
        while True:
            try:
                if (self.myMaster == None):
                    #Server ist ohne bekannten Master einem Netzwerk beigetreten
                    #frage Master oder Master Bedingungswert an
                    inSocket.send(bytes('-votem', 'utf8'))
                    data = inSocket.recv(1024)
                    if (data.decode('utf8') == "-votem"):
                        #sende Nachricht mit Master Value zum voten
                        inSocket.send(bytes(str('-votem+' + str(self.getMasterVoteValue())), 'utf8'))
                    elif (data.decode('utf8')[0:7] == "-votem+"):
                        #master value des anderen Servers erhalten
                        #extrahiere information und vergleiche mit eigenem
                        #bestimme so neuen Master
                        masterValue = data.decode('utf8')[7:]
                        if (str(masterValue).find('-', 0) > -1):
                            masterValue = masterValue[0:str(masterValue).find('-', 0)]
                        print(masterValue)
                        if (self.masterVoteFunction(self.getMasterVoteValue(), masterValue)):
                            #Server ist Master
                            self.myMaster = self
                        else:
                            pass
                    elif (data.decode('utf8') == "-ismaster"):
                        self.myMaster = inSocket
                        
                else:
                    #Server ist Master oder kennt Master
                    inSocket.send(bytes('-alive', 'utf8'))
                    data = inSocket.recv(1024)
                    if (data.decode('utf8') != "-alive"):
                        if (data.decode('utf8') == "-votem"):
                            if (self.myMaster == self):
                                inSocket.send(bytes('-ismaster', 'utf8'))
                            else:
                                pass
            except (ConnectionResetError, BrokenPipeError) as e:
                print("connection lost!")
                self.connections.remove(inSocket)
                if (len(self.connections) < 1):
                    #keine Verbindungen, vergiss Master
                    self.myMaster = None
                inSocket.close()
                break
    
    def connectToServer(self, cAdress, cPort):
        """ Versucht einen Verbindungsaufbau zur gewuenschten IP und Port.
        """
        
        validRequest = 1
        for connection in self.connections:
            if (cAdress == connection.getpeername()[0] and cPort == connection.getpeername()[1]):
                validRequest = 0
                print("already connected to this server!")
        
        if (validRequest):
            cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cSock.connect((cAdress, cPort))
            addr = (cAdress, cPort)
            conThread = threading.Thread(target=self.connectionHandler, args=(cSock, addr))
            conThread.daemon = True
            conThread.start()
            self.connections.append(cSock)
            print(cSock)
    
    
    
    def inputListener(self):
        while True:
            inText = input("")
            if (inText == "-h"):
                print("Commands:\n-q: quit server\n-t: print start time\n\
-m: check if server is master\n\
-c: <ip> <port>: connect to ip and port\n\
-cn: get number of connections")
            if (inText == "-m"):
                print(self.isMaster())
            elif (inText == "-q"):
                self.running = 0
                self.sSock.close()
            elif (inText == "-t"):
                print(self.startTime)
            elif (inText[0:3] == "-c "):
                spacer = inText.find(" ", 3)
                cAdress = inText[3:spacer]
                cPort = int(inText[spacer+1:])
                if (cAdress != self.ip or cPort != self.port):
                    self.connectToServer(cAdress, cPort)
                else:
                    print("server cannot connect to itself!")
            elif (inText == "-cn"):
                print(len(self.connections))
            elif (inText == "-cl"):
                for connection in self.connections:
                    print(connection)
                
        
    
    def run(self):
        """ Server lauscht nach eingehenden Verbindungen und oeffnet dann einen
        thread fuer die Kommunikation.
        """
        
        inSocket = None
        try:
            #starte listener fuer inputs
            inputThread = threading.Thread(target=self.inputListener)
            inputThread.daemon = True
            inputThread.start()
            print("Server started")
            while self.running:
                #starte connection Suche
                inSocket, addr = self.sSock.accept()
                conThread = threading.Thread(target=self.connectionHandler, args=(inSocket, addr))
                conThread.daemon = True #offene Threads werden beim Schließen mitgeschlossen
                conThread.start()
                self.connections.append(inSocket)
                print(inSocket)
        finally:
            if (inSocket != None):
                inSocket.close()
            

if (len(sys.argv) == 3):
    server = Server(sys.argv[1], int(sys.argv[2]))
    try:
        server.run()
    except KeyboardInterrupt as e:
        sys.exit("\nQuit Server")
else:
    sys.exit("Missing arguments\nUse IP-Adress and Port")