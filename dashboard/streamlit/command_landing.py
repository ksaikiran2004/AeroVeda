from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from dashboard.streamlit import command_center as ui
from dashboard.streamlit import mission_control as mc


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
THREAT_LIBRARY = REPOSITORY_ROOT / "shared" / "threat_library"
PAGE_MAP: dict[str, Any] = {}


def bind_pages(pages: dict[str, Any]) -> None:
	global PAGE_MAP
	PAGE_MAP = pages


def load_threat_library() -> list[dict[str, Any]]:
	entries = []
	for path in sorted(THREAT_LIBRARY.glob("*.json")):
		with path.open("r", encoding="utf-8") as handle:
			entries.append(json.load(handle))
	return entries


def _switch_page(label: str) -> None:
	page = PAGE_MAP.get(label)
	if page is not None:
		st.switch_page(page)


def _jump_to_event(event_index: int) -> None:
	st.session_state[mc.REPLAY_INDEX] = event_index
	st.session_state[mc.REPLAY_SCRUBBER] = event_index
	st.session_state[mc.REPLAY_PLAYING] = False
	st.session_state[mc.REPLAY_INITIAL_FRAME] = False
	_switch_page("Mission Control")


def _launch_mission(sector_label: str) -> None:
	st.session_state[mc.SECTOR_KEY] = sector_label
	st.session_state[mc.REPLAY_INDEX] = 0
	st.session_state[mc.REPLAY_SCRUBBER] = 0
	st.session_state[mc.REPLAY_PLAYING] = False
	st.session_state[mc.REPLAY_INITIAL_FRAME] = False
	_switch_page("Mission Control")


@st.dialog("AeroVeda Threat Library", width="large")
def show_threat_library() -> None:
	entries = load_threat_library()
	st.caption("Shared training definitions / read only")
	for threat in entries:
		with ui.tactical_panel(
			threat.get("name", "Unknown Threat"),
			f"{threat.get('category', 'UNKNOWN')} / {threat.get('threatLevel', 'UNRATED')} THREAT LEVEL",
		):
			st.markdown(
				f"**Behavior:** {threat.get('behavior', 'Not recorded')}  "
				f"**Flight profile:** {threat.get('flightProfile', 'Not recorded')}"
			)
			hints = threat.get("detectionHints", [])
			st.markdown("Detection cues: " + ", ".join(hints) if hints else "No detection cues recorded.")


