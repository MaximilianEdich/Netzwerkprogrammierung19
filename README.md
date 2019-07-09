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
dem Neuen. Anschließend wird überprüft, ob der neue Server nach der gegebenen Bedingung der neue Master wird. Fall sich der Master ändert, sendet der neue Master eine entsprechende Benachrichtigung, um das Wissen über den aktuellen Master im Netz zu teilen.
Verbindet sich stattdessen der neue Server nicht mit dem Masterserver, gibt der entsprechende Server dem neuen Server die Daten zum Master. Danach wird ein Verbindungsaufbau
zum Master getätigt und der oben beschriebene Vorgang läuft ab.

Ein anderes Szenraio, bei dem gegebenenfalls ein neue Master bestimmt werden muss, ist die Verringerung der Serverzahl. Wird ein beliebiger Server vom Netz entfernt, so
ändert sich nichts. Wird der Master entfernt, muss ein neuer bestimmt werden. Dabei werden die Vermerke über den bisherigen Master in allen gelöscht, sobald festgestellt wird,
dass die Verbindung nicht mehr besteht. Anschließend erfolgt ein neuer Vergleich der Masterbedingung unter den verbliebenen Servern, indem jeder Server zum Master wird. Nun wird mit jeder Verbindung überprüft, ob der eigene Master Status erhalten bleibt oder nicht. Am Ende bleibt nur noch ein einzelner Master Server nach nur einer Iteration durch die Serverliste.

Werden alle Server bis auf den Master vom Netz genommen, so verliert auch der Master Server seinen Status und wird zu einem gewöhnlichen Server.

## Beispiel

Zunächst wird ein erster Server gestartet. Hier unter der Adresse 127.0.0.1:10001
```
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.1 10001

```
Analog werden zwei weitere Server gestartet.
```
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.20 10002
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.30 10003

```
Nun können der erste und zweite Server verbunden werden. Dazu muss in einem der Server, hier im zweiten, der Connect Befehl `-c` ausgeführt werden:
```
-c 127.0.0.1 10001

```
Bei Erfolg wird die Socket in der Kommandozeile angezeigt. Diese kann auch über den Befehl `-cl` mit allen anderen Verbindungen angezeigt werden.
```
<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 49850), raddr=('127.0.0.1', 10001)>

```

Über `-m` prüfen wir, welcher der Server der aktuelle Master ist und stellen fest, dass dies beim ersten Server der Fall ist.
Über exakt die selbe Eingabe wie oben können wir auch den dritten Server mit dem ersten Verbinden. Das Beenden des Servers 3 über `Strg + C`hat dabei keine Auswirkung auf den Masterstatus, wir sehen jedoch bei Server 1 und 2 eine Meldung über den Abbruch einer Verbindung.
Bei einem erneuten Start von Server 3 können wir ihn diesmal auch mit Server 2 verbinden. Dieser wird ihn aber an den Master weiterleiten und die erste Verbindung wieder kappen. Der Master koordiniert dann ein Verbinden von allen Servern zu dem Neuen hin.

## Lizenz

Das Projekt ist unter der GNU General Public License v3.0 lizensiert und auf GitHub veröffentlicht. Das Projekt darf somit verbreitet, modifiziert und beliebig genutzt werden, sofern die Lizenz beibehalten wird. Genauere lizenzspezifische Informationen zu der GNU General Public License v3.0 finden sich hier: https://github.com/MaximilianEdich/Netzwerkprogrammierung19/blob/master/LICENSE
