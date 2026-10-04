from __future__ import annotations

import base64
import html
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATA_FILE = Path(__file__).resolve().parent / "data" / "exports" / "session_record_demo.json"
LOGO_FILE = Path(__file__).resolve().parents[1] / "AV_Logo.png"
LOGO_DATA_URI = (
	"data:image/png;base64," + base64.b64encode(LOGO_FILE.read_bytes()).decode("ascii")
	if LOGO_FILE.exists()
	else ""
)


def load_session_record() -> dict[str, Any]:
	if not DATA_FILE.exists():
		raise FileNotFoundError(f"Session record not found at {DATA_FILE}")

	with DATA_FILE.open("r", encoding="utf-8") as handle:
		return json.load(handle)


def escape(value: Any) -> str:
	return html.escape(str(value))


def get_event(record: dict[str, Any], event_type: str) -> dict[str, Any] | None:
	return next(
		(event for event in record.get("events", []) if event.get("eventType") == event_type),
		None,
	)


def display_score(value: Any) -> str:
	if value is None:
		return "NOT RECORDED"
	try:
		score = float(value)
	except (TypeError, ValueError):
		return "NOT RECORDED"
	return f"{score * 100:.1f}%" if 0 <= score <= 1 else f"{score:.1f}%"


def inject_theme() -> None:
	st.markdown(
		"""
		<style>
		@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
		:root {
			--bg: #050b08;
			--panel: #0a1510;
			--panel-raised: #0d1b14;
			--line: rgba(105, 181, 125, .22);
			--line-strong: rgba(117, 255, 148, .55);
			--text: #d8e7d9;
			--muted: #77917c;
			--green: #72ff91;
			--green-dim: #1c9b50;
			--amber: #ffc45c;
			--red: #ff5269;
			--cyan: #59e3d7;
			--mono: 'IBM Plex Mono', 'Courier New', monospace;
			--display: 'Chakra Petch', 'Arial Narrow', sans-serif;
		}
		html, body, [class*="css"] { font-family: var(--display); color: var(--text); }
		.stApp {
			background-color: var(--bg);
			background-image:
				linear-gradient(rgba(61, 112, 75, .045) 1px, transparent 1px),
				linear-gradient(90deg, rgba(61, 112, 75, .045) 1px, transparent 1px),
				linear-gradient(180deg, rgba(16, 37, 24, .24), transparent 40%);
			background-size: 32px 32px, 32px 32px, 100% 100%;
		}
		[data-testid="stAppViewContainer"] { background: transparent; }
		header[data-testid="stHeader"] { background: rgba(4, 11, 7, .92); }
		#MainMenu, footer { visibility: hidden; }
		[data-testid="stToolbar"] { visibility: hidden; height: 0; }
		.block-container { max-width: 1800px; padding: 1rem 1.6rem 2.25rem; }
		[data-testid="stSidebar"] {
			background: linear-gradient(180deg, #08130d 0%, #060d09 100%);
			border-right: 1px solid var(--line-strong);
		}
		[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
		[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { margin-bottom: .35rem; }
		.sidebar-brand {
			padding: .5rem .3rem 1.2rem;
			border-bottom: 1px solid var(--line);
			margin-bottom: 1.1rem;
		}
		.brand-line { display: flex; align-items: center; gap: .55rem; min-width: 0; }
		.brand-logo-img { display: block; width: 3.7rem; height: 3.7rem; flex: none; object-fit: contain; filter: drop-shadow(0 0 9px rgba(114,255,145,.2)); }
		.brand-mark {
			width: 2.25rem; height: 2.25rem; display: grid; place-items: center;
			border: 1px solid var(--green); color: var(--green); border-radius: 50%;
			font: 700 1rem var(--mono); box-shadow: 0 0 16px rgba(114,255,145,.18);
		}
		.brand-name { color: var(--green); font: 700 1.22rem var(--display); letter-spacing: .065em; white-space: nowrap; }
		.brand-letter { display: inline-block; color: var(--amber); font-size: 1.35em; line-height: .82; vertical-align: -.06em; text-shadow: 0 0 10px rgba(255,196,92,.42); }
		.brand-sub { color: #8da695; font: 500 .57rem var(--mono); letter-spacing: .1em; line-height: 1.5; margin-top: .35rem; }
		.nav-kicker, .eyebrow { color: var(--green); font: 600 .66rem var(--mono); letter-spacing: .16em; text-transform: uppercase; }
		[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none; }
		[data-testid="stSidebar"] [role="radiogroup"] { gap: .28rem; }
		[data-testid="stSidebar"] [role="radiogroup"] label {
			display: flex !important; align-items: center; min-height: 2.45rem; padding: .48rem .6rem; border: 1px solid transparent;
			border-left: 2px solid transparent; background: transparent;
			color: #a5b5a8; transition: background .15s ease, color .15s ease;
		}
		[data-testid="stSidebar"] label[data-testid="stRadioOption"]:before {
			content: ''; display: inline-block; flex: 0 0 .48rem; width: .48rem; height: .48rem;
			margin-right: .62rem; border: 1px solid #55735c; border-radius: 50%; background: #0a1510;
		}
		[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child { display: none; }
		[data-testid="stSidebar"] [role="radiogroup"] label:hover {
			background: rgba(77, 255, 125, .07); border-color: var(--line); color: var(--text);
		}
		[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
			background: rgba(66, 255, 117, .1); border-color: rgba(114,255,145,.24);
			border-left-color: var(--green); color: var(--green);
		}
		[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"]:before {
			background: var(--green); border-color: var(--green); box-shadow: 0 0 9px rgba(114,255,145,.7);
		}
		[data-testid="stSidebar"] [role="radiogroup"] label p { font: 600 .78rem var(--display); letter-spacing: .04em; }
		[data-testid="stVerticalBlockBorderWrapper"] {
			background: linear-gradient(145deg, rgba(12,27,18,.96), rgba(7,17,11,.96));
			border: 1px solid var(--line) !important; border-radius: 2px !important;
			padding: .72rem .85rem; box-shadow: inset 0 1px rgba(190,255,200,.025), 0 12px 26px rgba(0,0,0,.16);
		}
		[data-testid="stVerticalBlockBorderWrapper"] > div { gap: .45rem; }
		.status-strip {
			display: grid; grid-template-columns: repeat(7, minmax(0, 1fr));
			border: 1px solid var(--line); border-top: 2px solid var(--green-dim);
			background: linear-gradient(100deg, rgba(11,25,16,.97), rgba(8,18,12,.9));
			margin: 0 0 1.2rem; box-shadow: 0 8px 24px rgba(0,0,0,.18);
		}
		.status-cell { min-width: 0; padding: .62rem .72rem .58rem; border-right: 1px solid var(--line); }
		.status-cell:last-child { border-right: 0; }
		.status-label { color: var(--muted); font: 500 .57rem var(--mono); letter-spacing: .08em; white-space: nowrap; }
		.status-value { color: var(--text); font: 600 .83rem var(--mono); margin-top: .28rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
		.status-value.good { color: var(--green); }
		.status-value.warn { color: var(--amber); }
		.status-value.hostile { color: var(--red); }
		.page-heading { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin: .25rem 0 1rem; }
		.page-heading h1 { color: #e5f4e7; font: 700 clamp(1.3rem, 2vw, 1.8rem) var(--display); letter-spacing: .06em; margin: .2rem 0 0; }
		.page-heading .subline { color: var(--muted); font: 500 .67rem var(--mono); letter-spacing: .08em; text-align: right; }
		.panel {
			position: relative; background: linear-gradient(145deg, rgba(12,27,18,.96), rgba(7,17,11,.96));
			border: 1px solid var(--line); border-radius: 2px; padding: 1rem 1.05rem;
			box-shadow: inset 0 1px rgba(190,255,200,.025), 0 12px 26px rgba(0,0,0,.16);
		}
		.panel:before { content: ''; position: absolute; left: -1px; top: -1px; width: 2.7rem; height: 2px; background: var(--green); }
		.panel-title { display: flex; align-items: center; justify-content: space-between; gap: .75rem; color: var(--green); font: 600 .78rem var(--display); letter-spacing: .11em; text-transform: uppercase; margin-bottom: .7rem; }
		.panel-meta { color: var(--muted); font: 500 .58rem var(--mono); letter-spacing: .07em; }
		.map-frame { overflow: hidden; border: 1px solid rgba(114,255,145,.24); background: #07130c; }
		.map-topline { display: flex; justify-content: space-between; align-items: center; gap: .75rem; padding: .58rem .8rem; border-bottom: 1px solid var(--line); color: #a6bbaa; font: 500 .62rem var(--mono); letter-spacing: .08em; }
		.map-state { color: var(--amber); border: 1px solid rgba(255,196,92,.5); padding: .22rem .38rem; }
		.map-surface {
			position: relative; min-height: 410px; aspect-ratio: 1.65 / 1; overflow: hidden;
			background-color: #08170f;
			background-image: linear-gradient(rgba(95,168,106,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(95,168,106,.08) 1px, transparent 1px), linear-gradient(rgba(95,168,106,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(95,168,106,.025) 1px, transparent 1px);
			background-size: 42px 42px, 42px 42px, 8px 8px, 8px 8px;
		}
		.map-surface:after { content: ''; position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse at 52% 52%, transparent 20%, rgba(2,7,4,.52) 100%); }
		.map-contour { position: absolute; border: 1px solid rgba(114,255,145,.1); border-radius: 47% 53% 62% 38%; transform: rotate(-21deg); }
		.contour-a { width: 62%; height: 39%; left: 7%; top: 14%; }
		.contour-b { width: 49%; height: 57%; right: 5%; bottom: -13%; transform: rotate(14deg); }
		.contour-c { width: 25%; height: 23%; left: 37%; top: 38%; transform: rotate(41deg); }
		.radar-ring { position: absolute; left: 48%; top: 48%; width: 17rem; height: 17rem; border: 1px solid rgba(89,227,215,.25); border-radius: 50%; transform: translate(-50%,-50%); box-shadow: 0 0 35px rgba(89,227,215,.045), inset 0 0 30px rgba(89,227,215,.035); }
		.radar-ring:before, .radar-ring:after { content: ''; position: absolute; border: 1px solid rgba(89,227,215,.22); border-radius: 50%; inset: 22%; }
		.radar-ring:after { inset: 43%; }
		.radar-sweep { position: absolute; left: 48%; top: 48%; width: 17rem; height: 17rem; border-radius: 50%; transform: translate(-50%,-50%); background: conic-gradient(from 18deg, transparent 0deg 285deg, rgba(66,255,128,.03) 315deg, rgba(66,255,128,.2) 358deg, transparent 360deg); animation: sweep 12s linear infinite; }
		@keyframes sweep { to { transform: translate(-50%,-50%) rotate(360deg); } }
		.map-crosshair { position: absolute; left: 48%; top: 48%; width: 1px; height: 100%; background: rgba(89,227,215,.11); transform: translateX(-50%); }
		.map-crosshair.horizontal { width: 100%; height: 1px; transform: translateY(-50%); }
		.map-path { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 2; }
		.map-path path { fill: none; stroke: rgba(255,82,105,.75); stroke-width: 1.5; stroke-dasharray: 6 5; vector-effect: non-scaling-stroke; }
		.map-path .axis { stroke: rgba(89,227,215,.34); stroke-dasharray: 2 6; }
		.map-marker { position: absolute; z-index: 3; font: 600 .58rem var(--mono); letter-spacing: .04em; white-space: nowrap; }
		.map-marker .symbol { display: grid; place-items: center; width: 1.35rem; height: 1.35rem; margin-bottom: .28rem; }
		.marker-hostile { left: 68%; top: 28%; color: var(--red); }
		.marker-hostile .symbol { border: 1px solid var(--red); background: rgba(255,82,105,.18); transform: rotate(45deg); box-shadow: 0 0 14px rgba(255,82,105,.45); }
		.marker-hostile .symbol span { transform: rotate(-45deg); }
		.marker-sensor { left: 41%; top: 48%; color: var(--cyan); }
		.marker-sensor .symbol { border: 1px solid var(--cyan); border-radius: 50%; color: var(--cyan); box-shadow: 0 0 13px rgba(89,227,215,.3); }
		.marker-asset { left: 27%; top: 68%; color: var(--green); }
		.marker-asset .symbol { border: 1px solid var(--green); color: var(--green); background: rgba(114,255,145,.09); }
		.map-coordinate { position: absolute; z-index: 4; color: rgba(165,197,169,.58); font: .55rem var(--mono); }
		.coord-nw { top: .65rem; left: .7rem; }.coord-se { right: .7rem; bottom: .65rem; }
		.map-legend { display: flex; flex-wrap: wrap; gap: .6rem 1rem; padding: .62rem .8rem; border-top: 1px solid var(--line); color: #a2b5a5; font: 500 .57rem var(--mono); }
		.legend-item { display: inline-flex; align-items: center; gap: .38rem; }
		.legend-dot { width: .48rem; height: .48rem; display: inline-block; border-radius: 50%; }
		.dot-red { background: var(--red); box-shadow: 0 0 7px var(--red); }.dot-cyan { background: var(--cyan); }.dot-green { background: var(--green); }.dot-ring { border: 1px solid var(--cyan); }
		.threat-card { padding: .85rem; border: 1px solid rgba(255,82,105,.42); border-left: 3px solid var(--red); background: linear-gradient(110deg, rgba(72,19,26,.35), rgba(10,19,13,.7)); margin: .72rem 0; }
		.threat-type { color: #ff9ba8; font: 700 1.03rem var(--display); letter-spacing: .05em; }
		.threat-status { color: var(--red); font: 600 .59rem var(--mono); letter-spacing: .08em; margin-top: .25rem; }
		.data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .65rem .5rem; margin: .85rem 0; }
		.data-pair { border-bottom: 1px solid var(--line); padding: .42rem 0; }
		.data-key { display: block; color: var(--muted); font: 500 .55rem var(--mono); letter-spacing: .07em; text-transform: uppercase; }
		.data-value { display: block; color: var(--text); font: 600 .75rem var(--mono); margin-top: .22rem; }
		.action-readout { padding: .65rem .72rem; border: 1px solid rgba(255,196,92,.45); background: rgba(255,196,92,.07); color: var(--amber); font: 600 .77rem var(--mono); }
		.event-stream { display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: .55rem; margin-top: .65rem; }
		.event-item { position: relative; padding: .67rem .68rem .7rem .8rem; border: 1px solid var(--line); border-left: 2px solid var(--green-dim); background: rgba(9,20,13,.82); min-height: 5.5rem; }
		.event-item.alert { border-left-color: var(--red); }.event-item.warning { border-left-color: var(--amber); }.event-item.info { border-left-color: var(--cyan); }
		.event-time { color: var(--muted); font: 500 .54rem var(--mono); }
		.event-name { color: var(--green); font: 600 .68rem var(--mono); letter-spacing: .035em; margin: .27rem 0; }
		.event-item.alert .event-name { color: #ff8797; }.event-item.warning .event-name { color: var(--amber); }.event-item.info .event-name { color: var(--cyan); }
		.event-details { color: #bac8bc; font: 400 .68rem var(--display); line-height: 1.4; }
		.readout-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .65rem; }
		.readout { min-height: 5.3rem; padding: .72rem; border: 1px solid var(--line); background: rgba(7,16,10,.62); }
		.readout-label { color: var(--muted); font: 500 .58rem var(--mono); letter-spacing: .08em; text-transform: uppercase; }
		.readout-value { color: var(--text); font: 600 1.08rem var(--display); margin-top: .5rem; }
		.readout-value.green { color: var(--green); }.readout-value.amber { color: var(--amber); }.readout-value.red { color: var(--red); }
		.verdict { padding: 1.15rem; border: 1px solid var(--green-dim); background: rgba(33,133,65,.12); color: var(--green); font: 700 1.05rem var(--display); letter-spacing: .08em; text-align: center; }
		.verdict.bad { border-color: var(--red); background: rgba(133,33,49,.12); color: var(--red); }
		.gauge-wrap { display: grid; place-items: center; padding: .6rem; }
		.score-gauge { --score-angle: 0deg; width: 12rem; aspect-ratio: 1; position: relative; display: grid; place-items: center; border-radius: 50%; background: conic-gradient(from -90deg, var(--green) 0deg var(--score-angle), rgba(114,255,145,.12) var(--score-angle) 360deg); box-shadow: 0 0 28px rgba(114,255,145,.1); }
		.score-gauge:before { content: ''; position: absolute; inset: .55rem; background: #09150e; border: 1px solid var(--line); border-radius: 50%; }
		.gauge-text { z-index: 1; text-align: center; }.gauge-number { color: var(--green); font: 700 2rem var(--mono); }.gauge-caption { color: var(--muted); font: 500 .57rem var(--mono); letter-spacing: .1em; }
		.score-bars { display: grid; gap: .8rem; margin: .7rem 0; }
		.score-row { display: grid; grid-template-columns: 8.5rem 1fr 3.2rem; align-items: center; gap: .65rem; }
		.score-label, .score-value { color: #bdcdbf; font: 500 .64rem var(--mono); }.score-value { text-align: right; color: var(--green); }
		.score-track { height: .45rem; background: rgba(121,164,128,.13); border: 1px solid var(--line); }
		.score-fill { height: 100%; background: linear-gradient(90deg, var(--green-dim), var(--green)); box-shadow: 0 0 8px rgba(114,255,145,.24); }
		.action-list { display: grid; gap: .48rem; margin-top: .65rem; }
		.action-line { display: flex; gap: .6rem; padding: .55rem .65rem; background: rgba(10,22,14,.7); border: 1px solid var(--line); color: #c6d6c8; font: 400 .76rem var(--display); }
		.action-mark { color: var(--green); font: 600 .67rem var(--mono); }
		.missing-note { color: #9a987e; font: 500 .63rem var(--mono); line-height: 1.5; padding: .6rem .7rem; border-left: 2px solid var(--amber); background: rgba(255,196,92,.05); }
		.console-table { width: 100%; border-collapse: collapse; font: 500 .7rem var(--mono); }
		.console-table td { padding: .58rem .48rem; border-bottom: 1px solid var(--line); }
		.console-table td:first-child { color: var(--muted); width: 38%; text-transform: uppercase; font-size: .6rem; }
		.console-table td:last-child { color: var(--text); overflow-wrap: anywhere; }
		.stButton button, [data-testid="stDownloadButton"] button {
			background: rgba(56,168,83,.15); color: var(--green); border: 1px solid var(--green-dim);
			border-radius: 1px; font: 600 .68rem var(--mono); letter-spacing: .08em; text-transform: uppercase;
		}
		.stButton button:hover, [data-testid="stDownloadButton"] button:hover { background: rgba(70,255,120,.2); border-color: var(--green); color: #effff0; }
		[data-testid="stPlotlyChart"] { border: 1px solid var(--line); background: rgba(7,16,10,.36); }
		@media (max-width: 900px) {
			.block-container { padding: .7rem .8rem 1.5rem; }
			.status-strip { grid-template-columns: repeat(4, minmax(0,1fr)); }
			.status-cell:nth-child(4) { border-right: 0; }
			.status-cell:nth-child(n+5) { border-top: 1px solid var(--line); }
			.map-surface { min-height: 350px; }
		}
		@media (max-width: 760px) {
			[data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: .7rem !important; }
			[data-testid="stHorizontalBlock"] > [data-testid="column"] { width: 100% !important; min-width: 100% !important; flex: 1 1 100% !important; }
		}
		@media (max-width: 560px) {
			.status-strip { grid-template-columns: repeat(2, minmax(0,1fr)); }
			.status-cell { border-bottom: 1px solid var(--line); }
			.status-cell:nth-child(even) { border-right: 0; }
			.status-cell:nth-child(4) { border-right: 0; }
			.page-heading { align-items: start; flex-direction: column; }
			.page-heading .subline { text-align: left; }
			.map-surface { min-height: 300px; aspect-ratio: 1 / 1; }
			.radar-ring, .radar-sweep { width: 13rem; height: 13rem; }
			.score-row { grid-template-columns: 6.7rem 1fr 2.8rem; gap: .4rem; }
		}
		</style>
		""",
		unsafe_allow_html=True,
	)


