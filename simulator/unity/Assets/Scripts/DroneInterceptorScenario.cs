using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

/// <summary>Spawns a visual attacker copy and manages the A-to-B interception scenario.</summary>
public sealed class DroneInterceptorScenario : MonoBehaviour
{
    [Header("Scenario")]
    [SerializeField] private DroneController playerDrone;
    [SerializeField] private float missionFlightAltitude = 48f;
    [SerializeField] private float attackerSpawnAhead = 30f;
    [SerializeField] private float destinationDistance = 850f;
    [SerializeField] private float attackerSpeed = 16f;
    [SerializeField] private float interceptRadius = 6f;

    private AttackerDroneAI attacker;
    private GameObject pointA;
    private GameObject pointB;
    private GameObject hudCanvas;
    private GameObject attackerLabel;
    private GameObject pointALabel;
    private GameObject pointBLabel;
    private TextMeshProUGUI missionStatusLabel;
    private readonly List<Material> runtimeMaterials = new List<Material>();
    private readonly List<Mesh> runtimeMeshes = new List<Mesh>();
    private Vector3 destination;
    private bool playerReachedDestination;
    private string lastStatusText;

    private void Start()
    {
        if (playerDrone == null)
            playerDrone = GetComponent<DroneController>();

        if (playerDrone == null)
        {
            Debug.LogError("Interceptor scenario needs a player DroneController.", this);
            enabled = false;
            return;
        }

        Sprite projectLogo = Resources.Load<Sprite>("Branding/AeroVeda_AV_Logo");
        RemoveFallingLeaves();
        ConfigureWeatherHint();
        BuildHud(projectLogo);

        Transform player = playerDrone.transform;
        float flightAltitude = Mathf.Max(player.position.y, missionFlightAltitude);
        Vector3 playerStart = new Vector3(player.position.x, flightAltitude, player.position.z);
        Rigidbody playerBody = playerDrone.rb != null ? playerDrone.rb : player.GetComponent<Rigidbody>();
        player.position = playerStart;
        if (playerBody != null)
        {
            playerBody.position = playerStart;
            playerBody.linearVelocity = Vector3.zero;
            playerBody.angularVelocity = Vector3.zero;
        }
        Physics.SyncTransforms();

        Vector3 heading = player.forward;
        heading.y = 0f;
        heading = heading.sqrMagnitude > 0.001f ? heading.normalized : Vector3.forward;

        Vector3 start = player.position + heading * attackerSpawnAhead;
        destination = start + heading * destinationDistance;

        GameObject attackerObject = Instantiate(playerDrone.gameObject, start, Quaternion.LookRotation(heading));
        attackerObject.name = "Attacker Drone (A → B)";
        attackerObject.transform.localScale *= 2.7f;

        // Prevent the cloned drone from starting another scenario or responding to player input.
        DroneInterceptorScenario copiedScenario = attackerObject.GetComponent<DroneInterceptorScenario>();
        if (copiedScenario != null)
            copiedScenario.enabled = false;

        DroneController copiedController = attackerObject.GetComponent<DroneController>();
        Transform[] rotors = copiedController != null ? copiedController.propellers : null;
        if (copiedController != null)
            copiedController.enabled = false;

        Transform copiedInsignia = attackerObject.transform.Find("AeroVeda UAV Insignia");
        if (copiedInsignia != null)
            Destroy(copiedInsignia.gameObject);

        NewMonoBehaviourScript windController = attackerObject.GetComponent<NewMonoBehaviourScript>();
        if (windController != null)
            windController.enabled = false;

        ApplyAttackerAppearance(attackerObject, rotors);

        attacker = attackerObject.GetComponent<AttackerDroneAI>();
        if (attacker == null)
            attacker = attackerObject.AddComponent<AttackerDroneAI>();

        attacker.Initialize(
            destination,
            player,
            rotors,
            attackerSpeed,
            interceptRadius,
            copiedController != null ? copiedController.propellerSpeed : 2500f
        );

        // Build the interceptor airframe after cloning so the attacker keeps its own visual identity.
        Transform playerVisualRoot = ApplyPlayerMilitaryAppearance(playerDrone.gameObject);
        ApplyPlayerInsignia(playerVisualRoot, projectLogo);

        Vector3 pointAPosition = player.position + heading * (attackerSpawnAhead * 0.5f) - Vector3.up * 0.30f;
        pointA = CreateMarker("A — Airborne UAV Launch Platform", pointAPosition, true);
        pointB = CreateMarker("B — Airborne Destination Platform", destination - Vector3.up * 0.30f, false);
        attackerLabel = CreateBillboardLabel("ATTACKER UAV", attacker.transform, new Vector3(0f, 2.1f, 0f), new Color(1f, 0.82f, 0.34f));
        pointALabel = CreateBillboardLabel("A  •  UAV LAUNCH BASE", pointA.transform, new Vector3(0f, 3.8f, 0f), new Color(1f, 0.83f, 0.45f));
        pointBLabel = CreateBillboardLabel("B  •  TARGET ZONE", pointB.transform, new Vector3(0f, 3.8f, 0f), new Color(1f, 0.83f, 0.45f));
        pointBLabel.GetComponent<ScreenSpaceWorldLabel>().AvoidOverlapWith(pointALabel.GetComponent<RectTransform>());
        pointBLabel.GetComponent<ScreenSpaceWorldLabel>().AvoidOverlapWith(attackerLabel.GetComponent<RectTransform>());
    }

