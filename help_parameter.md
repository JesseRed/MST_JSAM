# Paradigma File

Das Experiment wird durch ein Paradigma File im csv Format gesteuert.
## Speicherort
Gesteuert wird ueber die csv Paradigmen Files im Ornder /Assets/ExperimentalDesign

## Benennung des Files und Auswahl im Experiment:
Der Name des Files bestimmt seinen Aufruf 
Bsp: FRA_Day1.csv (FRA wird im Menu angeklickt und erster Trainingstag wird eingegeben)
<br/><br/>






|Block|Sequence|timeOn|timeOff|endBlockPause|endBlockMessage|endBlockManualContinuation|startBlockPause|startBlockPrimer|showSingleKeys|singleSequenceFeedback|
|----:|:-----------------:|:----:|:----:|:----:|:-------------:|:----:|:----:|:----:|:-----:|:----------------:|
|1|4-1-3-2-4-2-1-3|-1|2|5|nachricht2|0|2|red|1|show_smiley_red|
|2|3-2-4-1-3-2-4-1|-1|2|5|nachricht2|0|2|blue|1|next_sequence|
|3|3-2-4-1-3-2-4-1|-1|0|0|nachricht2|0|2|blue|1|show_smiley_red|
|4|4-1-3-2-4-2-1-3|-1|0|0|nachricht1|0|2|red|1|show_smiley_red|
|5|4-1-3-2-4-2-1-3|-1|0|0|nachricht1|0|2|red|1|show_smiley_red|

# Beschreibung
> Die Namen der Spalten koennen veraendert werden ... es ist nur ihre Reihenfolge Wichtig
## 1. Block [int]
> Nummer des Blocks, aufsteigende Anzahl
Bsp: 2
## 2. Sequence [string]
> die Sequenz die Gezeigt werden soll muss mit "-" getrennt sein

Bsp: 4-1-3-2-4-2-1-3

## 3. showSingleKeys [0,1]
> 0 = Sequenz wird in ihrer vollen Laenge auf dem Bildschirm dargestellt <br>
> 1 = nur das Zeichen das als naechstes gedruckt werden soll wird gezeigt

## 4. startBlockPause  [int] 
> Anzahl an Sekunden Pause vor Beginn eines neuen Blocks ... In dieser ZEit wird der startBlockPrimer gezeigt
## 5. startBlockPrimer [string]
> Wird waehrd der startBlockPause gezeigt (stellt eine Farbe dar) erlaubt sind
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

## 6. timeOn [int]
> Zeit die der Proband hat um die Sequenz einzutippen
> 
eine Zahl kleiner als 0 bewirkt, dass die Sequenz genau einmal gezeigt wird

Bsp: 2

## 7. feedbacktime [int]
> Zeit der Pause nach einem Block in welchem die endBlockMessage gezeigt wird, die Sequenz ist in dieser Zeit nicht zu sehen
> Es wird ein Counter gezeigt der diese Anzahl von Sekunden herunter zaehlt

Bsp: 2
## 8. singleSequenceFeedback [sting]
> Feedback fuer den Probanden ueber die zuletzt durchgefuehrte Sequenz

Es wird geprueft ob der uebergebene String ein Spezialstring ist der besonders verarbeitet wird, ansonsten wird der String an sich angezeigt
* show_smiley_red = es wird ein roter trauriger Smiley gezeigt aber nur wenn ein Fehler gemacht wurde
* show_smiley_green = es wird ein gruener Smiley gezeigt aber nur wenn die Sequenz korrekt war

es koennen noch mehr spezialkeys im IEnumerator startBlockPassive(string textnachricht) eingefuegt werden im Events.cs File

## 9. endBlockPause [int]
> Zeit der Pause nach einem Block in welchem das SingleSequenceFeedback gezeigt wird

Bsp: 2
## 10. endBlockMessage [string]
> Nachricht die in der Zeit des timeOff gezeigt wird

Bsp: naechste Sequence kommt gleich
## 11. endBlockManualContinuation [0,1]
> 0 = der naechste Block startet ohne manuelle Beststaetigung des Nutzers
> 1 = der naechste Block startet erst nach druck der Space taste

