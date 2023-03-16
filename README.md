- [rdwapihulpmiddelen python versie](#rdwapihulpmiddelen-python-versie)
  - [rdw.py](#rdwpy)
  - [rdwfinder.py](#rdwfinderpy)
  - [missing.py](#missingpy)

# rdwapihulpmiddelen python versie
Python RDW API hulpmiddelen voor de IONIQ 5, misschien dat het ook gebruikt kan worden ter inspiratie voor andere auto's. Maar kan natuurlijk ook gebruikt worden om nieuwe kentekens te vinden die nog niet op naam staan.

Voor de perl versie, [zie hier](https://github.com/ZuinigeRijder/rdwapihulpmiddelen).

Er zijn 3 python scripts:
- rdw.py: haalt IONIQ 5 kentekens op naam op
- rdwfinder.py: vind kentekens in de opgegeven range (hoeven nog niet op naam te staan)
- missing.py: haal de kentekens in missing.txt op en laat de nieuwe (nog niet opgehaalde) kentekens zien.

De tools worden gedraaid op Windows 10 en geschikt voor Python 3.9, Python versie die ik gebruik: 3.9.13

De python scripts gebruiken wget om data op te halen, wget versie die ik gebruik:
````
wget --version
GNU Wget 1.20.3 built on mingw32.
````

En ook curl wordt gebruikt voor https, curl versie die ik gebruik:
````
curl --version
curl 7.83.1 (Windows) libcurl/7.83.1 Schannel
Release-Date: 2022-05-13
Protocols: dict file ftp ftps http https imap imaps pop3 pop3s smtp smtps telnet tftp
Features: AsynchDNS HSTS IPv6 Kerberos Largefile NTLM SPNEGO SSL SSPI UnixSockets
````

## rdw.py
Opgehaalde kentekens worden opgeslagen onder sub-map kentekens/ zodat alleen de delta kentekens opgehaald worden.
P.S.
- crëeer de sub-map kentekens/ handmatig
- de eerste keer zul je dus véél kentekens ophalen (meer dan 3000 voor de IONIQ 5)

3 aanroepmogelijkheden:
- zonder parameters: python rdw.py
- samenvatting: python rdw.py summary
- overzicht: python rdw.py overview

## rdwfinder.py
Vindt kenteken in een range, handig om kentekens nog niet op naam te vinden. Bijvoorbeeld:
- python rdwfinder.py R LF 510 520 1

P.S.
Het is mogelijk dat je IP-adres geblocked gaat worden, wanneer je teveel opvragingen doet.
Hoewel er geprobeerd wordt om niet teveel opvragingen te doen.
Bij voorkeur gebruik je een VPN om dit te voorkomen.

## missing.py
Kentekens nog niet op naam kun je handmatig in missing.txt zetten die gevonden zijn door rdwfinder. Daarna running van python missing.py zonder parameters.

P.S. rdw.py zal ook de output van missing.outfile.txt meenemen in de resultaten.
