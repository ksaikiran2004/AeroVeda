using UnityEngine;
using UnityEngine.XR;

public class NewMonoBehaviourScript : MonoBehaviour
{

    public WindZone windZone;
    public float windmultiplier = 2f;

    public float maxTilt = 12f;

    public float tiltSmoothness = 4f;

    public Rigidbody rb;
    // Start is called once before the first execution of Update after the MonoBehaviour is created

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void FixedUpdate()
    {
        if (windZone == null)
        {
            return;
        }

        Vector3 windDirection = windZone.transform.forward; // direction

        float windStrength = windZone.windMain; // magnitude

        Vector3 windForce = windDirection * windStrength * windmultiplier; // calculated force

        rb.AddForce(windForce, ForceMode.Force); // adding force of wind on drone

        Vector3 localWind = transform.InverseTransformDirection(windDirection); // direction of tilt

        float pitch = Mathf.Clamp(-localWind.z * windStrength * maxTilt, -maxTilt, maxTilt); // for pitch tilt by wind
        float roll = Mathf.Clamp(localWind.x * windStrength * maxTilt, -maxTilt, maxTilt); // same for roll

        Quaternion tragetRotation = Quaternion.Euler(pitch, transform.eulerAngles.y, roll);

        rb.MoveRotation(Quaternion.Slerp(rb.rotation, tragetRotation, tiltSmoothness * Time.fixedDeltaTime));



    }
}