def render_sidebar_brand(active_page: Any, page_map: dict[str, Any]) -> None:
	with st.sidebar:
		logo_markup = (
			f'<img class="brand-logo-img" src="{LOGO_DATA_URI}" alt="AeroVeda crest">'
			if LOGO_DATA_URI
			else '<div class="brand-mark">AV</div>'
		)
		st.markdown(
			f"""
			<div class="sidebar-brand">
				<div class="brand-line">{logo_markup}<div class="brand-name"><span class="brand-letter">A</span>ERO<span class="brand-letter">V</span>EDA</div></div>
				<div class="brand-sub">AI-ENABLED COUNTER-UAS<br>TRAINING PLATFORM</div>
			</div>
			<div class="nav-kicker">Command Navigation</div>
			""",
			unsafe_allow_html=True,
		)
		labels = list(page_map)
		if "aeroveda_navigation" not in st.session_state:
			st.session_state.aeroveda_navigation = active_page.title
		selected = st.radio(
			"Command navigation",
			labels,
			key="aeroveda_navigation",
			label_visibility="collapsed",
		)
		if selected != active_page.title:
			st.switch_page(page_map[selected])


def render_status_strip(record: dict[str, Any]) -> None:
	completed = str(record.get("status", "")).lower() == "completed"
	detection_accuracy = display_score(record.get("detectionAccuracy"))
	response_accuracy = "1/1 PASS" if record.get("responseCorrect") is True else (
		"1/1 FAIL" if record.get("responseCorrect") is False else "NOT SCORED"
	)
	active_threats = "0 / 1" if completed else ("1 TRACK" if record.get("actualThreatType") else "NONE")
	final_score = display_score(record.get("finalScore"))
	items = [
		("MISSION STATUS", record.get("status", "UNKNOWN"), "good" if completed else "warn"),
		("SCENARIO TYPE", record.get("scenarioEnvironment", "NOT RECORDED"), ""),
		("DIFFICULTY", record.get("difficultyLevel", "NOT RECORDED"), ""),
		("ACTIVE THREATS", active_threats, "hostile" if not completed else "good"),
		("DETECTION ACC.", detection_accuracy, "warn" if detection_accuracy == "NOT RECORDED" else "good"),
		("RESPONSE ACC.", response_accuracy, "good" if "PASS" in response_accuracy else "warn"),
		("CURRENT SCORE", final_score, "good"),
	]
	markup = "".join(
		f'<div class="status-cell"><div class="status-label">{escape(label)}</div>'
		f'<div class="status-value {kind}">{escape(value)}</div></div>'
		for label, value, kind in items
	)
	st.markdown(f'<div class="status-strip">{markup}</div>', unsafe_allow_html=True)


