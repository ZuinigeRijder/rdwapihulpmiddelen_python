- [rdwapihulpmiddelen python versie](#rdwapihulpmiddelen-python-versie)
- [rdw.py](#rdwpy)
- [rdw\_utils.py](#rdw_utilspy)

# rdwapihulpmiddelen python versie
Python RDW API hulpmiddelen voor de IONIQ 5, misschien dat het ook gebruikt kan worden ter inspiratie voor andere auto's. Maar kan natuurlijk ook gebruikt worden om nieuwe kentekens te vinden die nog niet op naam staan.

Voor de perl versie, [zie hier](https://github.com/ZuinigeRijder/rdwapihulpmiddelen). Echter dat is niet aangepast aan het feit dat RDW sinds 12 april 2023 ook kentekens nog niet op naam teruggeeft.

Er is 1 python script:
- rdw.py: haalt IONIQ 5 kentekens op

De tools worden gedraaid op Windows 10 en geschikt voor Python 3.9, Python versie die ik gebruik: 3.9.13

# rdw.py

3 aanroepmogelijkheden:
- zonder parameters: python rdw.py
- samenvatting: python rdw.py summary
- overzicht: python rdw.py overview

Aangezien per 12 april 2023 de RDW ook kentekens nog niet op naam teruggeeft, heb ik het script drastisch moeten herschrijven. Aan de andere kant is het script daar ook door versimpeld.
Er zijn 3 input/output bestanden:
- exported.txt
- nognietopnaam.txt
- opnaam.txt

Ook wordt er een backup gemaakt van deze files met een datum/tijd in de naam, bijvoorbeeld:
- nognietopnaam.txt.2023.04.21_09.42.25.txt

Wanneer er niets gewijzigd is in de backup file, wordt de backup file weer verwijderd.

Via RDW worden alle IONIQ5 kentekens opgehaald met de metadata in x.kentekens. Wanneer deze niet in exported.txt, nognietopnaam.txt of opnaam.txt voorkomen, wordt deze aan het einde als nieuw kenteken getoond. Ook wordt er getoond wanneer een kenteken van nognietopnaam.txt naar opnaam.txt of naar exported.txt verhuisd is. Aan het eind wordt dan de volgende delta's gerapporteerd bij "python rdw.py" zonder parameters:
- Eerder gevonden kenteken op naam gezet
- Nieuw kenteken op naam gezet
- Nieuw kenteken nog niet op naam
- Nieuw kenteken geexporteerd

Voorbeelden van uitvoer kun je op tweakers ["Het Hyundai Ioniq 5 leveringen topic"](https://gathering.tweakers.net/forum/list_messages/2073194/2?data%5Bfilter_pins%5D=1) terugvinden.


# rdw_utils.py

Hulp functies, gebruikt door rdw.py, onder andere om de juiste variant te vinden aan de hand van fiscale prijs, kleur en type.