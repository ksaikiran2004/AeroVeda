from __future__ import annotations

import base64
import math
import re
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from dashboard.streamlit import command_center as ui


LOGO_FILE = Path(__file__).resolve().parents[1] / "AV_Logo.png"
LOGO_DATA_URI = (
	"data:image/png;base64," + base64.b64encode(LOGO_FILE.read_bytes()).decode("ascii")
	if LOGO_FILE.exists()
	else ""
)

SECTORS: dict[str, dict[str, Any]] = {
	"Sector KILO-7 | Mountain Valley": {
		"code": "KILO-7", "terrain": "Mountain Valley", "relief": "Synthetic relief bands: 22-64 sim units",
		"profile": "RIDGELINE / VALLEY FLOOR / DRAINAGE CUT",
		"assets": [("NORTH DEPOT", 22, 24), ("VALLEY RELAY", 76, 70)],
		"sensors": [("RIDGE-01", 19, 73, 16), ("PASS-02", 58, 51, 13), ("DEPOT-03", 80, 26, 11)],
		"zones": [("WESTERN SCREEN", [5, 5, 43, 43], [39, 84, 84, 39])],
		"waypoints": [("WP-1", 84, 80), ("WP-2", 69, 68), ("WP-3", 51, 58), ("WP-4", 37, 41)],
		"terrain": "mountain",
	},
	"Sector RAVEN-3 | Desert Corridor": {
		"code": "RAVEN-3", "terrain": "Desert Corridor", "relief": "Synthetic relief bands: 08-19 sim units",
		"profile": "DRY WASH / DUNE RIDGE / OPEN CORRIDOR",
		"assets": [("FORWARD POST", 25, 28), ("WATER POINT", 73, 72)],
		"sensors": [("WASH-01", 18, 67, 17), ("RIDGE-02", 55, 48, 15), ("POST-03", 81, 25, 11)],
		"zones": [("EASTERN CORRIDOR", [45, 45, 94, 94], [18, 75, 75, 18])],
		"waypoints": [("WP-1", 89, 78), ("WP-2", 74, 69), ("WP-3", 57, 55), ("WP-4", 35, 34)],
		"terrain": "desert",
	},
	"Sector ATLAS-5 | Urban Infrastructure": {
		"code": "ATLAS-5", "terrain": "Urban Infrastructure", "relief": "Synthetic relief bands: 04-16 sim units",
		"profile": "BUILT-UP GRID / TRANSIT SPINE / OPEN PLAZA",
		"assets": [("OPERATIONS HUB", 25, 26), ("POWER NODE", 76, 73), ("TRANSIT EXCHANGE", 75, 27)],
		"sensors": [("NORTH ARRAY", 18, 74, 15), ("CENTRAL ARRAY", 51, 51, 14), ("EAST ARRAY", 82, 72, 13)],
		"zones": [("TRANSIT PROTECTION ZONE", [32, 32, 68, 68], [30, 69, 69, 30])],
		"waypoints": [("WP-1", 87, 83), ("WP-2", 72, 72), ("WP-3", 60, 56), ("WP-4", 43, 39)],
		"terrain": "urban",
	},
	"Sector TRIDENT-4 | Coastal Defense": {
		"code": "TRIDENT-4", "terrain": "Coastal Defense", "relief": "Synthetic relief bands: 00-28 sim units",
		"profile": "SHORELINE / BLUFF / INLET APPROACH",
		"assets": [("COASTAL STATION", 24, 27), ("HARBOR RELAY", 72, 72)],
		"sensors": [("BLUFF-01", 18, 76, 18), ("HARBOR-02", 58, 48, 14), ("PIER-03", 82, 25, 12)],
		"zones": [("HARBOR APPROACH", [42, 42, 96, 96], [15, 75, 75, 15])],
		"waypoints": [("WP-1", 91, 78), ("WP-2", 76, 68), ("WP-3", 61, 56), ("WP-4", 39, 38)],
		"terrain": "coastal",
	},
}

