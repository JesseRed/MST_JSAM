using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using TMPro;

public class GameSession : MonoBehaviour
{
    public PlayerData playerData;
    public bool isTutorial = false;
    public bool isInitialized = false;
    


    private void Awake()
    {
        SetUpSingleton();
    }

    private void SetUpSingleton()
    {
        int numberOfGameSessions = FindObjectsOfType<GameSession>().Length;
        if (numberOfGameSessions > 1)
        {
            print("already initialized");
            //GameObject MM = FindObject


            Destroy(gameObject);

        }
        else
        {
            DontDestroyOnLoad(gameObject);
        }

    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void InitializePlayerDataStructure()
    {
        // hole mir die Daten und initialisiere die Classe mit den PlayerData
        //GameObject tmp = FindObjectOfType<VornameText>;
        //GameObject tmp = GameObject.Find("VornameText");
        //TextMeshProUGUI tmp2 = tmp.GetComponent<TextMeshProUGUI>();
        string vorname = GameObject.Find("VornameText").GetComponent<TextMeshProUGUI>().text;
        string nachname = GameObject.Find("NachnameText").GetComponent<TextMeshProUGUI>().text;
        string gebDat = GameObject.Find("GebDatText").GetComponent<TextMeshProUGUI>().text;
        string trainingsDaystring = GameObject.Find("TrainingsDayText").GetComponent<TextMeshProUGUI>().text;
        trainingsDaystring = trainingsDaystring.Substring(0,trainingsDaystring.Length-1);
        int trainingsDay = int.Parse(trainingsDaystring);
        
        string vpNummerstring = GameObject.Find("VPNummerText").GetComponent<TextMeshProUGUI>().text;
        vpNummerstring = vpNummerstring.Substring(0,vpNummerstring.Length-1);
        int vpNummer = int.Parse(vpNummerstring);

        


        playerData = new PlayerData(vorname, nachname, gebDat, trainingsDay, vpNummer);
        isInitialized = true;
    }



    public class PlayerData
    {
        public string vorname;
        public string nachname;
        public string gebDatum;
        public int trainingsDay;
        public int vpNummer;
        
        private List<PlayerTrackEntry> playerTrackEntries ;
        public char lineSeperater = '\n'; // It defines line seperate character
        public char fieldSeperator = '\t'; // It defines field seperate chracter
        public string relativeFilePath = "Assets/Data/";


        // construktor .... ohne die persoenlichen Infos geht nix
        public PlayerData(string vn, string nn, string gd, int td, int vpnum)
        {
            vorname = vn;
            nachname = nn;
            gebDatum = gd;
            trainingsDay = td;
            vpNummer = vpnum;
            playerTrackEntries = new List<PlayerTrackEntry>();
        }

        public void AddData(string blockType, int blockIdx, int seqNum, int itemNum, int timeSinceExpStart, int bp, int bt, int tc, int ta, int timex, int numHit, int numRsp, int RT_2, int Resp_2)
        {
            playerTrackEntries.Add(new PlayerTrackEntry(blockType, blockIdx, seqNum,  itemNum, timeSinceExpStart, bp, bt, tc, ta, timex, numHit, numRsp, RT_2, Resp_2));
        }

        public void SaveDataAsCSV()
        {
            string path = relativeFilePath; // Application.persistentDataPath;
            string filename = path + '/' + vpNummer + vorname + nachname + gebDatum + trainingsDay.ToString() + ".csv";
            print("filename = " + filename);
            using (StreamWriter sw = new StreamWriter(filename))
            {

                // heading line for csv File 
                //string line = "BlockNumber" + fieldSeperator + "SeqNumber" + fieldSeperator + "ItemNumber" + fieldSeperator + "buttonPressed" + fieldSeperator + "buttonTarget" + fieldSeperator + "CircleTarget" + fieldSeperator + "timeAvailable" + fieldSeperator + "timeToButtonPressed";
                string line = "type" + fieldSeperator + "block" + fieldSeperator +
                	"sequ." + fieldSeperator +	"trial" + fieldSeperator +
                    "time" + fieldSeperator + "Pos." + fieldSeperator +	
                    "Color" + fieldSeperator + "Button" + fieldSeperator + 
                    "NumRsp" + fieldSeperator +	"Resp_1" + fieldSeperator + 
                    "RT_1" + fieldSeperator + "R_Code" + fieldSeperator + 
                    "Resp_2" + fieldSeperator +	"RT_2" + fieldSeperator +
                    "Trigg." + fieldSeperator +	"n_hit" + fieldSeperator +
                    "n_inc" + fieldSeperator + "n_miss" + fieldSeperator +
                    "score_%";

                sw.WriteLine(line);
                for (int i=0; i<playerTrackEntries.Count; i++)
                {
                    //line = playerTrackEntries[i].getEntryString();
                    line = playerTrackEntries[i].getEntryStringRalph();
                    sw.WriteLine(line);
                }

            }
        }

    }

    public class PlayerTrackEntry
    {
        private string blockType;
        private int blockIdx;
        private int itemNumber;
        private int sequenceNumber;
        private int timeSinceExpStart;
        private int buttonPressed;
        private int buttonTarget;
        private int targetCircle;
        private int timeAvailable;
        private int timeToButtonPress;
        private int numHit;
        private int RT_1;
        private int RT_2;
        private int Resp_1;
        private int Resp_2;
        private int numRsp;
        public char fieldSeperator = '\t'; // It defines field seperate chracter

        public PlayerTrackEntry(string iblockType, int bidx, int seqNum, int itemNum, int itimeSinceExpStart, int iResp_1, int bt, int tc, int ta, int iRT_1, int inumHit, int inumRsp, int iRT_2, int iResp_2)
        {
            blockType = iblockType;
            blockIdx = bidx;
            itemNumber = itemNum;
            sequenceNumber=seqNum;
            timeSinceExpStart = itimeSinceExpStart;
            buttonTarget=bt;
            targetCircle = tc;
            timeAvailable=ta;
            numHit = inumHit;
            numRsp = inumRsp;
            RT_2 = iRT_2;
            Resp_2 = iResp_2;
            RT_1 = iRT_1;
            Resp_1 = iResp_1;
        }

        public string getEntryString()
        {
            string line = blockIdx.ToString() + fieldSeperator + sequenceNumber.ToString() + fieldSeperator + itemNumber.ToString() + fieldSeperator +  buttonPressed.ToString() + fieldSeperator + buttonTarget.ToString() +fieldSeperator + targetCircle.ToString() + fieldSeperator + timeAvailable.ToString() + fieldSeperator + timeToButtonPress.ToString();
            return line;
        }

        public string getEntryStringRalph()
        {
            targetCircle += 1; // Ralph faengt bei 1 an
            int R_Code = 1;

            string line = blockType + fieldSeperator + blockIdx.ToString() + fieldSeperator + 
            sequenceNumber.ToString() + fieldSeperator + itemNumber.ToString() + fieldSeperator + 
            timeSinceExpStart.ToString() + fieldSeperator + targetCircle.ToString() + fieldSeperator +
            buttonTarget.ToString() + fieldSeperator + Resp_1.ToString() + fieldSeperator + 
            numRsp.ToString() + fieldSeperator + Resp_1.ToString() + fieldSeperator +
            RT_1.ToString() + fieldSeperator + R_Code.ToString() + fieldSeperator +
            Resp_2.ToString() + fieldSeperator + RT_2.ToString() + fieldSeperator +
            timeAvailable.ToString() + fieldSeperator + numHit.ToString();
            return line;

// type	block	sequ.	trial	time	Pos.	Color	Button	NumRsp	Resp_1	RT_1	R_Code	Resp_2	RT_2	Trigg.	n_hit	n_inc	n_miss	score_%

// random	1	1	1	3379	6	1	1	1	0	1011	1	4	0	8	1	0	0	100
        }
    }
}
