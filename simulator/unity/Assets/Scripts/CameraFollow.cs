using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Vector3 offset = new Vector3(0f, 3f, -6f);
    public Transform Drone;

    public float smoothing = 4f;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void LateUpdate()
    {
        if (Drone != null )
        {
            Vector3 cameraPosition  = Drone.position + Drone.TransformDirection(offset);//follow

            transform.position = Vector3.Lerp(transform.position, cameraPosition, smoothing * Time.deltaTime);

            Vector3 direcxtion = Drone.position - transform.position;

            if (direcxtion.sqrMagnitude >0.01f)
            {
                Quaternion targetRotation = Quaternion.LookRotation(direcxtion);

                transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, smoothing * Time.deltaTime);
            }
        }




    }
}
