using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System.IO;
using TMPro;


public class Events : MonoBehaviour
{

    public GameSession gameSession;
    public bool isActive = false;
    private bool isIntro = true;
    private GameSession.Block currentBlock;

    public List<Vector3Int> activeSequence;

    public List<Vector3Int> resultsPresented = new List<Vector3Int>();
    public List<Vector3Int> resultsPressed = new List<Vector3Int>();


    private int buttonPressed;
    // Use this for initialization
    private List<int> resultButtonPressed = new List<int>();
    private GameObject waitObject;
    private TextMeshProUGUI waitTMPText;
    private GameObject nextObject;
    private TextMeshProUGUI nextTMPText;
    //  private GameObject waitObject;
    private GameObject introObject;
    private TextMeshProUGUI introTMPText;
    //  private GameObject waitObject;

    private GameObject sequenceObject;
    private TextMeshProUGUI sequenceTMPText;
    // private GameObject sequenceObject;
    private GameObject sequenceUnderlineObject;
    private TextMeshProUGUI sequenceUnderlineTMPText;
    //  private GameObject waitObject;
    private int currentTargetNum;
    private bool isButtonPressedInFrame = false;
    private bool isButtonPressedProcessed = false;
    private int lastButtonPressed = -1;
    private int tmpButtonPressed = -1;
    public AudioClip audioClipSuccess;
    public AudioClip audioClipFailure;
    public AudioSource audioSource;
    public int currentBlockIdx;
    private int eventNumInBlock = 0;
    private float currentBlockStartTime;
    private float lastButtonPressedTime;
    private string currenttextnachricht = "";
    private string sequence = "";
    private bool errorInBlock = false;
    private GameObject panelPrimer;
    private GameObject rawimagesmileygreen;
    private GameObject rawimagesmileyred;
    void Awake()
    {
        print("awake");
        // hole mir als erstes die Sequencedaten die im csv File im Files verzeichis
        // gespeichert sind und an das CSVParsing object mit dem Script CSVParsing gekoppelt sind
        Application.targetFrameRate = 120;
        //timeOfApplicationStart = Time.realtimeSinceStartup;
        //print("Fertig");
        gameSession = FindObjectOfType<GameSession>();
        rawimagesmileygreen = GameObject.Find("RawImageSmileyGreen");
        rawimagesmileygreen.SetActive(false);
        rawimagesmileyred = GameObject.Find("RawImageSmileyRed");
        rawimagesmileyred.SetActive(false);
        waitObject = GameObject.Find("WaitText");
        waitTMPText = waitObject.GetComponent<TextMeshProUGUI>();
        
        nextObject = GameObject.Find("NextText");
        nextTMPText = nextObject.GetComponent<TextMeshProUGUI>();
        
        sequenceObject = GameObject.Find("SequenceText");
        sequenceTMPText = sequenceObject.GetComponent<TextMeshProUGUI>();
        panelPrimer = GameObject.Find("PanelPrimer");
        panelPrimer.SetActive(false);
        sequenceTMPText.fontSize=20;

        int max_seq_length = 0;
        foreach (GameSession.Block block in gameSession.playerData.paradigmaBlocks)
        {   
            //print(block.expSequence.Count);
            if (block.expSequence.Count>max_seq_length){
                max_seq_length = block.expSequence.Count;
            }
        }
        //print("max_seq_length =" + max_seq_length);
        if (max_seq_length<=6){ sequenceTMPText.fontSize=100;}
        if (max_seq_length>=7 && max_seq_length<9 ){ sequenceTMPText.fontSize=70;}
        if (max_seq_length>=9 && max_seq_length<13 ){ sequenceTMPText.fontSize=50;}
        if (max_seq_length>=13){ sequenceTMPText.fontSize=40;}

        // sequenceUnderlineObject = GameObject.Find("SequenceUnderlineText");
        // sequenceUnderlineTMPText = sequenceUnderlineObject.GetComponent<TextMeshProUGUI>();
        introObject = GameObject.Find("IntroText");
        introTMPText = introObject.GetComponent<TextMeshProUGUI>();
        audioSource.clip = audioClipSuccess;
        //StartCoroutine(startPresentation());

    }

