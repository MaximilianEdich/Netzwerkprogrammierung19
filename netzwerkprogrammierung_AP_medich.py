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
    Ein Server mit eines festen IPv4 Adresse und einem festen Port.
    Er kann eine Verbindung zu beliebig vielen weiteren Servern aufnehmen und
    über TCP mit ihnen kommunizieren.
    """
    
    connections= []
    #adress family und Protokollfestlegung
    sSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    
    def __init__(self, pIp, pPort):
        """ 
        Initialisiert Standartwerte des Servers und macht die Verbindung
        zugaenglich.
        
        Parameter
        ---------
            pIp : str
                die gewuenschte IPv4 Adresse des Servers
            pPort : int
                der gewuenschte Port
        """
        
        #speichere Startzeit des Servers und Adressen-Argumente.
        self.startTime = time.time()
        self.ip = pIp
        self.port = pPort
        
        #starte socket und lausche auf dem port nach Verbindungsanfragen
        self.sSock.bind((self.ip, self.port))
        self.sSock.listen(socket.SOMAXCONN)
        
        #variablen fuer die Kommunikation mit anderen Servern
        self.myMaster = None
        self.running = True
        self.waitForReqCons = False
        self.concurrentMaster = False
        self.totalMasterCheck = False
        
    def isMaster(self):
        """ 
        Gibt zurueck, ob dieser Server Master des Netzwerks ist.
        """
        
        return self.myMaster == self
    
    def getMasterVoteValue(self):
        """
        Randbedingung, um einen Master zu bestimmen.
        In der Standardversion gibt diese Funktion die Startzeit des Servers
        zurueck.
        """
        
        return self.startTime
    
    def masterVoteFunction(self, localServerValue, remoteServerValue):
        """
        Randbedingungsfunktion. Nimmt die relevanten Werte dieses Servers und
        eines Kommunikationspartners entgegen.
        
        Parameter
        ---------
            localServerValue
                Wert dieses Servers
            remoteServerValue
                Wert des Kommunikationspartners (anderer Server)
        
        Returns
        -------
            True
                dieser Server ist gegenueber dem anderen ein valider Master
            False
                der andere Server ist gegenueber diesem ein valider Master
        """
        
        return self.convertMVValue(localServerValue) < self.convertMVValue(remoteServerValue)
    
    def convertMVValue(self, value):
        """
        Konvertiert die Eingaben in die masterVoteFunction(lsv, rsv) in die
        richtigen Datentypen, damit die Funktion mit ihnen einen Maser
        ermitteln kann.
        """
        
        return float(value)
    
    
    def connectionHandler (self, inSocket, addr):
        """ 
        Regelt die beidseitige Verbindung zwischen zwei Servern.
        Tauscht Nachrichten aus und bestimmt neue Master.
        
        Parameter
        ---------
            inSocket
                die Verbindung zum anderen Server
            addr
                Adresse des anderen Servers
        """
        
        while True:
            try:
                if (self.totalMasterCheck):
                    #ueberpruefe mit jeder einzelen Verbindung, welche auch
                    #angeblich Master ist, wer von beiden Master waere, bis
                    #nur noch ein Master uebrig ist.
                    inSocket.send(bytes('-iammaster+' + str(self.getMasterVoteValue()), 'utf8'))
                    print("-iammaster")
                    data = inSocket.recv(1024)
                    if (data.decode('utf8')[0:11] == "-iammaster+"):
                        #extrahiere Information und vergleiche mit eigenem Wert
                        masterValue = data.decode('utf8')[11:]
                        if (str(masterValue).find('-', 0) > -1):
                            masterValue = masterValue[0:str(masterValue).find('-', 0)]
                        print(masterValue)
                        if (self.masterVoteFunction(self.getMasterVoteValue(), masterValue)):
                            #Server bleibt master
                            self.myMaster = self
                        else:
                            #server ist kein master
                            self.totalMasterCheck = False
                        
                if (self.concurrentMaster):
                    #Server ist frisch beigetreten und koennte neuer Master sein
                    inSocket.send(bytes('-mvotem', 'utf8'))
                    print("-mvotem")
                    data = inSocket.recv(1024)
                    if (data.decode('utf8')[0:8] == "-mvotem+"):
                        #master value des anderen Servers erhalten
                        #extrahiere information und vergleiche mit eigenem
                        #bestimme so neuen Master
                        masterValue = data.decode('utf8')[8:]
                        if (str(masterValue).find('-', 0) > -1):
                            masterValue = masterValue[0:str(masterValue).find('-', 0)]
                        print(masterValue)
                        if (self.masterVoteFunction(self.getMasterVoteValue(), masterValue)):
                            #Neuer Server ist neuer Master
                            self.myMaster = self
                            self.concurrentMaster = False
                            #teile neuen Master mit
                            for connection in self.connections:
                                connection.send(bytes('-newmaster', 'utf8'))
                        else:
                            #server ist kein master
                            #alter master bleibt bestehen
                            self.concurrentMaster = False
                
                elif (self.waitForReqCons):
                    #frage beim Master Verbindung mit restlichen Servern an
                    #reqcons = request connections
                    inSocket.send(bytes(str("-reqcons+" + str(self.ip) + "+" + str(self.port)), 'utf8'))
                    print("-reqcons+" + str(self.ip) + "+" + str(self.port))
                    data = inSocket.recv(1024)
                    if (data.decode('utf8')[0:8] == "-newcon+"):
                        #Master hat Anfragen an restliche Server gesendet
                        #beende weitere Anfragen
                        self.waitForReqCons = False
                        self.concurrentMaster = True
                        print("concurrent")
                
                elif (self.myMaster == None):
                    print("none master")
                    #Server ist ohne bekannten Master einem Netzwerk beigetreten
                    #frage Master oder Master Bedingungswert an
                    try:
                        inSocket.send(bytes('-votem', 'utf8'))
                        print("-votem")
                        data = inSocket.recv(1024)
                    except OSError as e:
                        #gelegentliche Fehlermeldung beim schließen dieses Threads oder der Verbindung,
                        #bevor hieraus alles gesendet wurde.
                        #Fehlermeldung hat keine Auswirkungen auf den Programmablauf
                        pass
                    
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
                            #server ist kein master
                            #warte auf weitere nachrichten des masters
                            pass
                        
                    elif (data.decode('utf8') == "-ismaster"):
                        self.myMaster = inSocket
                        #frage beim Master Verbindung mit restlichen Servern an
                        #request connections
                        self.waitForReqCons = True
                    elif (data.decode('utf8')[0:8] == "-master+"):
                        #extrahiere master-server informationen aus Nachricht
                        address = data.decode('utf8')[8:]
                        if (str(address).find('-', 0) > -1):
                            address = address[0:str(address).find('-', 0)]
                        ip = address[0:str(address).find('+', 0)]
                        port = address[(str(address).find('+', 0)+1):]
                        #neuer Server baut Verbindung zum Master auf und loescht
                        #aktuelle Verbindung
                        self.connections.remove(inSocket)
                        inSocket.close()
                        self.connectToServer(ip, int(port))
                        
                else:
                    #Server ist Master oder kennt Master
                    #(oder kennt noch einen alten Master)
                    inSocket.send(bytes('-alive', 'utf8'))
                    data = inSocket.recv(1024)
                    if (data.decode('utf8') != "-alive"):
                        if (data.decode('utf8') == "-votem"):
                            #neuer Server kenn keinen Master
                            if (self.isMaster()):
                                #sende neuem Server, dass dieser hier Master ist
                                inSocket.send(bytes('-ismaster', 'utf8'))
                                print("-ismaster")
                            else:
                                #sende dem neuen Server, wer der Master ist
                                print(str(self.myMaster.getsockname()[1]))
                                inSocket.send(bytes('-master+' + str(self.myMaster.getpeername()[0]) + "+" + str(self.myMaster.getpeername()[1]), 'utf8'))
                        elif (self.isMaster() and data.decode('utf8')[0:9] == "-reqcons+"):
                            #Master erhaelt Beitrittsanfrage eines neuen Servers
                            #extrahiere serverinformationen aus nachricht
                            address = data.decode('utf8')[9:]
                            if (str(address).find('-', 0) > -1):
                                address = address[0:str(address).find('-', 0)]
                            ip = address[0:str(address).find('+', 0)]
                            port = address[(str(address).find('+', 0)+1):]
                            #sende an jeden server einen Verbindungsbefehl zum
                            #neuen server
                            for connection in self.connections:
                                connection.send(bytes(str('-newcon+' + str(ip) + "+" + str(port)), 'utf8'))
                                print("send newcon")
                        elif (data.decode('utf8')[0:8] == "-newcon+"):
                            #baue verbindung zum neuen server auf, fall es nicht
                            #der server selbst ist.
                            address = data.decode('utf8')[8:]
                            if (str(address).find('-', 0) > -1):
                                address = address[0:str(address).find('-', 0)]
                            ip = address[0:str(address).find('+', 0)]
                            port = address[(str(address).find('+', 0)+1):]
                            self.connectToServer(ip, int(port))
                        elif (data.decode('utf8') == "-mvotem"):
                            #sende Nachricht mit Master Value zum voten
                            inSocket.send(bytes(str('-mvotem+' + str(self.getMasterVoteValue())), 'utf8'))
                        elif (data.decode('utf8') == "-newmaster"):
                            #setze Verbindung als neuen Master
                            self.myMaster = inSocket
            
            #Verbindungsabbruch
            except (ConnectionResetError, BrokenPipeError) as e:
                print("connection lost!")
                if (inSocket == self.myMaster):
                    print("Master lost!")
                    self.myMaster = self
                    self.totalMasterCheck = True
                self.connections.remove(inSocket)
                print(len(self.connections))
                if (self.totalMasterCheck):
                    for connection in self.connections:
                        connection.send(bytes('-iammaster+' + str(self.getMasterVoteValue()), 'utf8'))
                if (len(self.connections) < 1):
                    #keine Verbindungen, vergiss Master
                    #reset suchanfragen
                    self.myMaster = None
                    self.totalMasterCheck = False
                    self.concurrentMaster = False
                    self.waitForReqCons = False
                inSocket.close()
                break
    
    def connectToServer(self, cAdress, cPort):
        """ 
        Versucht einen Verbindungsaufbau zur gewuenschten IP und Port.
        Bei Erfolg wird in einem Thread die Funktion 'connectionHandler()' gestartet.
        
        Parameter
        ---------
            cAdress
                IPv4 Adresse des Zielservers
            cPort
                Port des Zielservers
        """
        
        validRequest = True
        if (cAdress == self.ip and cPort == self.port):
            validRequest = False
        else:
            for connection in self.connections:
                if (cAdress == connection.getpeername()[0] and cPort == connection.getpeername()[1]):
                    validRequest = False
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
        """
        Lauscht nach Tasteneingaben des Benutzers und verarbeitet Kommandos.
        """
        
        while True:
            inText = input("")
            if (inText == "-h"):
                #Befehlsausgabe
                print("Commands:\n-t: print start time\n\
-m: check if server is master\n\
-c: <ip> <port>: connect to ip and port\n\
-cn: get number of connections")
            if (inText == "-m"):
                #Prueft, ob Server Master ist
                print(self.isMaster())
                if (self.myMaster == None):
                    print("(none master)")
            elif (inText == "-t"):
                #Printet Startzeit des Servers
                print(self.startTime)
            elif (inText[0:3] == "-c "):
                #Verbinde zum gewuenschten Server
                spacer = inText.find(" ", 3)
                cAdress = inText[3:spacer]
                cPort = int(inText[spacer+1:])
                if (cAdress != self.ip or cPort != self.port):
                    self.connectToServer(cAdress, cPort)
                else:
                    print("server cannot connect to itself!")
            elif (inText == "-cn"):
                #Zeige Anzahl von Verbindungen
                print(len(self.connections))
            elif (inText == "-cl"):
                #Zeige Verbindungen
                for connection in self.connections:
                    print(connection)
                
        
    
    def run(self):
        """ 
        Server lauscht nach eingehenden Verbindungen und oeffnet dann einen
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
            
"""
Programm Start.
Programm startet mit 2 Argumenten fuer die '__init__()' Funktion der Server
Klasse, der Ipv4 Adresse und dem Port des Servers.
"""
if (len(sys.argv) == 3):
    server = Server(sys.argv[1], int(sys.argv[2]))
    try:
        server.run()
    except KeyboardInterrupt as e:
        sys.exit("\nQuit Server")
else:
    sys.exit("Missing arguments\nUse IP-Adress and Port")