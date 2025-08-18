# pages/03_Content_Engine.py — scaffold placeholder
from __future__ import annotations
import streamlit as st
from shared import state, ui

state.init()
ui.title("Content Engine — A/B/C")

st.info("This is the scaffold. Paste your existing Content Engine UI/logic here.\n\n"
        "It should read company + brand rules from shared.state and write results to shared.history.")