    // Update is called once per frame
    void Update()
    {

        if (Input.GetKeyDown("escape"))
        {
            print("now quit");
            Application.Quit();
        }
        if (isIntro)
        {
            if (Input.GetKeyDown("space"))
            {
                introTMPText.SetText("");
                StartCoroutine(startPresentation());
                lastButtonPressedTime = Time.time;
            }
        }

        if (isActive)
        {
            if (Input.GetKeyDown("f")) { tmpButtonPressed = 4; } // Zeigefinger
            if (Input.GetKeyDown("g")) { tmpButtonPressed = 3; } // Mittelfinger
            if (Input.GetKeyDown("h")) { tmpButtonPressed = 2; } // Ringfinger
            if (Input.GetKeyDown("j")) { tmpButtonPressed = 1; } // kleiner Finger
            if (Input.GetButtonDown("Fire1")) { tmpButtonPressed = 4; print("Fire1"); } // Zeigefinger
            if (Input.GetButtonDown("Fire2")) { tmpButtonPressed = 3; print("Fire2"); } // Zeigefinger
            if (Input.GetButtonDown("Fire3")) { tmpButtonPressed = 2; print("Fire3"); } // Zeigefinger
            if (Input.GetButtonDown("Fire4")) { tmpButtonPressed = 1; print("Fire4"); } // Zeigefinger

            // wenn einer der 4 nummern gepressed wurde UND (es nicht der gleiche ist oder mehr als 50 ms vergangen)
            if (tmpButtonPressed>0 && (tmpButtonPressed != lastButtonPressed || Time.time-lastButtonPressedTime>0.05))
            {
                audioSource.Play();
                ButtonPressed(tmpButtonPressed);
                isButtonPressedInFrame = true;
                lastButtonPressedTime = Time.time;
                tmpButtonPressed = 0;
            }
            
        }
    }


    private IEnumerator startPresentation()
    {
        currentBlockIdx = 0;
        foreach (GameSession.Block block in gameSession.playerData.paradigmaBlocks)
        {
            currentBlockIdx++;
            currentBlock = block;
            currentBlockStartTime = Time.time;
            errorInBlock = false;
            //print(block.expSequence);
            currenttextnachricht = block.expEndBlockMessage;
            sequence = block.expStartBlockPrimer;
            if (currentBlock.expStartBlockPause>0){
                yield return StartCoroutine(startBlockPrimer(block.expStartBlockPause, block.expStartBlockPrimer));
            }
            if (currentBlock.expTimeOn>0){
                yield return StartCoroutine(startBlockActiveTime());
            }
            if (currentBlock.expTimeOn<=0){
                yield return StartCoroutine(startBlockActiveOneSequence());
            }
            if (currentBlock.expEndBlockPause>0){
                yield return StartCoroutine(startBlockFeedback(block.expEndBlockPause, block.expSingleSequenceFeedback));
            }

            if (currentBlock.expTimeOff>0){
                yield return StartCoroutine(startBlockPassive(currenttextnachricht));
            }
            gameSession.playerData.SaveDataAsCSV("unvollstaendig");

        }
        // alles abgeschlossen  ... speichere nun die Daten
        gameSession.playerData.SaveDataAsCSV("fertig");
        introTMPText.SetText("Experiment abgeschlossen!");
        //panelEnde.SetActive(true);
        yield return new WaitForSeconds(5);
        Application.Quit();
    }

    IEnumerator startBlockActiveOneSequence()
    {
        isActive = true;
        float starttime = Time.time;
        print(currentBlock.expShowKeys);
        // Active Period by time
        for (int i = 0; i < currentBlock.expSequence.Count; i++)
        {
            currentTargetNum = currentBlock.expSequence[i];
            string seq = createSequenceString(i);
            sequenceTMPText.SetText(seq);
            while (!isButtonPressedInFrame)
            {
                yield return null; //new WaitForEndOfFrame();
            }
            isButtonPressedInFrame = false;
        }
        

        sequenceTMPText.SetText("");
    }
    IEnumerator startBlockActiveTime()
    {
        isActive = true;
        float starttime = Time.time;
        bool toExit = false;
        print(currentBlock.expTimeOn);
        // Active Period by time

        while (Time.time  - starttime < currentBlock.expTimeOn){
        for (int i = 0; i < currentBlock.expSequence.Count; i++)
        {
            currentTargetNum = currentBlock.expSequence[i];
            string seq = createSequenceString(i);
            sequenceTMPText.SetText(seq);
            while (!isButtonPressedInFrame)
            {
                yield return null; //new WaitForEndOfFrame();
                if (Time.time  - starttime >currentBlock.expTimeOn){
                    toExit = true;
                    break;
                }
            }
            isButtonPressedInFrame = false;
            if (toExit){ break; }
        }
        }
        

        sequenceTMPText.SetText("");
    }

    public void ButtonPressed(int num)
    { //4 = Zeigefinger/f, 3 = Mittelfinger/g, 2= Ringfinger/h, 1 = kleinerFinger/j
        //Add button to playerdata
        //show effect on screen
        int isHit;
        if (num == currentTargetNum)
        {
            print("success");
            audioSource.clip = audioClipSuccess;
            isHit = 1;
        }
        else
        {
            audioSource.clip = audioClipFailure;
            isHit = 0;
            errorInBlock = true;
        }
        eventNumInBlock++;
        audioSource.Play();
        print("button pressed was : " + num);
        lastButtonPressed = num;
        gameSession.playerData.AddData(currentBlockIdx, eventNumInBlock, Time.time-currentBlockStartTime, isHit,currentTargetNum,num, sequence);
    }