    private static void RemoveFallingLeaves()
    {
        ParticleSystem[] particleSystems = FindObjectsByType<ParticleSystem>(
            FindObjectsInactive.Include, FindObjectsSortMode.None);
        foreach (ParticleSystem particleSystem in particleSystems)
        {
            Transform current = particleSystem.transform;
            while (current != null)
            {
                if (current.name.IndexOf("FallingLeaves", System.StringComparison.OrdinalIgnoreCase) >= 0 ||
                    current.name.IndexOf("LeafParticle", System.StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    current.gameObject.SetActive(false);
                    break;
                }
                current = current.parent;
            }
        }
    }

    private Transform ApplyPlayerMilitaryAppearance(GameObject drone)
    {
        Color oliveDrab = new Color(0.12f, 0.16f, 0.14f);
        Color darkMetal = new Color(0.045f, 0.055f, 0.052f);
        foreach (Renderer renderer in drone.GetComponentsInChildren<Renderer>())
        {
            if (renderer.transform == drone.transform)
            {
                // Keep the original root collider/Rigidbody for gameplay, but replace its cube look.
                renderer.enabled = false;
                continue;
            }

            string partName = renderer.transform.name.ToLowerInvariant();
            renderer.material.color = partName.Contains("propeller") || partName.Contains("rotor")
                ? darkMetal
                : Color.Lerp(oliveDrab, darkMetal, 0.35f);
        }

        Transform airframe = CreateUnscaledVisualRoot(drone.transform, "TRIC AeroVeda Interceptor Airframe");
        Color armor = new Color(0.19f, 0.23f, 0.20f);
        Color edge = new Color(0.37f, 0.39f, 0.33f);
        Color glass = new Color(0.08f, 0.15f, 0.16f);

        AddDroneDetail(airframe, PrimitiveType.Cube, "Interceptor central fuselage",
            new Vector3(0f, 0.15f, 0.02f), new Vector3(0.96f, 0.50f, 3.0f), oliveDrab);
        AddDroneDetail(airframe, PrimitiveType.Sphere, "Armored cockpit canopy",
            new Vector3(0f, 0.38f, 0.53f), new Vector3(0.58f, 0.20f, 0.84f), glass);
        AddDroneDetail(airframe, PrimitiveType.Capsule, "Forward EO sensor turret",
            new Vector3(0f, 0.17f, 1.48f), new Vector3(0.46f, 0.32f, 0.58f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Sphere, "Sensor lens",
            new Vector3(0f, 0.12f, 1.78f), new Vector3(0.20f, 0.18f, 0.16f), edge);
        AddSweptWing(airframe, "Interceptor swept wing", 5.6f, 0.58f, 0.78f, 2.80f, 0.18f, -0.82f,
            -0.82f, -0.12f, 0.11f, armor);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Rear tailplane",
            new Vector3(0f, 0.13f, -1.25f), new Vector3(1.72f, 0.12f, 0.46f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Vertical tail fin",
            new Vector3(0f, 0.43f, -1.28f), new Vector3(0.14f, 0.68f, 0.48f), oliveDrab);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Insignia mounting plate",
            new Vector3(0f, 0.418f, -0.55f), new Vector3(0.90f, 0.028f, 0.90f), darkMetal);

        for (int x = -1; x <= 1; x += 2)
        for (int z = -1; z <= 1; z += 2)
            AddDroneDetail(airframe, PrimitiveType.Cube, "Armored motor nacelle",
                new Vector3(x * 0.82f, 0.08f, z * 0.50f), new Vector3(0.36f, 0.24f, 0.38f), darkMetal);

        AddDroneDetail(airframe, PrimitiveType.Cube, "Left wing subdued ID panel",
            new Vector3(-2.47f, -0.045f, -0.14f), new Vector3(0.38f, 0.025f, 0.34f), edge);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Right wing subdued ID panel",
            new Vector3(2.47f, -0.045f, -0.14f), new Vector3(0.38f, 0.025f, 0.34f), edge);
        return airframe;
    }

