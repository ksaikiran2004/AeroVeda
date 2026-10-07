using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.UI;

public class WindUIController : MonoBehaviour
{

    public WindZone windZone;

    public Slider strengthSlider;
    public Slider speedSlider;
    public Slider turbulenceSlider;
    public Slider valueSlider;
    public Slider directionSlider;

    public Volume globalVolume;
    public Slider fogSlider;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

        //RenderSettings.fog = true;

        fogSlider.onValueChanged.AddListener(UpdateFog);
        //UpdateFog(fogSlider.value);

        windZone.windMain = strengthSlider.value; // changing wind strength by slider value

        strengthSlider.onValueChanged.AddListener(UpdateWindStrength);

        windZone.windPulseFrequency = speedSlider.value;

        speedSlider.onValueChanged.AddListener(UpdateWindSpeed);// speed

        windZone.windTurbulence = turbulenceSlider.value;// turbulance

        turbulenceSlider.onValueChanged.AddListener(UpdateWindTurbulence);

        windZone.windPulseMagnitude = valueSlider.value;// turbulance

        valueSlider.onValueChanged.AddListener(UpdateWindvalue);

        windZone.transform.rotation = Quaternion.Euler(windZone.transform.rotation.eulerAngles.x, directionSlider.value, windZone.transform.rotation.eulerAngles.z);

        directionSlider.onValueChanged.AddListener(UpdateWindDirection);


    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void UpdateWindStrength(float value) // function to change value strength
    {
        windZone.windMain = value;
    }
    void UpdateWindSpeed(float value) // function to change value speed 
    {
        windZone.windPulseFrequency = value;
    }
    void UpdateWindTurbulence(float value) // function to change value turb
    {
        windZone.windTurbulence = value;
    }
    void UpdateWindvalue(float value) // function to change value magnitude
    {
        windZone.windPulseMagnitude = value;
    }
    void UpdateWindDirection(float value) // function to change value magnitude
    {
        windZone.transform.rotation = Quaternion.Euler(windZone.transform.rotation.eulerAngles.x, value, windZone.transform.rotation.eulerAngles.z); ;
    }
    void UpdateFog(float value)
    {
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.ExponentialSquared;

        RenderSettings.fogDensity = Mathf.Lerp(0.005f, 0.04f, value);
    }



}
