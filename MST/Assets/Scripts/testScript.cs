using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class testScript : MonoBehaviour
{
    public GameSession gameSession;
    // Start is called before the first frame update
    void Start()
    {
         gameSession = FindObjectOfType<GameSession>();
         //gameSession.playerData.PrintPlayerData();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