def inject_landing_styles() -> None:
	st.markdown(
		"""
		<style>
		.home-hero { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.85rem 1rem; margin:.05rem 0 1rem; border:1px solid rgba(114,255,145,.38); border-left:3px solid #72ff91; background:linear-gradient(105deg,rgba(13,34,20,.98),rgba(7,16,10,.96)); }
		.home-identity { display:flex; align-items:center; gap:.9rem; min-width:0; }
		.home-logo { width:4.5rem; height:4.5rem; object-fit:contain; filter:drop-shadow(0 0 12px rgba(114,255,145,.2)); }
		.home-brand { color:#72ff91; font:700 clamp(1.35rem,2.2vw,2rem) 'Chakra Petch',sans-serif; letter-spacing:.11em; }
		.home-brand-letter { display:inline-block; color:#ffc45c; font-size:1.38em; line-height:.8; vertical-align:-.06em; text-shadow:0 0 12px rgba(255,196,92,.45); }
		.home-sub { color:#8da695; font:500 .61rem 'IBM Plex Mono',monospace; letter-spacing:.13em; margin-top:.22rem; }
		.home-status { display:flex; align-items:center; gap:.55rem; padding:.5rem .65rem; border:1px solid rgba(114,255,145,.28); color:#72ff91; font:600 .63rem 'IBM Plex Mono',monospace; letter-spacing:.11em; white-space:nowrap; }
		.home-kpi { min-height:4.7rem; padding:.7rem .82rem; border-left:2px solid #1c9b50; border-top:1px solid rgba(105,181,125,.18); border-bottom:1px solid rgba(105,181,125,.18); background:linear-gradient(110deg,rgba(12,29,18,.88),rgba(7,15,10,.62)); }
		.home-kpi-label { color:#77917c; font:500 .55rem 'IBM Plex Mono',monospace; letter-spacing:.1em; }
		.home-kpi-value { color:#d8e7d9; font:700 1.12rem 'Chakra Petch',sans-serif; margin-top:.28rem; }
		.home-kpi-value.green { color:#72ff91; }.home-kpi-value.amber { color:#ffc45c; }.home-kpi-value.red { color:#ff5269; }
		.home-sector { padding:.62rem .68rem; border-left:2px solid #1c9b50; border-bottom:1px solid rgba(105,181,125,.18); background:rgba(7,17,11,.65); min-height:4.05rem; }
		.home-sector-name { color:#d8e7d9; font:600 .75rem 'Chakra Petch',sans-serif; letter-spacing:.04em; }
		.home-sector-terrain { color:#77917c; font:500 .54rem 'IBM Plex Mono',monospace; margin-top:.25rem; }
		.home-activity { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.4rem; }
		.home-activity-item { padding:.52rem .55rem; border:1px solid rgba(105,181,125,.16); background:rgba(5,13,8,.6); }
		.home-activity-label { color:#77917c; font:500 .5rem 'IBM Plex Mono',monospace; letter-spacing:.08em; }
		.home-activity-count { color:#72ff91; font:700 .96rem 'IBM Plex Mono',monospace; margin-top:.18rem; }
		.home-quick-links [data-testid="stPageLink"] { border:1px solid rgba(105,181,125,.22); background:rgba(8,19,12,.82); padding:.5rem .6rem; min-height:2.8rem; }
		.home-quick-links [data-testid="stPageLink"]:hover { border-color:#72ff91; background:rgba(32,104,48,.16); }
		.home-map-note { color:#77917c; font:500 .54rem 'IBM Plex Mono',monospace; letter-spacing:.07em; padding-top:.25rem; }
		@media(max-width:620px) { .home-hero { align-items:flex-start; flex-direction:column; } .home-logo { width:3.7rem; height:3.7rem; } .home-activity { grid-template-columns:repeat(2,minmax(0,1fr)); } }
		</style>
		""",
		unsafe_allow_html=True,
	)


def _kpi(label: str, value: str, tone: str = "") -> str:
	return (
		f'<div class="home-kpi"><div class="home-kpi-label">{ui.escape(label)}</div>'
		f'<div class="home-kpi-value {tone}">{ui.escape(value)}</div></div>'
	)


def _recent_events(record: dict[str, Any]) -> None:
	events = record.get("events", [])
	if not events:
		st.markdown('<div class="missing-note">NO SESSION EVENTS AVAILABLE</div>', unsafe_allow_html=True)
		return

	columns = st.columns(min(5, len(events)), gap="small")
	for event_index, event in enumerate(events):
		with columns[event_index % len(columns)]:
			event_name = mc._event_label(event.get("eventType", "EVENT"))
			st.caption(event.get("timestampUtc", "TIME NOT RECORDED").split("T")[-1].replace("Z", " Z"))
			st.button(
				event_name,
				key=f"home_event_jump_{event_index}",
				help=event.get("details", "Jump to this recorded event in mission replay."),
				use_container_width=True,
				on_click=_jump_to_event,
				args=(event_index,),
			)


