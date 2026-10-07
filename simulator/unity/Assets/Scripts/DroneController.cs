using UnityEngine;

public class DroneController : MonoBehaviour
{

    public float hoverForce = 19.62f; // it us same force ans 2 mass and gravity;

    public Transform[] propellers; // cuz there are 4;
    public float propellerSpeed = 2500f;
    public float moveForce = 4f;
    public float verticalForce = 3f;
    public float maxSpeed = 6f;


    public float mouseSensitivity = 3f;
    public float maxPitch = 30f;

    public Rigidbody rb;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        rb = rb.GetComponent<Rigidbody>();
    }

    // Update is called once per frame
    void Update()
    {
        // plane
        float forward = Input.GetAxis("Vertical");
        float sideways = Input.GetAxis("Horizontal");

        Vector3 movement = transform.forward * forward + transform.right * sideways; // geting vector to move

        rb.AddForce(movement * moveForce, ForceMode.Force);// multiplying by magnitude

        //depth

        if (Input.GetKey(KeyCode.Space))
        {
            rb.AddForce(Vector3.up * verticalForce, ForceMode.Force);
        }
        if (Input.GetKey(KeyCode.LeftControl))
        {
            rb.AddForce(Vector3.down * verticalForce, ForceMode.Force);
        }

        if (rb.linearVelocity.magnitude > maxSpeed)
        {
            rb.linearVelocity = rb.linearVelocity.normalized * maxSpeed;
        }

        // mouse look
        if (GameUi.instace.state == GameUi.GameState.GamePlay)
        {
            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            transform.Rotate(Vector3.up * mouseX, Space.World);

            float pitch = -mouseY;
            transform.Rotate(Vector3.right * pitch, Space.Self);
        }

        //foreach (Transform rotator in propellers) // ,anipulating each propeller
        //{
        //    if (rotator != null)
        //    {
        //        rotator.Rotate(Vector3.up, propellerSpeed * Time.deltaTime);
        //    }
        //}
        //for individual control

        if (propellers.Length >= 4)
        {
            propellers[0].Rotate(Vector3.up, propellerSpeed * Time.deltaTime);
            propellers[1].Rotate(Vector3.up, -propellerSpeed * Time.deltaTime);
            propellers[2].Rotate(Vector3.up, -propellerSpeed * Time.deltaTime);
            propellers[3].Rotate(Vector3.up, propellerSpeed * Time.deltaTime);
        }

    }
    private void FixedUpdate()
    {
        rb.AddForce(Vector3.up * hoverForce, ForceMode.Force);// adding upward force to cancel gravity
    }
}
