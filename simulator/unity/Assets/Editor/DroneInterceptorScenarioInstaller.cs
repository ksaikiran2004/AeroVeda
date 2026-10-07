using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class DroneInterceptorScenarioInstaller
{
    [MenuItem("AeroVeda/Install A-to-B Interceptor Scenario")]
    private static void Install()
    {
        DroneController[] drones = Object.FindObjectsByType<DroneController>(FindObjectsSortMode.None);
        if (drones.Length == 0)
        {
            EditorUtility.DisplayDialog("AeroVeda Scenario", "Open SampleScene first; no DroneController was found.", "OK");
            return;
        }

        DroneController player = drones[0];
        DroneInterceptorScenario scenario = player.GetComponent<DroneInterceptorScenario>();
        if (scenario == null)
            scenario = Undo.AddComponent<DroneInterceptorScenario>(player.gameObject);

        SerializedObject serializedScenario = new SerializedObject(scenario);
        serializedScenario.FindProperty("playerDrone").objectReferenceValue = player;
        serializedScenario.ApplyModifiedProperties();
        EditorSceneManager.MarkSceneDirty(player.gameObject.scene);

        EditorUtility.DisplayDialog("AeroVeda Scenario", "Scenario installed on the player drone. Save the scene, then press Play to launch the attacker from A toward B.", "OK");
    }
}