def page_heading(title: str, kicker: str, right: str = "") -> None:
	st.markdown(
		f'<div class="page-heading"><div><div class="eyebrow">{escape(kicker)}</div>'
		f'<h1>{escape(title)}</h1></div><div class="subline">{escape(right)}</div></div>',
		unsafe_allow_html=True,
	)


def panel_title(title: str, meta: str = "") -> str:
	return (
		f'<div class="panel-title"><span>{escape(title)}</span>'
		f'<span class="panel-meta">{escape(meta)}</span></div>'
	)


@contextmanager
def tactical_panel(title: str, meta: str = ""):
	with st.container(border=True):
		st.markdown(panel_title(title, meta), unsafe_allow_html=True)
		yield


def event_class(event_type: str) -> str:
	name = event_type.lower()
	if "threat" in name or "hostile" in name:
		return "alert"
	if "response" in name or "jam" in name:
		return "warning"
	if "mission" in name:
		return "info"
	return ""


def render_event_stream(record: dict[str, Any], limit: int | None = None) -> None:
	events = record.get("events", [])
	if limit is not None:
		events = events[-limit:]
	if not events:
		st.markdown('<div class="missing-note">NO EVENT RECORDS IN SESSION EXPORT</div>', unsafe_allow_html=True)
		return

	items = []
	for event in events:
		event_type = str(event.get("eventType", "EVENT"))
		items.append(
			f'<div class="event-item {event_class(event_type)}">'
			f'<div class="event-time">{escape(event.get("timestampUtc", "TIME NOT RECORDED"))}</div>'
			f'<div class="event-name">{escape(event_type.replace("_", " ").upper())}</div>'
			f'<div class="event-details">{escape(event.get("details", "No details recorded."))}</div></div>'
		)
	st.markdown(f'<div class="event-stream">{"".join(items)}</div>', unsafe_allow_html=True)


