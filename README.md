# MST_JSAM
This repository contains a unity implementation for different Sequence Learning Tasks

Die Experimente werden durch Parameter Files gesteuert (/Assets/ExperimentalDesign)

[Parameter File Beschreibung](https://github.com/JesseRed/MST_JSAM/blob/ddc98b4fe1aa9eeef53b7e2e9dca82bfd6d8d839/help_parameter.md "Help_parameter")

Mit dem Paradigmafile laessen sich beispielsweise die folgenden Paradigmen abbilden
- Manual Sequence Task (MST)
- SRTT 
- 8 Sequence learning Task (FRA)
Der Name des Files bestimmt seinen Aufruf 
z.B. FRA_Day1.csv (FRA wird im Menue angeklickt und erster Trainingstag wird eingegeben)
<br/><br/>

Nach Durchfuehrung des Experiments werden die Ergebnisse in /Assets/Data gespeichert 

Diese Files gehen anschliessend in die Analyse Pipeline
Die Analyse ist ein Python Program im Ordner analyse_csv


![alt text](https://github.com/JesseRed/MST_JSAM/blob/fe39e2adaa4318477821db67f844c46d678d8263/MSTv2/Menu.png "sdf")



# -------------------------------------
#!  Jenaer Planungsgespraeche 28.04.2020
""" ------------------------------------
outcomeparameter zu Berechnen
* Anstieg insgesamt
* Anstieg zum Maximum
* Maximum
* Gesamtzahl korrekter Sequenzen
* Veraenderung der Outcomeparameter von Tag_1 zu Tag_2
* Fehlerhafte Sequenzen pro Block

Ziele:
- Wie gut kann ich Lernerfolg mit unterschiedlichen Lernspielen testen
- Wie valide sind die verschiedenen Lernspiele fuer diese Frage
- Wie kann ich Lerntypen unterscheiden, was sind Einflussfaktoren

Teilung der Gruppe anhand der Outcomeparameter in 2 Gruppen im median und Untersuchung welche Unterschiede diese Gruppen aufweisen


std der Lernspiele fuer verschiende outcomeparameter an Tag1, Tag2 und Tag2-Tag1
        

Indentifikation verschiedener LErntypen

            Multiple Regressionsanalyse verschiedener Einflussfaktoren auf die outcomeparameter
            1... alles aus neuropsych 
            2... chunking
            3... Alter, Geschlecht
            4... Fehlerquote


    ich bekomme eine Tabelle mit den klinischen Daten der Probanden
    dann trage ich dort ein:
    1. Outcomeparamter 
    2. die erfolgreichen Sequenzen pro Block
    3. chunking ... Mass Q

    die Tabelle dient zur Visualisierung und Nachauswertung durch die Probanden


    """
