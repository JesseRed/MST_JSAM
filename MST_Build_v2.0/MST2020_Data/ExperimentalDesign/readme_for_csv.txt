
Block ... number of Block ... increasing number
Sequence ... the Sequence of keys that has to be pressed
timeOn ... Active duration during which the subject has to press the Sequence
       ... if timeOn is "-1" then the Active period ends when the Subject has entered one Sequence
               after this the timeOff Period begins
timeOff ... Pause duration after the active part of a Block, the Sequence is not shown during this time
endBlockPause ... Pause in seconds at the end of the Block ... normally for showing a message
endBlockMessage ... Message shown at the end of the Block
endBlockManualContinuation ... 0/1  ... if 1 ... next Block starts only after manual continuation 0 .. next Block starts automatically
startBlockPause ... pause in seconds in before the current Block (normally used to show a primer
startBlockPrimer ... the color of a rectangle that will be shown before the Block for the duration of the startBlockPause
showSingleKeys  .... 0= whole Sequence is shown, 1-x only a specific number of next keys are shown

Block;Sequence;timeOn;timeOff;endBlockPause;endBlockMessage;endBlockManualContinuation;startBlockPause;startBlockPrimer;showSingleKeys;
1;4-1-3-2-4-2-1-3;30;30;0;nachricht1;0;2;red;0;
2;4-1-3-2-4-2-1-3;30;30;0;nachricht2;0;2;red;1;
3;4-1-3-2-4-2-1-3;30;30;0;nachricht3;0;2;red;2;
4;4-1-3-2-4-2-1-3;30;30;0;nachricht4;0;2;red;0;
5;4-1-3-2-4-2-1-3;30;30;0;nachricht5;0;2;red;0;
6;4-1-3-2-4-2-1-3;30;30;0;nachricht6;0;2;red;0;
7;4-1-3-2-4-2-1-3;30;30;0;nachricht7;0;2;red;0;
8;4-1-3-2-4-2-1-3;30;30;0;nachricht8;0;2;red;0;
9;4-1-3-2-4-2-1-3;30;30;0;nachricht9;0;2;red;0;
10;4-1-3-2-4-2-1-3;30;30;0;nachricht10;0;2;red;0;
11;4-1-3-2-4-2-1-3;30;30;0;nachricht11;0;2;red;0;
12;4-1-3-2-4-2-1-3;30;30;0;nachricht12;0;2;red;0;


Colors for the primer ...
black	Solid black. RGBA is (0, 0, 0, 1).
blue	Solid blue. RGBA is (0, 0, 1, 1).
clear	Completely transparent. RGBA is (0, 0, 0, 0).
cyan	Cyan. RGBA is (0, 1, 1, 1).
gray	Gray. RGBA is (0.5, 0.5, 0.5, 1).
green	Solid green. RGBA is (0, 1, 0, 1).
grey	English spelling for gray. RGBA is the same (0.5, 0.5, 0.5, 1).
magenta	Magenta. RGBA is (1, 0, 1, 1).
red	    Solid red. RGBA is (1, 0, 0, 1).
white	Solid white. RGBA is (1, 1, 1, 1).
yellow	Yellow. RGBA is (1, 0.92, 0.016, 1), but the color is nice to look at!