def render_live_threat(record: dict[str, Any]) -> None:
	completion = get_event(record, "MissionCompleted")
	status = "NEUTRALIZED / REPORTED" if completion else "TRACK STATUS NOT RECORDED"
	confidence = record.get("confidence", record.get("classificationConfidence"))
	range_value = record.get("rangeMeters", record.get("range"))
	speed_value = record.get("speedKph", record.get("speed"))
	action = record.get("recommendedResponse", "NOT RECORDED")
	with tactical_panel("Live Threat Feed", "1 TRACK / SESSION"):
		st.markdown(
			f'<div class="threat-card"><div class="threat-type">{escape(record.get("actualThreatType", "UNKNOWN"))}</div>'
			f'<div class="threat-status">{escape(status)}</div></div>',
			unsafe_allow_html=True,
		)
		rows = [
			("CONFIDENCE", display_score(confidence)),
			("RANGE", f"{escape(range_value)} m" if range_value is not None else "NOT RECORDED"),
			("SPEED", f"{escape(speed_value)} km/h" if speed_value is not None else "NOT RECORDED"),
			("CLASSIFICATION", record.get("classifiedThreatType", "NOT RECORDED")),
		]
		markup = "".join(
			f'<div class="data-pair"><span class="data-key">{escape(label)}</span>'
			f'<span class="data-value">{escape(value)}</span></div>'
			for label, value in rows
		)
		st.markdown(f'<div class="data-grid">{markup}</div>', unsafe_allow_html=True)
		st.markdown(
			f'<div class="data-key" style="margin-bottom:.35rem">RECOMMENDED ACTION</div>'
			f'<div class="action-readout">{escape(action).upper()}</div>',
			unsafe_allow_html=True,
		)