    private string createSequenceString(int num_active)
    {
        string seq = "<cspace=0.2em>";

        if (currentBlock.expShowKeys<=0){
        for (int i = 0; i < currentBlock.expSequence.Count; i++)
        {
            seq = seq + "-";
            if (num_active == i)
            {
                seq = seq + "<size=130%><u>";
                currentTargetNum = currentBlock.expSequence[i];
            }
            seq = seq + currentBlock.expSequence[i].ToString();
            if (num_active == i)
            {
                seq = seq + "</u><size=100%>";
            }

        }
        }

        if (currentBlock.expShowKeys>0){
            int end_key = num_active + currentBlock.expShowKeys;
            if (end_key>currentBlock.expSequence.Count){ end_key = currentBlock.expSequence.Count; };
            for (int i = num_active; i < end_key; i++)
            {
                seq = seq + "-";
                if (num_active == i)
                {
                    seq = seq + "<size=130%><u>";
                    currentTargetNum = currentBlock.expSequence[i];
                }
                seq = seq + currentBlock.expSequence[i].ToString();
                if (num_active == i)
                {
                    seq = seq + "</u><size=100%>";
                }

            }
        }
        
        seq = seq + "-";
        //<size=60%><cspace=0.2em>-4-<u>3</u>- 2-1-<mark=#ffff00aa>4</mark>
        return seq;
    }
    IEnumerator startBlockPassive(string textnachricht)
    {
        isActive = false;
        introTMPText.text = "Pause!\n weiter in ...";
        // die textnachricht ist sowohl Nachricht wie auch keyword    
        switch (textnachricht)
        {
            case "show_smiley_red":
                rawimagesmileyred.SetActive(true);
                break;
            case "show_smiley_green":
                rawimagesmileygreen.SetActive(true);
                break;
            default:
                nextTMPText.text = textnachricht;
                break;
        }
        for (int i = currentBlock.expTimeOff; i >= 0; i--)
        {
            waitTMPText.SetText(i.ToString());
            yield return new WaitForSeconds(1);
        }
        introTMPText.SetText("");
        waitTMPText.SetText("");
        nextTMPText.SetText("");
        rawimagesmileygreen.SetActive(false);
        rawimagesmileyred.SetActive(false);
    }

    IEnumerator startBlockPrimer(int duration, string primer)
    {
        isActive = false;
        // introTMPText.text = "Pause!";
        // yield return new WaitForSeconds(1);
        introTMPText.text = "next Sequence\n ";
        //introTMPText.text = singleSequenceFeedback;
        waitTMPText.SetText("");
        nextTMPText.SetText("");
        panelPrimer.SetActive(true);
        Image img = panelPrimer.GetComponent<UnityEngine.UI.Image>();
        if (currentBlock.expStartBlockPrimer=="black"){img.color = Color.black; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="blue"){img.color = Color.blue; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="clear"){img.color = Color.clear; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="cyan"){img.color = Color.cyan; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="gray"){img.color = Color.gray; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="green"){img.color = Color.green; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="grey"){img.color = Color.grey; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="magenta"){img.color = Color.magenta; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="red"){img.color = Color.red; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="white"){img.color = Color.white; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        if (currentBlock.expStartBlockPrimer=="yellow"){img.color = Color.yellow; } // new Color(0.3f, 0.4f, 0.6f, 0.8f);
        
        yield return new WaitForSeconds(currentBlock.expStartBlockPause);
        introTMPText.SetText("");
        waitTMPText.SetText("");
        nextTMPText.SetText("");
        panelPrimer.SetActive(false);
    }

    IEnumerator startBlockFeedback(int duration, string singleSequenceFeedback)
    {
        isActive = false;
        // introTMPText.text = "Pause!";
        // yield return new WaitForSeconds(1);
        introTMPText.text = "Feedback\n ";
        //introTMPText.text = singleSequenceFeedback;
        waitTMPText.SetText("");
        nextTMPText.SetText("");
        //panelPrimer.SetActive(true);
        print("errorInBlock: " + errorInBlock);
        // show the SeqenceFeedback after each Sequence
        switch (singleSequenceFeedback)
        {
            case "show_smiley_red":
                if (errorInBlock){
                    rawimagesmileyred.SetActive(true);
                }
                break;
            case "show_smiley_green":
                if (!errorInBlock){
                    rawimagesmileygreen.SetActive(true);
                }
                break;
            default:
                introTMPText.text = singleSequenceFeedback;
                break;
        }

        yield return new WaitForSeconds(currentBlock.expEndBlockPause);
        introTMPText.SetText("");
        waitTMPText.SetText("");
        nextTMPText.SetText("");
        panelPrimer.SetActive(false);
        rawimagesmileygreen.SetActive(false);
        rawimagesmileyred.SetActive(false);
    }

}
