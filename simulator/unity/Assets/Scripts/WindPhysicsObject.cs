using UnityEngine;

public class WindSystemScript : MonoBehaviour
{

    public WindZone windZone;
    public float windMultiplier = 3f;

    public Rigidbody rb;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        rb = GetComponent<Rigidbody>();
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

        Vector3 windDirection = windZone.transform.forward;

        float windStrength = windZone.windMain;

        Vector3 force = windDirection * windStrength * windMultiplier;
        rb.AddForce(force, ForceMode.Force);

    }
}