def render_mission_control() -> None:
	from dashboard.streamlit.mission_control import render_mission_control as render_view

	render_view()


def render_threat_detection() -> None:
	record = load_session_record()
	event = get_event(record, "ThreatDetected")
	page_heading("Threat Detection", "Sensor Picture", "DETECTION DATA / RECORDED SESSION")
	detection_time = record.get("detectionTimeSeconds")
	confidence = record.get("detectionConfidence")
	cols = st.columns(4)
	readouts = [
		("Detection", "CONFIRMED" if event else "NOT RECORDED", "green" if event else "amber"),
		("Time To Detect", f"{detection_time:.2f} SEC" if detection_time is not None else "NOT RECORDED", ""),
		("Detection Accuracy", display_score(record.get("detectionAccuracy")), "amber"),
		("Sensor Confidence", display_score(confidence), ""),
	]
	for col, (label, value, tone) in zip(cols, readouts):
		with col:
			st.markdown(
				f'<div class="readout"><div class="readout-label">{escape(label)}</div>'
				f'<div class="readout-value {tone}">{escape(value)}</div></div>',
				unsafe_allow_html=True,
			)
	left, right = st.columns([1.5, 1], gap="medium")
	with left:
		with tactical_panel("Detection Event", "SOURCE / EVENTS[]"):
			if event:
				render_event_stream({"events": [event]})
			else:
				st.markdown('<div class="missing-note">NO THREATDETECTED EVENT IN THIS EXPORT</div>', unsafe_allow_html=True)
	with right:
		with tactical_panel("Track Record", "SOURCE / SESSION RECORD"):
			st.markdown(
				f'<div class="data-grid"><div class="data-pair"><span class="data-key">THREAT</span><span class="data-value">{escape(record.get("actualThreatType", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">ENVIRONMENT</span><span class="data-value">{escape(record.get("scenarioEnvironment", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">RANGE</span><span class="data-value">{escape(record.get("rangeMeters", "NOT RECORDED"))}</span></div>'
				f'<div class="data-pair"><span class="data-key">TRACK ID</span><span class="data-value">{escape(record.get("trackId", "NOT RECORDED"))}</span></div></div>',
				unsafe_allow_html=True,
			)


