using Unity.VisualScripting;
using UnityEngine;

public class GameUi : MonoBehaviour
{

    public GameObject GameUI;
    public GameObject WeatherUI;

    public enum GameState
    {
        GamePlay,
        Weather
    }

    public GameState state;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        state = GameState.GamePlay;
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.P) && GameUI != null && WeatherUI != null)
        {
            if (state == GameState.GamePlay)
            {
                GameUI.SetActive(false);
                WeatherUI.SetActive(true);
                state = GameState.Weather;
            }

            else if (state == GameState.Weather)
            {
                GameUI.SetActive(true);
                WeatherUI.SetActive(false);

                state = GameState.GamePlay;
            }
        }
    }

    public static GameUi instace;

    private void Awake()
    {
        instace = this;
    }
}