MAP_LAYERS = [
	"Protected Assets", "Sensor Nodes", "Threat Tracks", "Detection Radius",
	"Patrol Zones", "Threat Waypoints", "Terrain Contours",
]
REPLAY_INDEX = "mc_replay_index"
REPLAY_PLAYING = "mc_replay_playing"
REPLAY_SCRUBBER = "mc_replay_scrubber"
REPLAY_INITIAL_FRAME = "mc_replay_initial_frame"
SECTOR_KEY = "mc_selected_sector"


def inject_mission_styles() -> None:
	st.markdown(
		"""
		<style>
		.mc-command-banner { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.7rem .9rem; margin:.1rem 0 .9rem; border:1px solid rgba(114,255,145,.38); border-left:3px solid #72ff91; background:linear-gradient(100deg,rgba(15,40,23,.96),rgba(7,17,11,.94)); }
		.mc-brand { display:flex; align-items:center; gap:.7rem; min-width:0; }
		.mc-logo { display:grid; place-items:center; width:2.4rem; height:2.4rem; border:1px solid #72ff91; color:#72ff91; font:700 1rem 'IBM Plex Mono',monospace; box-shadow:0 0 16px rgba(114,255,145,.18); }
		.mc-logo-img { display:block; width:4.2rem; height:4.2rem; flex:none; object-fit:contain; filter:drop-shadow(0 0 10px rgba(114,255,145,.22)); }
		.mc-brand-name { color:#72ff91; font:700 1.08rem 'Chakra Petch',sans-serif; letter-spacing:.12em; }
		.mc-brand-letter { display:inline-block; color:#ffc45c; font-size:1.42em; line-height:.82; vertical-align:-.06em; text-shadow:0 0 10px rgba(255,196,92,.48); }
		.mc-brand-sub { color:#77917c; font:500 .53rem 'IBM Plex Mono',monospace; letter-spacing:.08em; margin-top:.12rem; }
		.mc-ops-state { display:flex; align-items:center; gap:.5rem; color:#72ff91; font:600 .61rem 'IBM Plex Mono',monospace; letter-spacing:.1em; text-align:right; }
		.mc-watermark { color:rgba(175,198,178,.58); font:500 .52rem 'IBM Plex Mono',monospace; letter-spacing:.14em; margin-top:.3rem; }
		.mc-live-dot { width:.52rem; height:.52rem; flex:none; border-radius:50%; background:#72ff91; box-shadow:0 0 9px #72ff91; animation:mc-live 1.7s ease-in-out infinite; }
		@keyframes mc-live { 50% { opacity:.35; box-shadow:0 0 2px #72ff91; } }
		@keyframes mc-sweep { to { transform:translate(-50%,-50%) rotate(360deg); } }
		.st-key-mission_control_operations_map [data-testid="stPlotlyChart"] { position:relative; overflow:hidden; }
		.st-key-mission_control_operations_map [data-testid="stPlotlyChart"]:after { content:''; position:absolute; z-index:4; pointer-events:none; width:min(58.2%,26.125rem); aspect-ratio:1; left:var(--mc-sweep-x,50.6%); top:var(--mc-sweep-y,39.3%); transform:translate(-50%,-50%); border-radius:50%; background:conic-gradient(from 0deg, transparent 0deg 315deg, rgba(114,255,145,.015) 330deg, rgba(114,255,145,.2) 358deg, transparent 360deg); animation:mc-sweep 8s linear infinite; }
		.mc-threat-live { animation:mc-threat-pulse 1.5s ease-in-out infinite; }
		@keyframes mc-threat-pulse { 50% { box-shadow:0 0 18px rgba(255,82,105,.24); border-color:rgba(255,82,105,.8); } }
		.mc-sector-line { display:flex; justify-content:space-between; gap:.7rem; flex-wrap:wrap; padding:.52rem .72rem; color:#9bb09e; border:1px solid rgba(105,181,125,.2); border-bottom:0; background:#09150e; font:500 .59rem 'IBM Plex Mono',monospace; letter-spacing:.045em; }
		.mc-sector-line strong { color:#ffc45c; font-weight:600; }
		.mc-map-foot { display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem; padding:.5rem .7rem; border:1px solid rgba(105,181,125,.2); border-top:0; color:#77917c; font:500 .55rem 'IBM Plex Mono',monospace; letter-spacing:.055em; }
		.mc-replay-meta { display:flex; justify-content:space-between; gap:.6rem; flex-wrap:wrap; margin:.15rem 0 .55rem; color:#77917c; font:500 .59rem 'IBM Plex Mono',monospace; }
		[data-testid="stElementContainer"][class*="st-key-mc_event_jump_"] button { width:100%; min-height:3rem; padding:.45rem; white-space:normal; line-height:1.25; border-left:2px solid #1c9b50; }
		[data-testid="stElementContainer"][class*="st-key-mc_event_jump_"] button:hover { border-left-color:#72ff91; }
		.mc-replay-state { color:#72ff91; font:600 .67rem 'IBM Plex Mono',monospace; letter-spacing:.08em; }
		[data-testid="stElementContainer"][class*="st-key-mc_layer_"] label:has(input[role="switch"]) > div:nth-child(2) { background:#101d14 !important; border:1px solid rgba(105,181,125,.38) !important; box-shadow:none !important; }
		[data-testid="stElementContainer"][class*="st-key-mc_layer_"] label:has(input[role="switch"]:checked) > div:nth-child(2) { background:rgba(28,155,80,.75) !important; border-color:#72ff91 !important; box-shadow:0 0 9px rgba(114,255,145,.25) !important; }
		[data-testid="stElementContainer"][class*="st-key-mc_layer_"] label:has(input[role="switch"]:checked) > div:nth-child(2) > div { background:#d8ffe0 !important; }
		[data-testid="stElementContainer"][class*="st-key-mc_layer_"] label:has(input[role="switch"]) [data-testid="stWidgetLabel"] p { color:#c2d3c5; font:500 .64rem 'IBM Plex Mono',monospace; }
		@media(max-width:900px) { .st-key-mission_control_operations_map [data-testid="stPlotlyChart"]:after { width:min(71%,13.25rem); left:var(--mc-sweep-mobile-x,59.6%); top:var(--mc-sweep-mobile-y,33.5%); } }
		@media(max-width:720px) { .mc-command-banner { align-items:flex-start; } .mc-logo-img { width:3.4rem; height:3.4rem; } .mc-brand-name { font-size:.91rem; } .mc-ops-state { max-width:9rem; line-height:1.5; } .mc-sector-line { font-size:.53rem; } }
		header[data-testid="stHeader"] { background:transparent !important; box-shadow:none !important; }
		</style>
		""",
		unsafe_allow_html=True,
	)