def render_threat_classification() -> None:
	record = load_session_record()
	page_heading("Threat Classification", "Operator Assessment", "TRUTH / OPERATOR COMPARISON")
	actual = record.get("actualThreatType", "NOT RECORDED")
	classified = record.get("classifiedThreatType", record.get("classification", "NOT RECORDED"))
	correct = record.get("classificationCorrect")
	confidence = record.get("classificationConfidence", record.get("confidence"))
	verdict = "CORRECT CLASSIFICATION" if correct is True else "INCORRECT CLASSIFICATION" if correct is False else "NOT SCORED"
	verdict_class = "" if correct is True else "bad" if correct is False else ""
	truth_col, operator_col = st.columns(2, gap="medium")
	for col, label, value, tone in [
		(truth_col, "Actual Threat", actual, "red"),
		(operator_col, "Operator Classification", classified, "green" if correct else "red"),
	]:
		with col:
			st.markdown(
				f'<div class="panel"><div class="eyebrow">{label}</div>'
				f'<div style="font:700 clamp(1.5rem,3vw,2.5rem) var(--display);color:var(--{tone});padding:1.3rem 0;letter-spacing:.04em">{escape(value)}</div>'
				f'<div class="data-key">CONFIDENCE</div><div class="data-value">{display_score(confidence)}</div></div>',
				unsafe_allow_html=True,
			)
	st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
	st.markdown(f'<div class="verdict {verdict_class}">{verdict}</div>', unsafe_allow_html=True)
	event = get_event(record, "ThreatClassified")
	if event:
		with tactical_panel("Classification Record", "SOURCE / EVENTS[]"):
			render_event_stream({"events": [event]})
	else:
		st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
		st.markdown('<div class="missing-note">CLASSIFICATION EVENT NOT PRESENT IN SOURCE EXPORT</div>', unsafe_allow_html=True)