    private void ApplyPlayerInsignia(Transform airframe, Sprite logo)
    {
        if (logo == null)
        {
            Debug.LogWarning("AeroVeda logo sprite was not found in Resources/Branding.");
            return;
        }

        // A mesh-only decal has no collider or Rigidbody and remains attached to the player airframe.
        GameObject insignia = new GameObject("AeroVeda UAV Insignia", typeof(MeshFilter), typeof(MeshRenderer));
        insignia.name = "AeroVeda UAV Insignia";
        insignia.transform.SetParent(airframe, false);
        insignia.transform.localPosition = new Vector3(0f, 0.438f, -0.55f);

        Mesh decalMesh = CreateHorizontalQuad("AeroVeda Insignia Mesh", 0.82f, 0.82f);
        runtimeMeshes.Add(decalMesh);
        insignia.GetComponent<MeshFilter>().sharedMesh = decalMesh;

        Renderer renderer = insignia.GetComponent<Renderer>();
        renderer.shadowCastingMode = ShadowCastingMode.Off;
        renderer.receiveShadows = false;

        Material material = CreateRuntimeMaterial(Color.white, "AeroVeda Insignia", true);
        material.mainTexture = logo.texture;
        if (material.HasProperty("_BaseMap"))
            material.SetTexture("_BaseMap", logo.texture);
        renderer.sharedMaterial = material;
    }