def render_command_center() -> None:
	if not PAGE_MAP:
		st.error("Command Center navigation is not initialized.")
		return

	inject_landing_styles()
	record = ui.load_session_record()
	events = record.get("events", [])
	if mc.SECTOR_KEY not in st.session_state:
		st.session_state[mc.SECTOR_KEY] = "Sector ATLAS-5 | Urban Infrastructure"

	logo = mc.LOGO_DATA_URI
	brand_image = f'<img class="home-logo" src="{logo}" alt="AeroVeda crest">' if logo else ""
	st.markdown(
		f'<div class="home-hero"><div class="home-identity">{brand_image}<div>'
		f'<div class="home-brand"><span class="home-brand-letter">A</span>ERO<span class="home-brand-letter">V</span>EDA COMMAND CENTER</div>'
		f'<div class="home-sub">AI-ENABLED COUNTER-UAS TRAINING PLATFORM / TEAM TRINETRA</div></div></div>'
		'<div class="home-status"><i class="mc-live-dot"></i>TRAINING SYSTEM / READY</div></div>',
		unsafe_allow_html=True,
	)

	detection_count = sum(event.get("eventType") == "ThreatDetected" for event in events)
	classification_count = sum(event.get("eventType") == "ThreatClassified" for event in events)
	response_count = sum(event.get("eventType") == "ResponseSelected" for event in events)
	mission_state = "COMPLETE" if record.get("status") == "Completed" else str(record.get("status", "READY")).upper()
	summary_columns = st.columns(5, gap="small")
	for column, markup in zip(summary_columns, [
		_kpi("MISSION STATE", mission_state, "green"),
		_kpi("SECTOR", "ATLAS-5 / URBAN", "amber"),
		_kpi("THREATS DETECTED", f"{detection_count:02d}", "red"),
		_kpi("DECISION EVENTS", f"{classification_count + response_count:02d}"),
		_kpi("LAST MISSION SCORE", ui.display_score(record.get("finalScore")), "green"),
	]):
		with column:
			st.markdown(markup, unsafe_allow_html=True)

	main_map, activity_column = st.columns([1.85, 1], gap="medium")
	sector_label = st.session_state[mc.SECTOR_KEY]
	sector = mc.SECTORS[sector_label]
	with main_map:
		with ui.tactical_panel("Active Training Area", f"{sector['code']} / FICTIONAL SIM GRID"):
			preview_index = min(max(1, len(events) - 1), 1) if events else 0
			figure = mc.build_operations_map(sector, set(mc.MAP_LAYERS), events, preview_index)
			st.plotly_chart(
				figure,
				width="stretch",
				config={"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
				key="command_center_preview_map",
			)
			st.markdown(
				f'<div class="home-map-note">{ui.escape(sector["profile"])} / '
				'FICTIONAL LOCAL GRID / NOT GEOREFERENCED</div>',
				unsafe_allow_html=True,
			)
	with activity_column:
		with ui.tactical_panel("Threat Activity", "SESSION RECORD / EVENT COUNTS"):
			completed = any(event.get("eventType") == "MissionCompleted" for event in events)
			latest = "MISSION COMPLETE" if completed else "TRACK REVIEW"
			st.markdown(
				f'<div class="threat-card"><div class="threat-type">{ui.escape(record.get("actualThreatType", "NO TRACK"))}</div>'
				f'<div class="threat-status">{latest} / {ui.escape(record.get("scenarioEnvironment", "SIMULATION"))}</div></div>',
				unsafe_allow_html=True,
			)
			activity = [
				("DETECTED", detection_count),
				("CLASSIFIED", classification_count),
				("RESPONSES", response_count),
				("EVENTS", len(events)),
			]
			items = "".join(
				f'<div class="home-activity-item"><div class="home-activity-label">{label}</div>'
				f'<div class="home-activity-count">{count:02d}</div></div>'
				for label, count in activity
			)
			st.markdown(f'<div class="home-activity">{items}</div>', unsafe_allow_html=True)
			st.markdown(
				f'<div class="data-grid"><div class="data-pair"><span class="data-key">CLASSIFICATION</span>'
				f'<span class="data-value">{"CORRECT" if record.get("classificationCorrect") else "NOT SCORED"}</span></div>'
				f'<div class="data-pair"><span class="data-key">RESPONSE</span>'
				f'<span class="data-value">{"CORRECT" if record.get("responseCorrect") else "NOT SCORED"}</span></div></div>',
				unsafe_allow_html=True,
			)

	sectors_column, recent_column = st.columns([1.25, 1], gap="medium")
	with sectors_column:
		with ui.tactical_panel("Active Training Sectors", "SYNTHETIC SECTOR BANK / 4 READY"):
			sector_columns = st.columns(2, gap="small")
			for sector_index, (label, details) in enumerate(mc.SECTORS.items()):
				with sector_columns[sector_index % 2]:
					st.markdown(
						f'<div class="home-sector"><div class="home-sector-name">{details["code"]} / {details["terrain"].upper()}</div>'
						f'<div class="home-sector-terrain">{details["profile"]}</div></div>',
						unsafe_allow_html=True,
					)
					st.button(
						"OPEN SECTOR",
						key=f"home_sector_{details['code']}",
						use_container_width=True,
						on_click=_launch_mission,
						args=(label,),
					)
	with recent_column:
		with ui.tactical_panel("Recent Mission", "LATEST SESSION EXPORT"):
			st.markdown(
				f'<div class="data-grid"><div class="data-pair"><span class="data-key">SESSION</span>'
				f'<span class="data-value">{ui.escape(record.get("sessionId", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">SCENARIO</span>'
				f'<span class="data-value">{ui.escape(record.get("scenarioId", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">THREAT</span>'
				f'<span class="data-value">{ui.escape(record.get("actualThreatType", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">FINAL SCORE</span>'
				f'<span class="data-value">{ui.display_score(record.get("finalScore"))}</span></div></div>',
				unsafe_allow_html=True,
			)
			st.markdown(f'<div class="action-line"><span class="action-mark">AAR</span>{ui.escape(record.get("trainingRecommendation", "No recommendation recorded."))}</div>', unsafe_allow_html=True)

	with ui.tactical_panel("Mission Event Replay", "SELECT AN EVENT TO OPEN IT IN REPLAY"):
		_recent_events(record)

	with ui.tactical_panel("Scenario Launcher", "START A FICTIONAL TRAINING MISSION"):
		launcher_column, launch_column = st.columns([2, 1], gap="small")
		with launcher_column:
			st.selectbox("SELECT TRAINING SECTOR", list(mc.SECTORS), key=mc.SECTOR_KEY)
		with launch_column:
			st.markdown('<div style="height:1.85rem"></div>', unsafe_allow_html=True)
			st.button(
				"LAUNCH MISSION",
				key="home_launch_mission",
				icon=":material/rocket_launch:",
				use_container_width=True,
				on_click=_launch_mission,
				args=(st.session_state[mc.SECTOR_KEY],),
			)

	with ui.tactical_panel("Quick Access Modules", "OPERATIONAL WORKSPACES"):
		link_columns = st.columns(4, gap="small")
		quick_links = [
			("Mission Control", "radar"),
			("Threat Detection", "sensors"),
			("Threat Classification", "target"),
			("Tactical Response", "bolt"),
			("Mission Timeline", "timeline"),
			("After Action Review", "fact_check"),
			("Competency Assessment", "monitoring"),
			("Instructor Console", "school"),
		]
		for link_index, (label, icon) in enumerate(quick_links):
			with link_columns[link_index % len(link_columns)]:
				st.page_link(PAGE_MAP[label], label=label, icon=f":material/{icon}:")
		library_col, analytics_col = st.columns([1, 2], gap="small")
		with library_col:
			st.button("THREAT LIBRARY / 5 DEFINITIONS", key="home_threat_library", icon=":material/menu_book:", use_container_width=True, on_click=show_threat_library)
		with analytics_col:
			st.page_link(PAGE_MAP["Competency Assessment"], label="OPEN PERFORMANCE ANALYTICS", icon=":material/monitoring:")