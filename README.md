# MST_JSAM
This repository contains the following learn paradigm as unity games and the currently available data
- Manual Sequence Task (MST)
- SRTT 
- 8 Sequence learning Task (FRA)


![alt text](https://github.com/JesseRed/MST_JSAM/blob/fe39e2adaa4318477821db67f844c46d678d8263/MSTv2/Menu.png "sdf")

Gesteuert wird ueber die csv Paradigmen Files im Ornder /Assets/ExperimentalDesign
Der Name des Files bestimmt seinen Aufruf 
z.B. FRA_Day1.csv (FRA wird im Menue angeklickt und erster Trainingstag wird eingegeben)
<br/><br/>



|Block|Sequence|timeOn|timeOff|endBlockPause|endBlockMessage|endBlockManualContinuation|startBlockPause|startBlockPrimer|showSingleKeys|singleSequenceFeedback|
|----:|:-----------------:|:----:|:----:|:----:|:-------------:|:----:|:----:|:----:|:-----:|:----------------:|
|1|4-1-3-2-4-2-1-3|-1|2|5|nachricht2|0|2|red|1|show_smiley_red|
|2|3-2-4-1-3-2-4-1|-1|2|5|nachricht2|0|2|blue|1|next_sequence|
|3|3-2-4-1-3-2-4-1|-1|0|0|nachricht2|0|2|blue|1|show_smiley_red|
|4|4-1-3-2-4-2-1-3|-1|0|0|nachricht1|0|2|red|1|show_smiley_red|
|5|4-1-3-2-4-2-1-3|-1|0|0|nachricht1|0|2|red|1|show_smiley_red|

# Beschreibung
## Block [int]
> Nummer des Blocks
## Sequence 
> die Sequenz die Gezeigt werden soll muss mit "-" getrennt sein
## timeOn [int]
> Zeit die der Proband hat um die Sequenz einzutippen
> eine Zahl kleiner als 0 bewirkt, dass die Sequenz genau einmal gezeigt wird
## timeOff
> Zeit der Pause nach einem Block in welchem die endBlockMessage gezeigt wird
* endBlockPause
* endBlockMessage
* endBlockManualContinuation
* startBlockPause  .... Anzahl an Sekunden Pause vor Beginn eines neuen Blocks ... In dieser ZEit wird der startBlockPrimer gezeigt
## startBlockPrimer .... 
>Wird waehrd der startBlockPause gezeigt (stellt eine Farbe dar) erlaubt sind
* black
  * blue
  * clear
  * cyan
  * gray
  * green
  * grey
  * magenta
  * red
  * white
  * yellow
* showSingleKeys
* singleSequenceFeedback
* 


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