def render_tactical_response() -> None:
	record = load_session_record()
	event = get_event(record, "ResponseSelected")
	page_heading("Tactical Response", "Engagement Record", "DECISION / ADJUDICATION")
	selected = record.get("selectedResponse", record.get("response", "NOT RECORDED"))
	recommended = record.get("recommendedResponse", "NOT RECORDED")
	correct = record.get("responseCorrect")
	selected_col, recommended_col = st.columns(2, gap="medium")
	for col, title, value, tone in [
		(selected_col, "Operator Selected", selected, "green" if correct else "amber"),
		(recommended_col, "Recommended", recommended, "green"),
	]:
		with col:
			st.markdown(
				f'<div class="panel"><div class="eyebrow">{title}</div>'
				f'<div style="font:700 clamp(1.8rem,4vw,3.2rem) var(--display);color:var(--{tone});padding:1.1rem 0;letter-spacing:.08em">{escape(value).upper()}</div>'
				f'<div class="panel-meta">RESPONSE ACTION / SESSION RECORD</div></div>',
				unsafe_allow_html=True,
			)
	st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
	verdict = "RESPONSE ADJUDICATED CORRECT" if correct is True else "RESPONSE ADJUDICATED INCORRECT" if correct is False else "RESPONSE NOT SCORED"
	st.markdown(f'<div class="verdict {"" if correct is True else "bad" if correct is False else ""}">{verdict}</div>', unsafe_allow_html=True)
	if event:
		with tactical_panel("Decision Event", "SOURCE / EVENTS[]"):
			render_event_stream({"events": [event]})


def render_mission_timeline() -> None:
	record = load_session_record()
	page_heading("Mission Timeline", "Event Replay", f"{len(record.get('events', [])):02d} RECORDED EVENTS")
	with tactical_panel("Chronological Event Stream", "SOURCE / EVENTS[]"):
		render_event_stream(record)


def render_after_action_review() -> None:
	record = load_session_record()
	page_heading("After Action Review", "Mission Debrief", f"SESSION // {record.get('sessionId', 'N/A')}")
	score = float(record.get("finalScore", 0.0))
	score_pct = max(0.0, min(score * 100 if score <= 1 else score, 100.0))
	score_col, breakdown_col = st.columns([1, 1.65], gap="medium")
	with score_col:
		with tactical_panel("Mission Score", "FINAL ADJUDICATION"):
			st.markdown(
				f'<div class="gauge-wrap"><div class="score-gauge" style="--score-angle:{score_pct * 3.6:.1f}deg">'
				f'<div class="gauge-text"><div class="gauge-number">{score_pct:.1f}</div><div class="gauge-caption">MISSION SCORE / 100</div></div></div></div>',
				unsafe_allow_html=True,
			)
	with breakdown_col:
		with tactical_panel("Scoring Breakdown", "AWARDED POINTS"):
			breakdown = record.get("scoreBreakdown", {})
			if breakdown:
				max_value = max(max(float(value) for value in breakdown.values()), 1.0)
				rows = "".join(
					f'<div class="score-row"><span class="score-label">{escape(str(key).replace("_", " ").upper())}</span>'
					f'<div class="score-track"><div class="score-fill" style="width:{max(0,min(float(value) / max_value * 100, 100)):.1f}%"></div></div>'
					f'<span class="score-value">{float(value):g} PTS</span></div>'
					for key, value in breakdown.items()
				)
				st.markdown(f'<div class="score-bars">{rows}</div>', unsafe_allow_html=True)
			else:
				st.markdown('<div class="missing-note">NO SCORING BREAKDOWN RECORDED</div>', unsafe_allow_html=True)

	correct_actions = []
	mistakes = []
	for field, label in [("classificationCorrect", "Threat classification"), ("responseCorrect", "Response selection")]:
		if record.get(field) is True:
			correct_actions.append(label)
		elif record.get(field) is False:
			mistakes.append(label)
	debrief_left, debrief_right = st.columns(2, gap="medium")
	with debrief_left:
		with tactical_panel("Recorded Errors", "ADJUDICATED FIELDS"):
			if mistakes:
				for item in mistakes:
					st.markdown(f'<div class="action-line"><span class="action-mark" style="color:var(--red)">!</span>{escape(item)}</div>', unsafe_allow_html=True)
			else:
				st.markdown('<div class="action-line"><span class="action-mark">OK</span>No classification or response error recorded.</div>', unsafe_allow_html=True)
	with debrief_right:
		with tactical_panel("Correct Actions", "ADJUDICATED FIELDS"):
			if correct_actions:
				for item in correct_actions:
					st.markdown(f'<div class="action-line"><span class="action-mark">OK</span>{escape(item)}</div>', unsafe_allow_html=True)
			else:
				st.markdown('<div class="missing-note">NO CORRECT ACTIONS RECORDED</div>', unsafe_allow_html=True)

	recommendation = record.get("trainingRecommendation", "No recommendation recorded.")
	with tactical_panel("Training Recommendation", "SOURCE / SESSION RECORD"):
		st.markdown(f'<div class="action-line"><span class="action-mark">NEXT</span>{escape(recommendation)}</div>', unsafe_allow_html=True)
	with tactical_panel("Timeline Replay", "RECORDED EVENTS"):
		render_event_stream(record)


