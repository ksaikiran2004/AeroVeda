# TRIC × AeroVeda

## Military UAV Interception Simulator

**AeroVeda** is a Unity-based military UAV interception simulator developed as part of the **TRIC × AeroVeda** concept.

The simulator focuses on a realistic aerial interception scenario where a player-controlled interceptor UAV must locate, pursue, and intercept an attacking UAV before it reaches its destination.

---

## 🎯 Project Objective

The core objective of AeroVeda is to simulate a **mid-air UAV interception mission**.

The scenario consists of:

- An airborne launch platform **A**
- A slower attacking UAV traveling toward destination **B**
- A faster player-controlled interceptor UAV
- A dynamic environment with wind and weather effects
- A real-time interception detection system
- Mission and attacker status feedback through the HUD

The player must use the interceptor UAV's speed and maneuverability to catch the attacker **before it reaches B**.

### Mission Flow

```text
  AIRBORNE PLATFORM A
            │
            │
    Attacker UAV
            │
            ▼
  ────────────────────►
            B
  DESTINATION PLATFORM


        ▲
        │
  Player Interceptor
        │
        │
        └────────►
        
    MID-AIR
  INTERCEPTION
```

## 🚁 UAV Systems

### Player Interceptor UAV
The player controls a dedicated military interceptor UAV designed for rapid pursuit.
Features include:
- Military-style UAV appearance
- Tactical military skin
- Distinctive interceptor silhouette
- TRIC × AeroVeda physical insignia
- Player-controlled flight
- Higher speed than the attacker UAV
- Mid-air interception capability
The final player drone is designed to visually communicate:
"This is the TRIC × AeroVeda interceptor UAV."

The physical TRIC × AeroVeda insignia is one of its recognizable visual features.
### Attacker UAV
The attacker represents the hostile aircraft that must be intercepted.
Features include:
- Military attack-UAV design
- Clearly visible aircraft silhouette
- Slower flight speed than the interceptor
- Automated A → B flight path
- Real-time attacker status
- Continuous interception detection during flight
## 🛰️ Airborne Mission Platforms
AeroVeda uses elevated airborne launch and destination platforms rather than conventional ground launch points.
### Platform A
The starting/launch platform for the UAV scenario.
### Platform B
The destination/target platform for the attacking UAV.
The attacker travels from A → B, while the player attempts to intercept it somewhere along the route.
Reaching B is not required for a successful interception.
The intended interception takes place in the air before the attacker reaches B.
## 🌦️ Environment & Weather
The simulator includes an outdoor environment designed to provide a natural terrain backdrop for the UAV scenario.
Environmental features include:
- Grass and natural terrain
- Dry earth and rocky terrain surfaces
- Vegetation and trees
- Dynamic wind system
- Weather controls
- Atmospheric lighting
- Sky environment
The environment provides visual context while keeping the UAVs clearly distinguishable during gameplay.
## 🖥️ Mission HUD
The simulator provides real-time mission information through the HUD.
The interface includes:
- TRIC × AeroVeda branding
- Attacker UAV status
- Mission state
- Weather-control information
- Destination/interception information
- AeroVeda logo
The physical TRIC × AeroVeda insignia is also displayed directly on the player UAV.
## 💥 Interception System
Interception is based on the spatial relationship between the player UAV and the attacker UAV.
The player must:
1. Locate the attacker.
2. Pursue the attacker.
3. Close the distance.
4. Enter the required interception range.
5. Trigger the interception condition.
6. Complete the mission.
The system continuously checks for interception while the attacker is traveling toward B.
This allows the interception to occur mid-flight, rather than requiring the attacker to reach its destination first.
## 🎮 Controls

### Weather Controls
Press:
P

to open the weather controls.
The player UAV flight controls are configured within the simulator.
## 🛠️ Technology Stack
- Unity 6.6
- C#
- Unity Physics
- Unity UI / TextMeshPro
- Unity Terrain
- Dynamic wind and weather system
- Environmental systems
- Git
- GitHub
## 📁 Project Structure
```text
AeroVeda/
│
├── Assets/
│   ├── Art/
│   ├── Editor/
│   ├── Forest/
│   ├── Material/
│   ├── Scenes/
│   ├── Scripts/
│   └── ...
│
├── Packages/
├── ProjectSettings/
├── README.md
└── .gitignore
```

## Important gameplay systems

Important gameplay systems include:
- Player/interceptor UAV control
- Attacker UAV AI
- Interception detection
- Wind/weather simulation
- HUD and mission state
- Environment setup

