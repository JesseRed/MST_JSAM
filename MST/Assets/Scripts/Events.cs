using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
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

    void Awake()
    {
        print("awake");
        // hole mir als erstes die Sequencedaten die im csv File im Files verzeichis
        // gespeichert sind und an das CSVParsing object mit dem Script CSVParsing gekoppelt sind
        Application.targetFrameRate = 120;
        //timeOfApplicationStart = Time.realtimeSinceStartup;
        //print("Fertig");
        gameSession = FindObjectOfType<GameSession>();
        waitObject = GameObject.Find("WaitText");
        waitTMPText = waitObject.GetComponent<TextMeshProUGUI>();
        sequenceObject = GameObject.Find("SequenceText");
        sequenceTMPText = sequenceObject.GetComponent<TextMeshProUGUI>();
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
            yield return StartCoroutine(startBlockActive());
            yield return StartCoroutine(startBlockPassive());
            gameSession.playerData.SaveDataAsCSV("unvollstaendig");

        }
        // alles abgeschlossen  ... speichere nun die Daten
        gameSession.playerData.SaveDataAsCSV("fertig");
        introTMPText.SetText("Experiment abgeschlossen!");
        //panelEnde.SetActive(true);
        yield return new WaitForSeconds(5);
        Application.Quit();
    }

    IEnumerator startBlockActive()
    {
        isActive = true;
        float starttime = Time.time;
        bool toExit = false;
        print(currentBlock.expTimeOn);
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
        }
        eventNumInBlock++;
        audioSource.Play();
        print("button pressed was : " + num);
        lastButtonPressed = num;
        gameSession.playerData.AddData(currentBlockIdx, eventNumInBlock, Time.time-currentBlockStartTime, isHit,currentTargetNum,num);
    }

    private string createSequenceString(int num_active)
    {
        string seq = "<cspace=0.2em>";
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
        seq = seq + "-";
        //<size=60%><cspace=0.2em>-4-<u>3</u>- 2-1-<mark=#ffff00aa>4</mark>
        return seq;
    }
    IEnumerator startBlockPassive()
    {
        isActive = false;
        // introTMPText.text = "Pause!";
        // yield return new WaitForSeconds(1);
        introTMPText.text = "Pause!\n weiter in ...";
        for (int i = currentBlock.expTimeOff; i >= 0; i--)
        {
            waitTMPText.SetText(i.ToString());

            //print("vor i = " + i);
            yield return new WaitForSeconds(1);
            //print("nach i = " + i);
        }
        introTMPText.SetText("");
        waitTMPText.SetText("");
    }

}