    private void ApplyAttackerAppearance(GameObject drone, Transform[] rotors)
    {
        Color camo = new Color(0.51f, 0.49f, 0.37f);
        Color darkMetal = new Color(0.11f, 0.14f, 0.14f);
        foreach (Renderer renderer in drone.GetComponentsInChildren<Renderer>())
        {
            if (renderer.transform == drone.transform)
            {
                renderer.enabled = false;
                continue;
            }

            bool isRotor = false;
            if (rotors != null)
            {
                foreach (Transform rotor in rotors)
                {
                    if (rotor != null && renderer.transform.IsChildOf(rotor))
                    {
                        isRotor = true;
                        break;
                    }
                }
            }
            renderer.material.color = isRotor ? darkMetal : camo;
        }

        Transform airframe = CreateUnscaledVisualRoot(drone.transform, "Distinct Attacker UAV Airframe");
        Color panel = new Color(0.68f, 0.64f, 0.48f);
        Color marking = new Color(0.90f, 0.68f, 0.31f);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker armored fuselage",
            new Vector3(0f, 0.17f, 0.08f), new Vector3(1.65f, 0.62f, 5.8f), camo);
        AddSweptWing(airframe, "Attacker long-span wing", 15.6f, 0.95f, 1.05f, 7.80f, 0.26f, -1.35f,
            -1.35f, -0.13f, 0.17f, panel);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker tailplane",
            new Vector3(0f, 0.18f, -2.28f), new Vector3(2.9f, 0.15f, 0.72f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker dorsal fin left",
            new Vector3(-0.56f, 0.48f, -2.30f), new Vector3(0.14f, 0.72f, 0.70f), camo);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker dorsal fin right",
            new Vector3(0.56f, 0.48f, -2.30f), new Vector3(0.14f, 0.72f, 0.70f), camo);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker left engine pod",
            new Vector3(-3.10f, 0.02f, -0.05f), new Vector3(0.68f, 0.44f, 1.30f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker right engine pod",
            new Vector3(3.10f, 0.02f, -0.05f), new Vector3(0.68f, 0.44f, 1.30f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Sphere, "Attacker forward sensor turret",
            new Vector3(0f, -0.20f, 2.55f), new Vector3(0.68f, 0.48f, 0.70f), darkMetal);
        AddDroneDetail(airframe, PrimitiveType.Sphere, "Attacker sensor lens",
            new Vector3(0f, -0.22f, 2.88f), new Vector3(0.26f, 0.24f, 0.18f), marking);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker wing identification band left",
            new Vector3(-7.10f, 0.0f, -0.28f), new Vector3(0.52f, 0.04f, 0.64f), marking);
        AddDroneDetail(airframe, PrimitiveType.Cube, "Attacker wing identification band right",
            new Vector3(7.10f, 0.0f, -0.28f), new Vector3(0.52f, 0.04f, 0.64f), marking);
    }

    private void AddDroneDetail(Transform parent, PrimitiveType shape, string objectName,
        Vector3 localPosition, Vector3 localScale, Color color)
    {
        GameObject detail = GameObject.CreatePrimitive(shape);
        detail.name = objectName;
        Collider collider = detail.GetComponent<Collider>();
        if (collider != null)
            DestroyImmediate(collider);
        detail.transform.SetParent(parent, false);
        detail.transform.localPosition = localPosition;
        detail.transform.localRotation = Quaternion.identity;
        detail.transform.localScale = localScale;
        Renderer renderer = detail.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = CreateRuntimeMaterial(color, objectName + " Material");
    }

    private Transform CreateUnscaledVisualRoot(Transform parent, string objectName)
    {
        GameObject root = new GameObject(objectName);
        root.transform.SetParent(parent, false);
        Vector3 parentScale = parent.localScale;
        root.transform.localScale = new Vector3(
            Mathf.Abs(parentScale.x) > 0.0001f ? 1f / parentScale.x : 1f,
            Mathf.Abs(parentScale.y) > 0.0001f ? 1f / parentScale.y : 1f,
            Mathf.Abs(parentScale.z) > 0.0001f ? 1f / parentScale.z : 1f
        );
        return root.transform;
    }

    private void AddSweptWing(Transform parent, string objectName, float span, float rootHalfSpan,
        float rootLeadingEdge, float tipHalfSpan, float tipLeadingEdge, float tipTrailingEdge,
        float rootTrailingEdge, float topY, float thickness, Color color)
    {
        Vector3[] outline =
        {
            new Vector3(-rootHalfSpan, topY, rootLeadingEdge),
            new Vector3(rootHalfSpan, topY, rootLeadingEdge),
            new Vector3(tipHalfSpan, topY, tipLeadingEdge),
            new Vector3(tipHalfSpan, topY, tipTrailingEdge),
            new Vector3(rootHalfSpan, topY, rootTrailingEdge),
            new Vector3(-rootHalfSpan, topY, rootTrailingEdge),
            new Vector3(-tipHalfSpan, topY, tipTrailingEdge),
            new Vector3(-tipHalfSpan, topY, tipLeadingEdge)
        };

        int count = outline.Length;
        Vector3[] vertices = new Vector3[count * 2];
        Vector2[] uv = new Vector2[count * 2];
        for (int i = 0; i < count; i++)
        {
            Vector3 top = outline[i];
            top.x = Mathf.Clamp(top.x, -span * 0.5f, span * 0.5f);
            vertices[i] = top;
            vertices[count + i] = new Vector3(top.x, top.y - thickness, top.z);
            uv[i] = new Vector2((top.x / span) + 0.5f, (top.z + 1f) / 2f);
            uv[count + i] = uv[i];
        }

        List<int> triangles = new List<int>(count * 12);
        for (int i = 1; i < count - 1; i++)
        {
            triangles.Add(0);
            triangles.Add(i);
            triangles.Add(i + 1);
            triangles.Add(count);
            triangles.Add(count + i + 1);
            triangles.Add(count + i);
        }
        for (int i = 0; i < count; i++)
        {
            int next = (i + 1) % count;
            triangles.Add(i);
            triangles.Add(count + i);
            triangles.Add(count + next);
            triangles.Add(i);
            triangles.Add(count + next);
            triangles.Add(next);
        }

        Mesh mesh = new Mesh { name = objectName + " Mesh" };
        mesh.vertices = vertices;
        mesh.uv = uv;
        mesh.triangles = triangles.ToArray();
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        runtimeMeshes.Add(mesh);

        GameObject wing = new GameObject(objectName, typeof(MeshFilter), typeof(MeshRenderer));
        wing.transform.SetParent(parent, false);
        wing.GetComponent<MeshFilter>().sharedMesh = mesh;
        wing.GetComponent<MeshRenderer>().sharedMaterial = CreateRuntimeMaterial(color, objectName + " Material");
    }

    private Mesh CreateHorizontalQuad(string meshName, float width, float length)
    {
        float halfWidth = width * 0.5f;
        float halfLength = length * 0.5f;
        Mesh mesh = new Mesh { name = meshName };
        mesh.vertices = new[]
        {
            new Vector3(-halfWidth, 0f, -halfLength),
            new Vector3(-halfWidth, 0f, halfLength),
            new Vector3(halfWidth, 0f, halfLength),
            new Vector3(halfWidth, 0f, -halfLength)
        };
        mesh.uv = new[] { new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(1f, 0f) };
        mesh.triangles = new[] { 0, 1, 2, 0, 2, 3 };
        mesh.normals = new[] { Vector3.up, Vector3.up, Vector3.up, Vector3.up };
        mesh.RecalculateBounds();
        return mesh;
    }

    private Material CreateRuntimeMaterial(Color color, string materialName, bool transparent = false)
    {
        Shader shader = Shader.Find(transparent
            ? "Universal Render Pipeline/Unlit"
            : "Universal Render Pipeline/Lit");
        if (shader == null)
            shader = Shader.Find(transparent ? "Sprites/Default" : "Standard");

        Material material = new Material(shader) { name = materialName };
        material.color = color;
        if (material.HasProperty("_BaseColor"))
            material.SetColor("_BaseColor", color);
        if (transparent)
        {
            if (material.HasProperty("_Surface"))
            {
                material.SetFloat("_Surface", 1f);
                material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                material.SetFloat("_ZWrite", 0f);
                material.SetOverrideTag("RenderType", "Transparent");
                material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            }
            material.SetInt("_Cull", (int)CullMode.Off);
            material.renderQueue = (int)RenderQueue.Transparent;
        }
        runtimeMaterials.Add(material);
        return material;
    }

    private void ConfigureWeatherHint()
    {
        GameObject hintObject = GameObject.Find("PText");
        if (hintObject == null)
            return;

        TextMeshProUGUI hint = hintObject.GetComponent<TextMeshProUGUI>();
        if (hint == null)
            return;

        RectTransform rect = hint.rectTransform;
        rect.anchorMin = rect.anchorMax = new Vector2(1f, 1f);
        rect.pivot = new Vector2(1f, 1f);
        rect.anchoredPosition = new Vector2(-24f, -24f);
        rect.sizeDelta = new Vector2(320f, 28f);
        hint.fontSize = 11f;
        hint.enableAutoSizing = false;
        hint.textWrappingMode = TextWrappingModes.NoWrap;
        hint.alignment = TextAlignmentOptions.Right;
        hint.fontStyle = FontStyles.Bold;
        hint.raycastTarget = false;

        GameUi gameUi = GameUi.instace;
        if (gameUi == null || gameUi.WeatherUI == null)
            return;

        RectTransform weatherRect = gameUi.WeatherUI.GetComponent<RectTransform>();
        if (weatherRect != null)
            weatherRect.anchoredPosition = new Vector2(-24f, -120f);

        foreach (TextMeshProUGUI weatherText in gameUi.WeatherUI.GetComponentsInChildren<TextMeshProUGUI>(true))
        {
            if (weatherText.gameObject.name != "PText (1)")
                continue;

            weatherText.text = "Press P to close weather controls";
            weatherText.fontSize = 11f;
            weatherText.enableAutoSizing = false;
            weatherText.textWrappingMode = TextWrappingModes.NoWrap;
            weatherText.alignment = TextAlignmentOptions.Right;
            weatherText.raycastTarget = false;
            weatherText.rectTransform.sizeDelta = new Vector2(420f, 36f);
            weatherText.rectTransform.anchoredPosition = new Vector2(-110f, 55f);
            break;
        }
    }

    private void Update()
    {
        if (!playerReachedDestination && playerDrone != null &&
            Vector3.Distance(playerDrone.transform.position, destination) <= interceptRadius)
            playerReachedDestination = true;

        UpdateHudStatus();
    }

    private static Vector3 GetGroundPosition(Vector3 position)
    {
        foreach (Terrain terrain in Terrain.activeTerrains)
        {
            if (terrain == null)
                continue;

            Vector3 local = position - terrain.transform.position;
            Vector3 size = terrain.terrainData.size;
            if (local.x < 0f || local.z < 0f || local.x > size.x || local.z > size.z)
                continue;

            position.y = terrain.SampleHeight(position) + terrain.transform.position.y;
            return position;
        }

        RaycastHit hit;
        if (Physics.Raycast(position + Vector3.up * 1000f, Vector3.down, out hit, 2000f))
            position.y = hit.point.y;
        return position;
    }

    private static GameObject CreateMarker(string markerName, Vector3 position, bool launchBase)
    {
        GameObject marker = new GameObject(markerName);
        marker.transform.position = position;
        Color concrete = new Color(0.105f, 0.135f, 0.13f);
        Color edge = new Color(0.40f, 0.43f, 0.36f);
        Color light = new Color(0.72f, 0.63f, 0.36f);
        if (launchBase)
        {
            // A compact airborne carrier deck, with an open support frame instead of a thick slab.
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Airborne launch landing deck",
                new Vector3(0f, 0.10f, 0f), new Vector3(8f, 0.20f, 42f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch catwalk port",
                new Vector3(-6.1f, 0.10f, 0f), new Vector3(1.25f, 0.20f, 39f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch catwalk starboard",
                new Vector3(6.1f, 0.10f, 0f), new Vector3(1.25f, 0.20f, 39f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch deck forward crossbeam",
                new Vector3(0f, 0.10f, 20.0f), new Vector3(14f, 0.20f, 0.55f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch deck aft crossbeam",
                new Vector3(0f, 0.10f, -20.0f), new Vector3(14f, 0.20f, 0.55f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Deck center runway",
                new Vector3(0f, 0.205f, 0f), new Vector3(3.2f, 0.012f, 39f), new Color(0.18f, 0.22f, 0.21f));
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch marking left",
                new Vector3(-1.20f, 0.215f, 0f), new Vector3(0.08f, 0.012f, 15f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch marking right",
                new Vector3(1.20f, 0.215f, 0f), new Vector3(0.08f, 0.012f, 15f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Launch marking crossbar",
                new Vector3(0f, 0.215f, 0f), new Vector3(3f, 0.012f, 0.08f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Carrier frame fore beam",
                new Vector3(0f, -0.50f, 19.2f), new Vector3(13f, 0.28f, 0.45f), darkFrameColor());
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Carrier frame aft beam",
                new Vector3(0f, -0.50f, -19.2f), new Vector3(13f, 0.28f, 0.45f), darkFrameColor());
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Carrier frame center beam",
                new Vector3(0f, -0.58f, 0f), new Vector3(0.55f, 0.35f, 39f), darkFrameColor());
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Carrier frame port beam",
                new Vector3(-6.1f, -0.50f, 0f), new Vector3(0.35f, 0.28f, 38f), darkFrameColor());
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Carrier frame starboard beam",
                new Vector3(6.1f, -0.50f, 0f), new Vector3(0.35f, 0.28f, 38f), darkFrameColor());
            AddPlatformSupports(marker.transform, 19.2f, 6.1f, light);
        }
        else
        {
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Airborne destination landing deck",
                new Vector3(0f, 0.10f, 0f), new Vector3(10f, 0.20f, 12f), concrete);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Destination perimeter north",
                new Vector3(0f, 0.21f, 8.8f), new Vector3(18.8f, 0.025f, 0.14f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Destination perimeter south",
                new Vector3(0f, 0.21f, -8.8f), new Vector3(18.8f, 0.025f, 0.14f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Destination perimeter east",
                new Vector3(8.8f, 0.21f, 0f), new Vector3(0.14f, 0.025f, 18.8f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Destination perimeter west",
                new Vector3(-8.8f, 0.21f, 0f), new Vector3(0.14f, 0.025f, 18.8f), edge);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cylinder, "Destination landing target",
                new Vector3(0f, 0.215f, 0f), new Vector3(4.8f, 0.018f, 4.8f), new Color(0.28f, 0.32f, 0.29f));
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Target center crossbar",
                new Vector3(0f, 0.23f, 0f), new Vector3(0.16f, 0.012f, 5.8f), light);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Target center crossbar east-west",
                new Vector3(0f, 0.23f, 0f), new Vector3(5.8f, 0.012f, 0.16f), light);
            AddMarkerPrimitive(marker.transform, PrimitiveType.Cube, "Destination support beam",
                new Vector3(0f, -0.50f, 0f), new Vector3(0.55f, 0.32f, 16f), darkFrameColor());
            AddPlatformSupports(marker.transform, 7.2f, 7.2f, light);
        }

        return marker;
    }

    private static Color darkFrameColor()
    {
        return new Color(0.035f, 0.045f, 0.045f);
    }

    private static void AddPlatformSupports(Transform parent, float halfLength, float halfWidth, Color beaconColor)
    {
        float[] xPositions = { -halfWidth, halfWidth };
        float[] zPositions = { -halfLength, halfLength };
        foreach (float x in xPositions)
        foreach (float z in zPositions)
        {
            AddMarkerPrimitive(parent, PrimitiveType.Cube, "Non-colliding platform strut",
                new Vector3(x, -0.38f, z), new Vector3(0.30f, 0.78f, 0.30f), darkFrameColor());
            AddMarkerPrimitive(parent, PrimitiveType.Sphere, "Platform amber beacon",
                new Vector3(x, 0.42f, z), new Vector3(0.20f, 0.12f, 0.20f), beaconColor);
        }
    }

    private static void AddMarkerPrimitive(Transform parent, PrimitiveType primitive, string objectName,
        Vector3 localPosition, Vector3 localScale, Color color)
    {
        GameObject part = GameObject.CreatePrimitive(primitive);
        part.name = objectName;
        part.transform.SetParent(parent, false);
        part.transform.localPosition = localPosition;
        part.transform.localScale = localScale;
        Collider collider = part.GetComponent<Collider>();
        if (collider != null)
            Destroy(collider);
        Renderer renderer = part.GetComponent<Renderer>();
        if (renderer != null)
            renderer.material.color = color;
    }

    private GameObject CreateBillboardLabel(string value, Transform target, Vector3 offset, Color color)
    {
        GameObject labelObject = new GameObject(value + " Label", typeof(RectTransform), typeof(CanvasRenderer), typeof(TextMeshProUGUI));
        labelObject.transform.SetParent(hudCanvas.transform, false);
        TextMeshProUGUI label = labelObject.GetComponent<TextMeshProUGUI>();
        label.font = TMP_Settings.defaultFontAsset;
        label.text = value;
        label.fontSize = value == "ATTACKER UAV" ? 18f : 16f;
        label.textWrappingMode = TextWrappingModes.NoWrap;
        label.alignment = TextAlignmentOptions.Center;
        label.fontStyle = FontStyles.Bold;
        label.color = color;
        label.outlineWidth = 0.2f;
        label.outlineColor = new Color(0.04f, 0.05f, 0.04f);
        label.raycastTarget = false;
        RectTransform rect = label.rectTransform;
        rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.sizeDelta = new Vector2(value == "ATTACKER UAV" ? 210f : 300f, 32f);
        ScreenSpaceWorldLabel follow = labelObject.AddComponent<ScreenSpaceWorldLabel>();
        Vector2 labelOffset = value == "ATTACKER UAV"
            ? new Vector2(0f, 38f)
            : value.StartsWith("A  ") ? new Vector2(-150f, 120f) : new Vector2(150f, 120f);
        follow.Initialize(target, offset, labelOffset, hudCanvas.GetComponent<RectTransform>(), rect, label);
        return labelObject;
    }

    private void BuildHud(Sprite projectLogo)
    {
        hudCanvas = new GameObject("Scenario HUD", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        Canvas canvas = hudCanvas.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 100;
        CanvasScaler scaler = hudCanvas.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);
        scaler.matchWidthOrHeight = 0.5f;

        TMP_FontAsset font = TMP_Settings.defaultFontAsset;
        TextMeshProUGUI brand = CreateHudText("Branding", hudCanvas.transform, font,
            "TRIC  ×  AeroVeda", 30f, FontStyles.Bold, TextAlignmentOptions.Left);
        SetHudRect(brand.rectTransform, new Vector2(0f, 1f), new Vector2(0f, 1f),
            new Vector2(28f, -24f), new Vector2(460f, 48f), new Vector2(0f, 1f));

        GameObject panel = new GameObject("Mission Status Panel", typeof(RectTransform), typeof(Image));
        panel.transform.SetParent(hudCanvas.transform, false);
        RectTransform panelRect = panel.GetComponent<RectTransform>();
        SetHudRect(panelRect, new Vector2(1f, 1f), new Vector2(1f, 1f),
            new Vector2(-24f, -112f), new Vector2(430f, 78f), new Vector2(1f, 1f));
        panel.GetComponent<Image>().color = new Color(0.035f, 0.05f, 0.04f, 0.82f);

        if (projectLogo != null)
        {
            GameObject logoFrame = new GameObject("AeroVeda Logo Frame", typeof(RectTransform), typeof(Image));
            logoFrame.transform.SetParent(hudCanvas.transform, false);
            RectTransform frameRect = logoFrame.GetComponent<RectTransform>();
            SetHudRect(frameRect, new Vector2(1f, 0f), new Vector2(1f, 0f),
                new Vector2(-24f, 24f), new Vector2(104f, 104f), new Vector2(1f, 0f));
            Image frameImage = logoFrame.GetComponent<Image>();
            frameImage.color = new Color(0.025f, 0.04f, 0.03f, 0.72f);
            frameImage.raycastTarget = false;

            GameObject logoObject = new GameObject("AeroVeda Project Logo", typeof(RectTransform), typeof(Image));
            logoObject.transform.SetParent(logoFrame.transform, false);
            RectTransform logoRect = logoObject.GetComponent<RectTransform>();
            SetHudRect(logoRect, Vector2.zero, Vector2.one, Vector2.zero,
                new Vector2(-12f, -12f), new Vector2(0.5f, 0.5f));
            Image logoImage = logoObject.GetComponent<Image>();
            logoImage.sprite = projectLogo;
            logoImage.preserveAspect = true;
            logoImage.raycastTarget = false;
        }

        missionStatusLabel = CreateHudText("Mission Status", panel.transform, font,
            "MISSION 01  •  INTERCEPT\nATTACKER UAV  •  EN ROUTE A → B", 18f,
            FontStyles.Bold, TextAlignmentOptions.Left);
        missionStatusLabel.textWrappingMode = TextWrappingModes.Normal;
        SetHudRect(missionStatusLabel.rectTransform, Vector2.zero, Vector2.one,
            new Vector2(14f, -8f), new Vector2(-28f, -16f), new Vector2(0f, 1f));
    }

    private static TextMeshProUGUI CreateHudText(string name, Transform parent, TMP_FontAsset font,
        string value, float size, FontStyles style, TextAlignmentOptions alignment)
    {
        GameObject textObject = new GameObject(name, typeof(RectTransform), typeof(CanvasRenderer), typeof(TextMeshProUGUI));
        textObject.transform.SetParent(parent, false);
        TextMeshProUGUI text = textObject.GetComponent<TextMeshProUGUI>();
        text.font = font;
        text.text = value;
        text.fontSize = size;
        text.fontStyle = style;
        text.alignment = alignment;
        text.color = new Color(0.94f, 0.94f, 0.86f);
        text.raycastTarget = false;
        return text;
    }

    private static void SetHudRect(RectTransform rect, Vector2 anchorMin, Vector2 anchorMax,
        Vector2 position, Vector2 size, Vector2 pivot)
    {
        rect.anchorMin = anchorMin;
        rect.anchorMax = anchorMax;
        rect.pivot = pivot;
        rect.anchoredPosition = position;
        rect.sizeDelta = size;
    }

    private void UpdateHudStatus()
    {
        if (missionStatusLabel == null || attacker == null)
            return;

        string state = attacker.State == AttackerDroneAI.FlightState.Intercepted
            ? "INTERCEPTED"
            : playerReachedDestination
                ? "DESTINATION REACHED"
                : attacker.State == AttackerDroneAI.FlightState.EnRoute
                ? "EN ROUTE  A → B"
                : "REACHED DESTINATION";
        string value = "MISSION 01  •  INTERCEPT\nATTACKER UAV  •  " + state;
        if (value != lastStatusText)
        {
            missionStatusLabel.text = value;
            lastStatusText = value;
        }
    }

    private void OnDestroy()
    {
        if (attacker != null)
            Destroy(attacker.gameObject);
        if (pointA != null)
            Destroy(pointA);
        if (pointB != null)
            Destroy(pointB);
        if (hudCanvas != null)
            Destroy(hudCanvas);
        if (attackerLabel != null)
            Destroy(attackerLabel);
        if (pointALabel != null)
            Destroy(pointALabel);
        if (pointBLabel != null)
            Destroy(pointBLabel);
        foreach (Material material in runtimeMaterials)
            if (material != null)
                Destroy(material);
        foreach (Mesh mesh in runtimeMeshes)
            if (mesh != null)
                Destroy(mesh);
        runtimeMaterials.Clear();
        runtimeMeshes.Clear();
    }
}