def _replay_scrubber_changed() -> None:
	st.session_state[REPLAY_INDEX] = st.session_state[REPLAY_SCRUBBER]
	st.session_state[REPLAY_PLAYING] = False
	st.session_state[REPLAY_INITIAL_FRAME] = False


def _start_replay() -> None:
	st.session_state[REPLAY_PLAYING] = True
	st.session_state[REPLAY_INITIAL_FRAME] = True


def _pause_replay() -> None:
	st.session_state[REPLAY_PLAYING] = False
	st.session_state[REPLAY_INITIAL_FRAME] = False


def _step_replay(delta: int, event_count: int) -> None:
	st.session_state[REPLAY_PLAYING] = False
	st.session_state[REPLAY_INITIAL_FRAME] = False
	index = int(st.session_state.get(REPLAY_INDEX, 0))
	index = max(0, min(event_count - 1, index + delta))
	st.session_state[REPLAY_INDEX] = index
	st.session_state[REPLAY_SCRUBBER] = index


def _jump_replay(event_index: int) -> None:
	st.session_state[REPLAY_PLAYING] = False
	st.session_state[REPLAY_INITIAL_FRAME] = False
	st.session_state[REPLAY_INDEX] = event_index
	st.session_state[REPLAY_SCRUBBER] = event_index


