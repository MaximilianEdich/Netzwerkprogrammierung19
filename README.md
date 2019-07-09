# "Who is the Boss?" - Netzwerkprogrammierung 2019
## Projekt

Dieses Programm ist Teil eines Projekts im Rahmen der Veranstaltung "Netzwerkprogrammierung" der Universität Bielefeld.
Ziel ist es mehrere gleichwertige Server so zusammenzuschließen, dass diese automatisch einen Master bestimmen. Dabei soll dieser Bestimmungsvorgang möglichst flexibel
sein und auch im Falle eines spontanen Serverausfalls einen neuen Master bestimmen.

## Verwendung

Das Python Script wird mittels python3 aufgerufen, wobei als zusätzliche Argumente die gewünschte IPv4 Adresse sowie die Portnummer mitgegeben werden müssen.
Sobald der Server gestartet ist, können weitere Befehle eingegeben werden. Diese beginnen immer mit einem Minus. Nachfolgend sind diese aufgelistet.

`-h`: 			Ruft eine Auflistung aller Befehle auf.
`-c <ip> <port>`: 	Baut eine Verbindung zum angegeben Server auf, sofern dieser erreichbar ist.
`-m`:			Gibt an, ob der Server der Master ist.
`-t`:			Zeigt die Startzeit des Servers an.
`-cn`:			Zeigt die Anzahl an Verbindungen an.
`-cl`:			Listet alle Verbindungen auf.

## Funktionsweise

Sobald sich zwei Server verbinden, sind sie zunächst gleichwertig. Durch eine frei konfigurierbare Funktion wird einer der beiden Server als Master ermittelt. Standardmäßig
wird hierfür die Serverstartzeit verwendet, wobei der ältere Server als Master bestimmt wird. Der andere Server bekommt lediglich vermerkt, wer der Master ist.
Wenn sich nun ein dritter Server mit dem Master verbindet, sendet der Master die Verbindungsdaten zum neuen Server an alle Bisherigen. Dadurch verbinden sich alle Server mit
dem Neuen. Anschließend wird überprüft, ob der neue Server nach der gegebenen Bedingung der neue Master wird.
Verbindet sich stattdessen der neue Server nicht mit dem Masterserver, gibt der entsprechende Server dem neuen Server die Daten zum Master. Danach wird ein Verbindungsaufbau
zum Master getätigt und der oben beschriebene Vorgang läuft ab.

Ein anderes Szenraio, bei dem gegebenenfalls ein neue Master bestimmt werden muss, ist die Verringerung der Serverzahl. Wird ein beliebiger Server vom Netz entfernt, so
ändert sich nichts. Wird der Master entfernt, muss ein neuer bestimmt werden. Dabei werden die Vermerke über den bisherigen Master in allen gelöscht, sobald festgestellt wird,
dass die Verbindung nicht mehr besteht.

Werden alle Server bis auf den Master vom Netz genommen, so verliert auch der Master Server seinen Status und wird zu einem gewöhnlichen Server.