/// <summary>Keeps a readable screen-space label aligned with a world position.</summary>
public sealed class ScreenSpaceWorldLabel : MonoBehaviour
{
    private Transform target;
    private Vector3 offset;
    private Vector2 screenOffset;
    private RectTransform canvasRect;
    private RectTransform labelRect;
    private readonly List<RectTransform> avoidRects = new List<RectTransform>();
    private TextMeshProUGUI label;
    private const float LabelAvoidanceGap = 12f;

    public void Initialize(Transform followTarget, Vector3 worldOffset, Vector2 uiOffset, RectTransform parentRect,
        RectTransform textRect, TextMeshProUGUI text)
    {
        target = followTarget;
        offset = worldOffset;
        screenOffset = uiOffset;
        canvasRect = parentRect;
        labelRect = textRect;
        label = text;
    }

    public void AvoidOverlapWith(RectTransform other)
    {
        if (other != null && !avoidRects.Contains(other))
            avoidRects.Add(other);
    }

    private void LateUpdate()
    {
        if (target == null || canvasRect == null || labelRect == null || label == null)
            return;

        Camera cameraToFace = Camera.main;
        if (cameraToFace == null)
            return;

        Vector3 screen = cameraToFace.WorldToScreenPoint(target.position + offset);
        if (label.text == "ATTACKER UAV" && screen.z > 0f)
        {
            if (screen.y > Screen.height - 190f && screen.x > Screen.width - 470f)
            {
                screen.x = Screen.width - 250f;
                screen.y = Screen.height - 238f;
            }
            else
            {
                screen.x = Mathf.Clamp(screen.x, labelRect.rect.width * 0.5f + 24f, Screen.width - labelRect.rect.width * 0.5f - 24f);
                screen.y = Mathf.Clamp(screen.y, labelRect.rect.height * 0.5f + 24f, Screen.height - 210f);
            }
            labelRect.anchoredPosition = ScreenPointToLocal(screen) + screenOffset;
            label.enabled = true;
            return;
        }

        bool visible = screen.z > 0f && screen.x >= 24f && screen.x <= Screen.width - 24f &&
            screen.y >= 24f && screen.y <= Screen.height - 24f;
        // Keep the dedicated top-right weather and mission HUD region clear while retaining the label.
        if (screen.y > Screen.height - 190f && screen.x > Screen.width - 470f)
        {
            screen.x = Screen.width - 250f;
            screen.y = Screen.height - 260f;
        }
        label.enabled = visible;
        if (visible)
        {
            Vector2 desiredPosition = ScreenPointToLocal(screen) + screenOffset;
            foreach (RectTransform other in avoidRects)
                if (other != null)
                    desiredPosition = ResolveOverlap(desiredPosition, other);
            labelRect.anchoredPosition = desiredPosition;
        }
    }