def _event_label(value: Any) -> str:
	return re.sub(r"(?<!^)(?=[A-Z])", " ", str(value)).upper()


def _circle(center_x: float, center_y: float, radius: float) -> tuple[list[float], list[float]]:
	angles = [2 * math.pi * index / 48 for index in range(49)]
	return (
		[center_x + radius * math.cos(angle) for angle in angles],
		[center_y + radius * math.sin(angle) for angle in angles],
	)


def build_operations_map(
	sector: dict[str, Any],
	visible_layers: set[str],
	events: list[dict[str, Any]],
	replay_index: int,
) -> go.Figure:
	figure = go.Figure()
	terrain = sector["terrain"]

	if "Terrain Contours" in visible_layers:
		for contour_index in range(7):
			x_values = list(range(0, 101, 2))
			y_values = []
			for x_value in x_values:
				if terrain == "mountain":
					y_value = 50 + 18 * math.sin(x_value / 10 + contour_index * .5) + 7 * math.sin(x_value / 4.5)
				elif terrain == "desert":
					y_value = 49 + 7 * math.sin(x_value / 9 + contour_index * .36) + 3 * math.sin(x_value / 3.8)
				elif terrain == "urban":
					y_value = 50 + 3 * math.sin(x_value / 7 + contour_index * .7) + 2 * math.sin(x_value / 3)
				else:
					y_value = 44 + 12 * math.sin(x_value / 16 + contour_index * .42) + 4 * math.sin(x_value / 5)
				y_values.append(max(4, min(96, y_value + (contour_index - 3) * 4)))
			figure.add_trace(go.Scatter(
				x=x_values, y=y_values, mode="lines", name="Synthetic Terrain Contours",
				line={"color": f"rgba(103, 179, 116, {0.16 + contour_index * .025})", "width": 1},
				hoverinfo="skip", showlegend=contour_index == 0,
			))

	for zone_name, zone_x, zone_y in sector["zones"]:
		if "Patrol Zones" in visible_layers:
			figure.add_trace(go.Scatter(
				x=zone_x + [zone_x[0]], y=zone_y + [zone_y[0]], mode="lines", fill="toself",
				name=f"Patrol Zone / {zone_name}",
				fillcolor="rgba(89, 227, 215, .07)",
				line={"color": "rgba(89, 227, 215, .55)", "width": 1, "dash": "dash"},
				hovertemplate=f"{zone_name}<extra></extra>",
			))

	if "Detection Radius" in visible_layers:
		for sensor_name, sensor_x, sensor_y, radius in sector["sensors"]:
			circle_x, circle_y = _circle(sensor_x, sensor_y, radius)
			figure.add_trace(go.Scatter(
				x=circle_x, y=circle_y, mode="lines", fill="toself",
				name=f"Detection Radius / {sensor_name}",
				fillcolor="rgba(89, 227, 215, .035)",
				line={"color": "rgba(89, 227, 215, .28)", "width": 1},
				hovertemplate=f"{sensor_name} / SYNTHETIC COVERAGE<extra></extra>",
			))

	if "Protected Assets" in visible_layers:
		assets = sector["assets"]
		figure.add_trace(go.Scatter(
			x=[asset[1] for asset in assets], y=[asset[2] for asset in assets],
			text=[asset[0] for asset in assets], mode="markers+text", textposition="bottom center",
			name="Protected Assets", textfont={"color": "#72ff91", "size": 9},
			marker={"symbol": "square", "size": 12, "color": "#72ff91", "line": {"color": "#d9ffe0", "width": 1}},
			hovertemplate="ASSET / %{text}<extra></extra>",
		))

	if "Sensor Nodes" in visible_layers:
		sensors = sector["sensors"]
		figure.add_trace(go.Scatter(
			x=[sensor[1] for sensor in sensors], y=[sensor[2] for sensor in sensors],
			text=[sensor[0] for sensor in sensors], mode="markers+text", textposition="top center",
			name="Sensor Nodes", textfont={"color": "#59e3d7", "size": 9},
			marker={"symbol": "cross", "size": 14, "color": "#59e3d7", "line": {"width": 2}},
			hovertemplate="SENSOR / %{text}<extra></extra>",
		))

	event_names = [str(event.get("eventType", "")) for event in events]
	stage_index = {
		"ThreatDetected": 0,
		"ThreatClassified": 1,
		"ResponseSelected": 2,
		"MissionCompleted": 3,
	}
	current_stage = -1
	for event_index, event_name in enumerate(event_names[:replay_index + 1]):
		if event_name in stage_index:
			current_stage = stage_index[event_name]

	waypoints = sector["waypoints"]
	if current_stage >= 0 and "Threat Waypoints" in visible_layers:
		figure.add_trace(go.Scatter(
			x=[point[1] for point in waypoints], y=[point[2] for point in waypoints],
			text=[point[0] for point in waypoints], mode="markers+text", textposition="top right",
			name="Threat Waypoints", textfont={"color": "#ff9ba8", "size": 8},
			marker={"symbol": "circle-open", "size": 9, "color": "#ff5269", "line": {"width": 1.5}},
			hovertemplate="THREAT WAYPOINT / %{text}<extra></extra>",
		))

	if current_stage >= 0 and "Threat Tracks" in visible_layers:
		track_points = waypoints[:current_stage + 1]
		figure.add_trace(go.Scatter(
			x=[point[1] for point in track_points], y=[point[2] for point in track_points],
			mode="lines", name="Recorded Threat Track",
			line={"color": "rgba(255,82,105,.9)", "width": 2.5, "dash": "dot"},
			hoverinfo="skip",
		))
		active_point = waypoints[current_stage]
		figure.add_trace(go.Scatter(
			x=[active_point[1]], y=[active_point[2]], mode="markers+text",
			text=["HOSTILE / " + ("TRACK" if current_stage == 0 else "CLASSIFIED" if current_stage == 1 else "RESPONSE" if current_stage == 2 else "COMPLETE")],
			textposition="top center", name="Active Threat Track",
			textfont={"color": "#ff8494", "size": 10},
			marker={"symbol": "diamond", "size": 21, "color": "#ff5269", "line": {"color": "#ffe0e4", "width": 1.4}},
			hovertemplate="SIM TRACK / %{text}<extra></extra>",
		))

	if current_stage >= 2:
		response_sensor = sector["sensors"][1]
		active_point = waypoints[current_stage]
		figure.add_trace(go.Scatter(
			x=[response_sensor[1], active_point[1]], y=[response_sensor[2], active_point[2]],
			mode="lines", name="Response Telemetry", line={"color": "#ffc45c", "width": 2},
			hovertemplate="SIMULATED RESPONSE VECTOR<extra></extra>",
		))

	figure.update_layout(
		height=560,
		margin={"l": 18, "r": 12, "t": 10, "b": 12},
		paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#07130c",
		font={"family": "IBM Plex Mono, monospace", "color": "#a9c2ae", "size": 9},
		legend={"orientation": "h", "y": -0.12, "x": 0, "font": {"size": 8}, "bgcolor": "rgba(5,11,8,.7)"},
		showlegend=True,
		dragmode="pan",
		uirevision=sector["code"],
		meta={"sector": sector["code"], "grid": "fictional local simulation grid"},
	)
	figure.update_xaxes(
		range=[0, 100], dtick=10, title={"text": "LOCAL GRID / EASTING", "font": {"color": "#77917c", "size": 8}}, zeroline=False,
		gridcolor="rgba(94,153,105,.13)", linecolor="rgba(114,255,145,.24)",
		tickfont={"color": "#77917c", "size": 8},
		showline=True, ticks="outside", constrain="domain",
	)
	figure.update_yaxes(
		range=[0, 100], dtick=10, title={"text": "LOCAL GRID / NORTHING", "font": {"color": "#77917c", "size": 8}}, zeroline=False,
		gridcolor="rgba(94,153,105,.13)", linecolor="rgba(114,255,145,.24)",
		tickfont={"color": "#77917c", "size": 8},
		showline=True, ticks="outside", scaleanchor="x", scaleratio=1, constrain="domain",
	)
	return figure


