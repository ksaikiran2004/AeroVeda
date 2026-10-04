from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
	sys.path.insert(0, str(REPOSITORY_ROOT))

from dashboard.streamlit import command_center, command_landing


st.set_page_config(
	page_title="AeroVeda | Mission Control",
	page_icon=":material/radar:",
	layout="wide",
	initial_sidebar_state="auto",
)

command_center.inject_theme()

routes = {
	"Command Center": (command_landing.render_command_center, "home_app_logo"),
	"Mission Control": (command_center.render_mission_control, "radar"),
	"Threat Detection": (command_center.render_threat_detection, "sensors"),
	"Threat Classification": (command_center.render_threat_classification, "target"),
	"Tactical Response": (command_center.render_tactical_response, "bolt"),
	"Mission Timeline": (command_center.render_mission_timeline, "timeline"),
	"After Action Review": (command_center.render_after_action_review, "fact_check"),
	"Competency Assessment": (command_center.render_competency_assessment, "monitoring"),
	"Instructor Console": (command_center.render_instructor_console, "school"),
}
pages = {
	title: st.Page(
		render,
		title=title,
		icon=f":material/{icon}:",
		default=title == "Command Center",
	)
	for title, (render, icon) in routes.items()
}
command_landing.bind_pages(pages)
active_page = st.navigation(list(pages.values()), position="hidden")

record = command_center.load_session_record()
command_center.render_sidebar_brand(active_page, pages)
command_center.render_status_strip(record)
active_page.run()