    private Vector2 ResolveOverlap(Vector2 desiredPosition, RectTransform otherRect)
    {
        TextMeshProUGUI otherLabel = otherRect.GetComponent<TextMeshProUGUI>();
        if (otherLabel != null && !otherLabel.enabled)
            return desiredPosition;

        Rect other = CanvasRectAt(otherRect, otherRect.anchoredPosition);
        Rect own = CanvasRectAt(labelRect, desiredPosition);
        if (!own.Overlaps(other))
            return desiredPosition;

        float canvasTop = canvasRect.rect.height * 0.5f;
        float canvasBottom = -canvasTop;
        float topLimit = canvasTop - 190f;
        float bottomLimit = canvasBottom + 32f;
        float height = labelRect.rect.height;

        Vector2 above = desiredPosition;
        above.y = other.yMax + LabelAvoidanceGap + height * labelRect.pivot.y;
        if (CanvasRectAt(labelRect, above).yMax <= topLimit)
            return above;

        Vector2 below = desiredPosition;
        below.y = other.yMin - LabelAvoidanceGap - height * (1f - labelRect.pivot.y);
        below.y = Mathf.Max(below.y, bottomLimit + height * labelRect.pivot.y);
        return below;
    }

    private static Rect CanvasRectAt(RectTransform rectTransform, Vector2 anchoredPosition)
    {
        Vector2 size = rectTransform.rect.size;
        Vector2 bottomLeft = anchoredPosition - Vector2.Scale(size, rectTransform.pivot);
        return new Rect(bottomLeft, size);
    }

    private Vector2 ScreenPointToLocal(Vector3 screen)
    {
        RectTransformUtility.ScreenPointToLocalPointInRectangle(canvasRect, screen, null, out Vector2 localPoint);
        return localPoint;
    }
}