def build_competency_radar(record: dict[str, Any]) -> go.Figure:
	breakdown = record.get("scoreBreakdown", {})
	labels = {
		"detection": "Detection",
		"classification": "Classification",
		"protocol": "Protocol",
		"response": "Response",
	}
	categories = [label for key, label in labels.items() if key in breakdown]
	values = [float(breakdown[key]) for key in labels if key in breakdown]
	if categories:
		categories = categories + [categories[0]]
		values = values + [values[0]]
	figure = go.Figure(
		go.Scatterpolar(
			r=values,
			theta=categories,
			fill="toself",
			fillcolor="rgba(83, 255, 128, 0.14)",
			line={"color": "#72ff91", "width": 2},
			marker={"color": "#72ff91", "size": 6},
			hovertemplate="%{theta}<br>%{r} awarded points<extra></extra>",
		)
	)
	max_value = max(values[:-1], default=1)
	figure.update_layout(
		showlegend=False,
		margin={"l": 42, "r": 42, "t": 28, "b": 30},
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		font={"family": "IBM Plex Mono, monospace", "color": "#a9c2ae", "size": 10},
		polar={
			"bgcolor": "rgba(5, 14, 8, .72)",
			"radialaxis": {"visible": True, "range": [0, max_value * 1.2], "gridcolor": "rgba(122, 184, 132, .2)", "linecolor": "rgba(122, 184, 132, .2)", "tickfont": {"size": 9}},
			"angularaxis": {"gridcolor": "rgba(122, 184, 132, .24)", "linecolor": "rgba(122, 184, 132, .24)", "tickfont": {"size": 10}},
		},
	)
	return figure


def render_competency_assessment() -> None:
	record = load_session_record()
	page_heading("Competency Assessment", "Operator Performance", "WEIGHTED POINTS / SOURCE BREAKDOWN")
	breakdown = record.get("scoreBreakdown", {})
	if not breakdown:
		st.markdown('<div class="missing-note">NO SCOREBREAKDOWN DATA IN SESSION EXPORT</div>', unsafe_allow_html=True)
		return

	weakest = min(breakdown, key=lambda key: float(breakdown[key]))
	strongest = max(breakdown, key=lambda key: float(breakdown[key]))
	score_pct = display_score(record.get("finalScore"))
	cols = st.columns(3)
	for col, label, value, tone in [
		(cols[0], "Overall Mission Score", score_pct, "green"),
		(cols[1], "Lowest Point Contribution", weakest.replace("_", " ").upper(), "amber"),
		(cols[2], "Highest Point Contribution", strongest.replace("_", " ").upper(), "green"),
	]:
		with col:
			st.markdown(
				f'<div class="readout"><div class="readout-label">{escape(label)}</div>'
				f'<div class="readout-value {tone}">{escape(value)}</div></div>',
				unsafe_allow_html=True,
			)
	chart_col, facts_col = st.columns([1.3, 1], gap="medium")
	with chart_col:
		with tactical_panel("Competency Radar", "AWARDED POINTS / NOT MASTERY RATES"):
			st.plotly_chart(build_competency_radar(record), width="stretch", config={"displayModeBar": False})
	with facts_col:
		with tactical_panel("Performance Readout", "SOURCE / SCOREBREAKDOWN"):
			rows = "".join(
				f'<div class="score-row"><span class="score-label">{escape(key.replace("_", " ").upper())}</span>'
				f'<div class="score-track"><div class="score-fill" style="width:{max(0,min(float(value),100)):.1f}%"></div></div>'
				f'<span class="score-value">{float(value):g}</span></div>'
				for key, value in breakdown.items()
			)
			st.markdown(f'<div class="score-bars">{rows}</div>', unsafe_allow_html=True)
			st.markdown('<div class="missing-note">SITUATIONAL AWARENESS: NOT SCORED IN THIS EXPORT. SCOREBREAKDOWN VALUES ARE AWARDED POINTS, NOT NORMALIZED SKILL RATES.</div>', unsafe_allow_html=True)
	weakest_label = weakest.replace("_", " ").title()
	strongest_label = strongest.replace("_", " ").title()
	with tactical_panel("Training Direction", "DERIVED FROM RECORDED SCORES"):
		st.markdown(
			f'<div class="action-list"><div class="action-line"><span class="action-mark" style="color:var(--amber)">FOCUS</span>'
			f"Review {escape(weakest_label)} in a follow-on scenario; it has the fewest awarded points in this record.</div>"
			f'<div class="action-line"><span class="action-mark">SUSTAIN</span>'
			f"Maintain performance in {escape(strongest_label)}, the highest point contribution in this record.</div></div>",
			unsafe_allow_html=True,
		)


def render_instructor_console() -> None:
	record = load_session_record()
	page_heading("Instructor Console", "Session Oversight", "REVIEW / EXPORT")
	events = record.get("events", [])
	metadata = [
		("Session ID", record.get("sessionId", "NOT RECORDED")),
		("Scenario", record.get("scenarioId", "NOT RECORDED")),
		("Operator", record.get("operatorId", "NOT RECORDED")),
		("Status", record.get("status", "NOT RECORDED")),
		("Start Time UTC", record.get("startTimeUtc", "NOT RECORDED")),
		("End Time UTC", record.get("endTimeUtc", "NOT RECORDED")),
		("Event Count", len(events)),
		("Source Record", DATA_FILE.name),
	]
	with tactical_panel("Session Record", "READ-ONLY SOURCE / JSON"):
		rows = "".join(
			f'<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>'
			for label, value in metadata
		)
		st.markdown(f'<table class="console-table">{rows}</table>', unsafe_allow_html=True)
	with tactical_panel("Export Artifact", "SESSION RECORD / JSON"):
		st.download_button(
			"Download Session JSON",
			data=json.dumps(record, indent=2),
			file_name=f"{record.get('sessionId', 'session')}.json",
			mime="application/json",
			icon=":material/download:",
			width="stretch",
		)