def _render_replay_timeline(events: list[dict[str, Any]], index: int, playing: bool) -> None:
	active_event = events[index]
	st.markdown(
		f'<div class="mc-replay-meta"><span class="mc-replay-state">{"PLAYING" if playing else "PAUSED"} / {index + 1:02d} OF {len(events):02d}</span>'
		f'<span>{ui.escape(active_event.get("timestampUtc", "TIME NOT RECORDED"))}</span>'
		f'<span>{ui.escape(_event_label(active_event.get("eventType", "EVENT")))}</span></div>',
		unsafe_allow_html=True,
	)
	st.session_state[REPLAY_SCRUBBER] = index
	st.slider(
		"MISSION REPLAY / EVENT SCRUBBER",
		min_value=0,
		max_value=max(0, len(events) - 1),
		step=1,
		key=REPLAY_SCRUBBER,
		on_change=_replay_scrubber_changed,
		disabled=playing,
		label_visibility="visible",
	)
	event_columns = st.columns(min(5, len(events)), gap="small")
	for event_index, event in enumerate(events):
		with event_columns[event_index % len(event_columns)]:
			st.caption(event.get("timestampUtc", "TIME NOT RECORDED").split("T")[-1].replace("Z", " Z"))
			st.button(
				_event_label(event.get("eventType", "EVENT")),
				key=f"mc_event_jump_{event_index}",
				help=event.get("details", "Jump to this event in the recorded mission."),
				use_container_width=True,
				on_click=_jump_replay,
				args=(event_index,),
			)
	st.markdown(
		f'<div class="action-line"><span class="action-mark">NOW</span>'
		f'{ui.escape(active_event.get("details", "No event details recorded."))}</div>',
		unsafe_allow_html=True,
	)


