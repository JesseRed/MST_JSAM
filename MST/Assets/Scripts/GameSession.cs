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
    public string relativeSavePath = "Data";
    public string relativeReadPath = "ExperimentalDesign";

    private void Awake()
    {
        SetUpSingleton();
        //Debug.Log("Awake");
    }

    private void SetUpSingleton()
    {
        int numberOfGameSessions = FindObjectsOfType<GameSession>().Length;
        if (numberOfGameSessions > 1)
        {
            //print("already initialized");
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
        string vorname = GameObject.Find("VornameText").GetComponent<TextMeshProUGUI>().text;
        string nachname = GameObject.Find("NachnameText").GetComponent<TextMeshProUGUI>().text;
        string gebDat = GameObject.Find("GebDatText").GetComponent<TextMeshProUGUI>().text;
        string trainingsDaystring = GameObject.Find("TrainingsDayText").GetComponent<TextMeshProUGUI>().text;
        trainingsDaystring = trainingsDaystring.Substring(0,trainingsDaystring.Length-1);

        int trainingsDay;
        trainingsDay = int.Parse(trainingsDaystring);

        string vpNummerstring = GameObject.Find("VPNummerText").GetComponent<TextMeshProUGUI>().text;
        vpNummerstring = vpNummerstring.Substring(0,vpNummerstring.Length-1);
        int vpNummer;
        int.TryParse(vpNummerstring, out vpNummer);
        string appdatapath = Application.dataPath;
        string fileDesignName;
        //fileDesignName = "Experiment1_Day1.csv";//"Experiment1_Day" + trainingsDaystring + ".csv";
        fileDesignName = "Experiment1_Day" + trainingsDay.ToString() + ".csv";
//        string relative_path_file = Path.Combine(relativeReadPath, fileDesignName);
        //string jsonString = Path.Combine(appdatapath, relative_path_file);
        char x = Path.DirectorySeparatorChar;
        //char x = '/';
        //string jsonFileName = Application.dataPath + x + relativeReadPath + x + fileDesignName; //Path.DirectorySeparatorChar Combine(appdatapath, relative_path_file);
        string paradigmFileName;
        //paradigmFileName = "G:/Unity/MST_JSAM/MST/Assets/ExperimentalDesign/Experiment1_Day1.csv"; //Application.dataPath + x + relativeReadPath + x + fileDesignName; //Path.DirectorySeparatorChar Combine(appdatapath, relative_path_file);
        paradigmFileName = Application.dataPath + x + relativeReadPath + x + fileDesignName; //Path.DirectorySeparatorChar Combine(appdatapath, relative_path_file);
        
//        print(paradigmFileName);

        playerData = new PlayerData(vorname, nachname, gebDat, trainingsDay, vpNummer, paradigmFileName);
        isInitialized = true;
    }

    [System.Serializable]
    public class PlayerData
    {
        public string vorname;
        public string nachname;
        public string gebDatum;
        public int trainingsDay;
        public int vpNummer;
        // public Paradigma paradigma;
        public List<Block> paradigmaBlocks = new List<Block>();

        private List<PlayerTrackEntry> playerTrackEntries;
        public char lineSeperater = '\n'; // It defines line seperate character
        public char fieldSeperator = ';'; // It defines field seperate chracter
        public string relativeFilePath = "Assets/Data/";


        // construktor .... ohne die persoenlichen Infos geht nix
        public PlayerData(string vn, string nn, string gd, int td, int vpnum, string paradigmaFileName)
        {
            vorname = vn;
            nachname = nn;
            gebDatum = gd;
            trainingsDay = td;
            vpNummer = vpnum;
            //paradigma = Paradigma(jsonString);
            //print(jsonString);
            //paradigma = Paradigma.CreateFromJSON(jsonString);
            //paradigma = JsonUtility.FromJson<Paradigma>(jsonString);
            readingExperimentalDesignFile(paradigmaFileName);
            playerTrackEntries = new List<PlayerTrackEntry>();
        }

        public void AddData(int iblockIdx, int ieventNum, float itimeSinceBlockStart, int iisHit, int itarget, int ipressed)
        {
            playerTrackEntries.Add(new PlayerTrackEntry(iblockIdx, ieventNum, itimeSinceBlockStart, iisHit, itarget, ipressed));
        }

        public void SaveDataAsCSV()
        {
            string path = relativeFilePath; // Application.persistentDataPath;
            string filename = path + '/' + vpNummer + vorname + nachname + gebDatum + trainingsDay.ToString() + ".csv";
            print("filename = " + filename);
            using (StreamWriter sw = new StreamWriter(filename))
            {
                // heading line for csv File 
                string line = "BlockNumber" + fieldSeperator + "EventNumber" +fieldSeperator + "Time Since Block start" + 
                fieldSeperator + "isHit" + fieldSeperator + "target" + fieldSeperator + "pressed";

                sw.WriteLine(line);
                for (int i = 0; i < playerTrackEntries.Count; i++)
                {
                    line = playerTrackEntries[i].getEntryString();
                    sw.WriteLine(line);
                }
            }
        }

        public void PrintPlayerData()
        {
            print("Ausgabe von Playerdata");
            print("Name = " + vorname + ' ' + nachname);
            foreach(Block b in paradigmaBlocks){
                print("BlockNumber = " + b.expBlock);
            } 
        }
        public void readingExperimentalDesignFile(string filename)
        {
            print("Reading experimental Design");
            string line;
            using (StreamReader sr = new StreamReader(filename))
            {
                sr.ReadLine();
                while (true)
                {
                    line = sr.ReadLine();
                    if (line == null)
                    {
                        break;
                    }
                    // print(line);
                    string[] fields = line.Split(';');
                    // print(fields[0]);
                    int expBlock = int.Parse(fields[0]);
                    string expSequence = fields[1];
                    int expTimeOn = int.Parse(fields[2]);
                    int expTimeOff = int.Parse(fields[3]);
                    int expEndBlockPause = int.Parse(fields[4]);
                    string expEndBlockMessage = fields[5];
                    int expEndBlockManualContinuation = int.Parse(fields[6]);
                    Block singleBlock = new Block(expBlock, expSequence, expTimeOn, expTimeOff, expEndBlockPause, expEndBlockMessage, expEndBlockManualContinuation);
                    paradigmaBlocks.Add(singleBlock);
                }
            }

        }
    }



    public class PlayerTrackEntry
    {

        // blockIdx  |   Time since Block start  |   Type           |  Hit          |   ScheibenNr (in Sequence)  |    position x  |  pos y     |    velocity   |       Radius   | existence time | max_existence time |  num scheiben present
        //    1                 1234 (ms)            mouseButton       1/0         |       1 bei miss naechste scheibe
        //    1                 3323                instantiate        0           |       2
        //    1                 3233 (ms)            destroy            0           |       3    
        private int blockIdx;
        private int eventNum;
        private float timeSinceBlockStart;
        private int isHit;
        private int target;
        private int pressed;
        public char fieldSeperator = ';'; // It defines field seperate chracter

        public PlayerTrackEntry(int iblockIdx, int ieventNum,float itimeSinceBlockStart, int iisHit, int iTarget, int ipressed)
        {
            blockIdx = iblockIdx;
            timeSinceBlockStart = itimeSinceBlockStart;
            eventNum = ieventNum;
            isHit = iisHit;
            target = iTarget;
            pressed = ipressed;
        }

        public string getEntryString()
        {
            string line = blockIdx.ToString() + fieldSeperator + eventNum.ToString() + 
            fieldSeperator + timeSinceBlockStart.ToString() + fieldSeperator + isHit.ToString() + 
            fieldSeperator + target.ToString() + fieldSeperator + pressed.ToString();
            return line;
        }
    }


    [System.Serializable]
    public class Block
    {
        public int expBlock;
        public List<int> expSequence = new List<int>();
        public int expTimeOn;
        public int expTimeOff;
        public int expEndBlockPause;
        public string expEndBlockMessage;
        public bool expEndBlockManualContinuation;

        public Block(int block, string seq, int timeOn, int timeOff, int endBlockPause, string endBlockMessage, int endBlockManualContinuation)
        {
            expBlock = block;
            // Sequence string to int array
            string[] fields = seq.Split('-');
            for (int i = 0; i<fields.Length; i++){
                //print("field = " + fields[i]);
                //print("type = " + fields[i].GetType());
                expSequence.Add(int.Parse(fields[i]));
            }
            expTimeOn = timeOn;
            expTimeOff = timeOff;
            expEndBlockPause = endBlockPause;
            expEndBlockMessage = endBlockMessage;
            if (endBlockManualContinuation == 1)
            {
                expEndBlockManualContinuation = true;
            }
            else
            {
                expEndBlockManualContinuation = false;
            }
        }
    }
    //      return JsonUtility.FromJson<Paradigma>(jsonString);
    // }





    // }
}
