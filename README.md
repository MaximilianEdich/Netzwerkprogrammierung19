# "Who is the Boss?" - Netzwerkprogrammierung 2019
## Projekt

Dieses Programm ist Teil eines Projekts im Rahmen der Veranstaltung "Netzwerkprogrammierung" der Universität Bielefeld.
Ziel ist es mehrere gleichwertige Server so zusammenzuschließen, dass diese automatisch einen Master bestimmen. Dabei soll dieser Bestimmungsvorgang möglichst flexibel
sein und auch im Falle eines spontanen Serverausfalls einen neuen Master bestimmen.

## Verwendung

Das Python Script wird mittels python3 aufgerufen, wobei als zusätzliche Argumente die gewünschte IPv4 Adresse sowie die Portnummer mitgegeben werden müssen. Zudem können schon hier Scripte, welche auf den Standard Servern oder dem Master laufen sollen spezifiziert werden.

```
python3 netwerkprogrammierung_AP_medich.py <ip> <port> -ds <default script> <ds args> -ms <master script> <ms args>
```

`-ds` und `-ms` mit ihren nachfolgenden Argument sind optional und für die allgemeine Funktionsweise der Serverkommunikation nicht relevant.

Sobald der Server gestartet ist, können weitere Befehle eingegeben werden. Diese beginnen immer mit einem Minus. Nachfolgend sind diese aufgelistet.

`-h`: 			Ruft eine Auflistung aller Befehle auf. (help)

`-c <ip> <port>`: 	Baut eine Verbindung zum angegeben Server auf, sofern dieser erreichbar ist. (connect)

`-m`:			Gibt an, ob der Server der Master ist. (master)

`-t`:			Zeigt die Startzeit des Servers an. (time)

`-cn`:			Zeigt die Anzahl an Verbindungen an. (connection number)

`-cl`:			Listet alle Verbindungen auf. (connection list)

`-msg <text>`:		Sende Textnachricht an alle verbundenen Server. Die Empfänger geben diesen über ihre Konsole aus. Nützlich zum schnellen Prüfen besteheder Verbindungen. (message)

`-sd <script> <args>`:	Spezifiziert ein Skript, welches von Standard Servern ausgeführt wird. Die Argumente für das Skript müssen ggf. hier mitgegeben werden. (default script)

`-ms <script> <args>`:	Spezifiziert ein Skript, welches vom Master Server ausgeführt wird. Die Argumente für das Skript müssen ggf. hier mitgegeben werden. (master script)

`-loop <1/0>`:		Legt fest, ob das laufende Skript in einer Schleife wiederholt wird oder die Spezifikation nach dem nächsten Ablauf entfernt wird. Mit "1" wird die,  Schleife aktiviert, mit "0" deaktiviert. Standardmäßig ist die Schleife aktiviert. (script loop)

`-sslp <float>`:	Zeit, welche der Thread nach Ausführung des Skriptes schläft, bevor das Skript erneut ausgeführt wird. Der Standardwert beträgt 1. (script sleep)


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

### Quorum

Zunächst wird ein erster Server gestartet. Hier unter der Adresse 127.0.0.1:10000
```
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.1 10000

```
Analog werden zwei weitere Server gestartet.
```
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.1 11000
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.1 12000

```
Nun können der erste und zweite Server verbunden werden. Dazu muss in einem der Server, hier im zweiten, der Connect Befehl `-c` ausgeführt werden:
```
-c 127.0.0.1 10000

```
Bei Erfolg wird die Socket in der Kommandozeile angezeigt. Diese kann auch über den Befehl `-cl` mit allen anderen Verbindungen angezeigt werden.
```
<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 49850), raddr=('127.0.0.1', 10000)>

```

Über `-m` prüfen wir, welcher der Server der aktuelle Master ist und stellen fest, dass dies beim ersten Server der Fall ist.
Über exakt die selbe Eingabe wie oben können wir auch den dritten Server mit dem ersten Verbinden. Das Beenden des Servers 3 über einen Keyboard Interrupt mit `Strg + C`hat dabei keine Auswirkung auf den Masterstatus, wir sehen jedoch bei Server 1 und 2 eine Meldung über den Abbruch einer Verbindung.
Bei einem erneuten Start von Server 3 können wir ihn diesmal auch mit Server 2 verbinden. Dieser wird ihn aber an den Master weiterleiten und die erste Verbindung wieder kappen. Der Master koordiniert dann ein Verbinden von allen Servern zu dem Neuen hin.

### Server Skripte

Ein Server kann mit zusätzlichen Argumenten auch sofort mit einem ausführbaren Skript gestartet werden.
```
python3 netzwerkprogrammierung_AP_medich.py 127.0.0.1 10000 -ds default_script.py -ms master_script.py
```

Der Output der Skripte wird dabei in die Kommandozeile ausgegeben. Die Wahl des Skripts wird durch den Master Status entschieden. Das Skript wird unendlich oft in einer Schleife ausgeführt. Dies können wir jedoch abschalten, wodurch die Referenz auf das Skript gelöscht wird:

```
-loop 0
```

Bei Bedarf können wir das Skript zu einem späteren Zeitpunk wieder starten:

```
-ds default_script.py
```

Falls das Skript zu häufig Aufgaben gibt, können wir dem Programm Pausen vorschreiben:

```
-sslp 10
```

Nun findet nur noch alle 10 Sekunden eine Ausgabe statt.

## Lizenz

Das Projekt ist unter der GNU General Public License v3.0 lizensiert und auf GitHub veröffentlicht. Das Projekt darf somit verbreitet, modifiziert und beliebig genutzt werden, sofern die Lizenz beibehalten wird. Genauere lizenzspezifische Informationen zu der GNU General Public License v3.0 finden sich hier: https://github.com/MaximilianEdich/Netzwerkprogrammierung19/blob/master/LICENSE