def _render_replay_controls(events: list[dict[str, Any]]) -> None:
	if not events:
		st.markdown('<div class="missing-note">NO REPLAYABLE EVENTS IN SESSION RECORD</div>', unsafe_allow_html=True)
		return

	controls = st.columns(4)
	controls[0].button("PLAY", key="mc_play", icon=":material/play_arrow:", use_container_width=True, on_click=_start_replay)
	controls[1].button("PAUSE", key="mc_pause", icon=":material/pause:", use_container_width=True, on_click=_pause_replay)
	controls[2].button("STEP BACK", key="mc_step_back", icon=":material/skip_previous:", use_container_width=True, on_click=_step_replay, args=(-1, len(events)))
	controls[3].button("STEP FORWARD", key="mc_step_forward", icon=":material/skip_next:", use_container_width=True, on_click=_step_replay, args=(1, len(events)))


def render_mission_workspace(record: dict[str, Any]) -> None:
	if SECTOR_KEY not in st.session_state:
		st.session_state[SECTOR_KEY] = "Sector ATLAS-5 | Urban Infrastructure"
	if REPLAY_INDEX not in st.session_state:
		st.session_state[REPLAY_INDEX] = 0
	if REPLAY_PLAYING not in st.session_state:
		st.session_state[REPLAY_PLAYING] = False
	if REPLAY_INITIAL_FRAME not in st.session_state:
		st.session_state[REPLAY_INITIAL_FRAME] = False
	if REPLAY_SCRUBBER not in st.session_state:
		st.session_state[REPLAY_SCRUBBER] = st.session_state[REPLAY_INDEX]

	logo_markup = (
		f'<img class="mc-logo-img" src="{LOGO_DATA_URI}" alt="AeroVeda crest">'
		if LOGO_DATA_URI
		else '<div class="mc-logo">AV</div>'
	)
	st.markdown(
		f'<div class="mc-command-banner"><div class="mc-brand">{logo_markup}'
		f'<div><div class="mc-brand-name"><span class="mc-brand-letter">A</span>ERO'
		f'<span class="mc-brand-letter">V</span>EDA / MISSION CONTROL</div>'
		f'<div class="mc-brand-sub">AI-ENABLED COUNTER-UAS TRAINING PLATFORM</div>'
		f'<div class="mc-watermark">TEAM TRINETRA / TRAINING SYSTEMS</div></div></div>'
		f'<div class="mc-ops-state"><i class="mc-live-dot"></i>SIMULATION FEED / NO LIVE SENSOR LINK</div></div>',
		unsafe_allow_html=True,
	)
	sector_col, layers_col = st.columns([1, 2.2], gap="small")
	with sector_col:
		st.selectbox("FICTIONAL TRAINING SECTOR", list(SECTORS), key=SECTOR_KEY)
	with layers_col:
		with ui.tactical_panel("Map Layers", "TOGGLE VISIBILITY"):
			layer_columns = st.columns(4)
			visible_layers: set[str] = set()
			for layer_index, layer_name in enumerate(MAP_LAYERS):
				layer_key = f"mc_layer_{layer_index}"
				if layer_key not in st.session_state:
					st.session_state[layer_key] = True
				with layer_columns[layer_index % len(layer_columns)]:
					if st.toggle(layer_name, key=layer_key):
						visible_layers.add(layer_name)
	sector = SECTORS[st.session_state[SECTOR_KEY]]
	events = record.get("events", [])
	if not events:
		st.warning("No mission events are available for replay.")
	st.markdown(
		f'<div class="mc-sector-line"><span><strong>{sector["code"]}</strong> / {sector["terrain"].upper()}</span>'
		f'<span>TOPO PROFILE / {sector["profile"]}</span><span>{sector["relief"]}</span></div>',
		unsafe_allow_html=True,
	)

	run_every = 0.85 if st.session_state[REPLAY_PLAYING] else None

	@st.fragment(run_every=run_every)
	def render_map_and_timeline() -> None:
		replay_index = max(0, min(int(st.session_state[REPLAY_INDEX]), len(events) - 1)) if events else 0
		if st.session_state[REPLAY_PLAYING] and events:
			if st.session_state[REPLAY_INITIAL_FRAME]:
				st.session_state[REPLAY_INITIAL_FRAME] = False
			elif replay_index < len(events) - 1:
				replay_index += 1
				st.session_state[REPLAY_INDEX] = replay_index
				st.session_state[REPLAY_SCRUBBER] = replay_index
			else:
				st.session_state[REPLAY_PLAYING] = False
				st.rerun(scope="app")
				return

		phase_event_names = [event.get("eventType") for event in events[:replay_index + 1]]
		detected = "ThreatDetected" in phase_event_names
		classified = "ThreatClassified" in phase_event_names
		response_sent = "ResponseSelected" in phase_event_names
		completed = "MissionCompleted" in phase_event_names

		map_col, feed_col = st.columns([2.45, 1], gap="medium")
		with map_col:
			with ui.tactical_panel("Tactical Operations Map", f"{sector['code']} / SYNTHETIC SIM GRID"):
				sweep_sensor = sector["sensors"][1]
				sensor_x, sensor_y = sweep_sensor[1], sweep_sensor[2]
				desktop_sweep_x = 50.6 + (sensor_x - 51) * .582
				desktop_sweep_y = 39.3 - (sensor_y - 51) * .746
				mobile_sweep_x = 59.6 + (sensor_x - 51) * .709
				mobile_sweep_y = 33.5 - (sensor_y - 51) * .379
				st.markdown(
					f'<style>.st-key-mission_control_operations_map {{'
					f'--mc-sweep-x:{desktop_sweep_x:.2f}%;--mc-sweep-y:{desktop_sweep_y:.2f}%;'
					f'--mc-sweep-mobile-x:{mobile_sweep_x:.2f}%;--mc-sweep-mobile-y:{mobile_sweep_y:.2f}%;'
					'</style>',
					unsafe_allow_html=True,
				)
				figure = build_operations_map(sector, visible_layers, events, replay_index)
				st.plotly_chart(
					figure,
					width="stretch",
					config={
						"scrollZoom": True,
						"displaylogo": False,
						"modeBarButtonsToRemove": ["select2d", "lasso2d"],
						"toImageButtonOptions": {"format": "png", "filename": f"{sector['code']}-sim-map"},
					},
					key="mission_control_operations_map",
				)
				st.markdown(
					'<div class="mc-map-foot"><span>SIM LOCAL GRID / NOT GEOREFERENCED</span>'
					'<span>SCROLL TO ZOOM / DRAG TO PAN / DOUBLE-CLICK TO RESET</span>'
					'<span>SYNTHETIC TERRAIN MODEL</span></div>',
					unsafe_allow_html=True,
				)
		with feed_col:
			with ui.tactical_panel("Live Threat Feed", f"{sector['code']} / SESSION REPLAY"):
				if completed:
					threat_state, state_class = "MISSION COMPLETE / TRACK RESOLVED", "neutralized"
				elif response_sent:
					threat_state, state_class = f"RESPONSE / {record.get('selectedResponse', 'ACTION')}", "response"
				elif classified:
					threat_state, state_class = "CLASSIFIED / HOSTILE", "hostile"
				elif detected:
					threat_state, state_class = "DETECTED / TRACK ACQUIRED", "hostile"
				else:
					threat_state, state_class = "SEARCH / NO TRACK", "search"
				pulse_class = " mc-threat-live" if detected and not completed else ""
				st.markdown(
					f'<div class="threat-card{pulse_class}"><div class="threat-type">{ui.escape(record.get("actualThreatType", "UNKNOWN"))}</div>'
					f'<div class="threat-status">{threat_state}</div></div>',
					unsafe_allow_html=True,
				)
				st.markdown(
					f'<div class="data-grid"><div class="data-pair"><span class="data-key">OPERATOR CLASS</span>'
					f'<span class="data-value">{ui.escape(record.get("classifiedThreatType", "NOT RECORDED") if classified else "PENDING")}</span></div>'
					f'<div class="data-pair"><span class="data-key">CONFIDENCE</span><span class="data-value">NOT RECORDED</span></div>'
					f'<div class="data-pair"><span class="data-key">RANGE</span><span class="data-value">NOT RECORDED</span></div>'
					f'<div class="data-pair"><span class="data-key">SPEED</span><span class="data-value">NOT RECORDED</span></div>'
					f'<div class="data-pair"><span class="data-key">WAYPOINT</span><span class="data-value">{"WP-" + str(min(4, max(1, replay_index))) if detected else "--"}</span></div>'
					f'<div class="data-pair"><span class="data-key">TRACK STATE</span><span class="data-value">{state_class.upper()}</span></div></div>',
					unsafe_allow_html=True,
				)
				if response_sent:
					st.markdown(
						f'<div class="data-key" style="margin-bottom:.35rem">RECORDED ACTION</div>'
						f'<div class="action-readout">{ui.escape(record.get("selectedResponse", "NOT RECORDED")).upper()}</div>',
						unsafe_allow_html=True,
					)
				st.markdown(
					f'<div class="missing-note">DISPLAY DATA: {sector["code"]} FICTIONAL TRAINING GRID. '
					'NO GPS, LIVE SENSOR, RANGE, OR SPEED TELEMETRY IN SOURCE RECORD.</div>',
					unsafe_allow_html=True,
				)

		if events:
			with ui.tactical_panel("Mission Replay Timeline", "SESSION EVENTS / RECORDED UTC"):
				_render_replay_timeline(events, replay_index, st.session_state[REPLAY_PLAYING])

	render_map_and_timeline()
	with ui.tactical_panel("Replay Controls", "PLAYBACK / STEP"):
		_render_replay_controls(events)


def render_mission_control() -> None:
	record = ui.load_session_record()
	ui.page_heading("Mission Control", "Interactive Operations Picture", f"SESSION // {record.get('sessionId', 'N/A')}")
	inject_mission_styles()
	render_mission_workspace(record)