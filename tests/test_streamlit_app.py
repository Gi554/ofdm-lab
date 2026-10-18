from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app/streamlit_app.py"


def app():
    return AppTest.from_file(str(APP), default_timeout=45).run()


def test_initial_simulation_and_snapshot_not_silently_relabelled():
    at = app()
    assert not at.exception
    assert len(at.metric) == 4
    original = at.session_state["result"]["settings"]["ebn0_db"]
    at.slider(key="ebn0").set_value(18).run()
    assert at.session_state["result"]["settings"]["ebn0_db"] == original
    assert any("Réglages modifiés" in x.value for x in at.info)
    at.button(key="run").click().run()
    assert not at.exception
    assert at.session_state["result"]["settings"]["ebn0_db"] == 18


def test_saved_history_comparison_and_ber_sweep():
    at = app()
    at.button(key="save").click().run()
    assert len(at.session_state["history"]) == 1
    at.radio(key="page").set_value("Comparaisons").run()
    at.slider(key="frames").set_value(16).run()
    at.multiselect(key="levels").set_value([6, 18]).run()
    at.button(key="sweep").click().run()
    assert not at.exception
    assert len(at.session_state["sweep_result"]["rows"]) == 10
    del at.session_state["sweep_result"]["levels"]
    at.run()
    assert not at.exception
    assert at.session_state["sweep_result"]["levels"] == [6, 18]
    at.multiselect(key="levels").set_value([6]).run()
    assert at.session_state["sweep_result"]["levels"] == [6, 18]
    assert any("Le balayage affiché" in x.value for x in at.info)
    at.button(key="clear_history").click().run()
    assert at.session_state["history"] == []


def test_image_transmission_and_repere_page():
    at = app()
    at.radio(key="page").set_value("Image").run()
    at.selectbox(key="channel").set_value("AWGN").run()
    at.slider(key="ebn0").set_value(30).run()
    at.button(key="image_run").click().run()
    assert not at.exception
    assert at.session_state["image_result"]["trial"].reception.image_crc_valid is True
    at.radio(key="page").set_value("Repères").run()
    assert not at.exception


def test_short_cp_warning_and_mmse_estimated_channel():
    at = app()
    at.slider(key="cp_64").set_value(0).run()
    at.selectbox(key="estimation").set_value("Pilotes LS").run()
    at.selectbox(key="equalizer").set_value("MMSE").run()
    at.button(key="run").click().run()
    assert not at.exception
    assert not at.session_state["result"]["selected"]["cp_sufficient"]
    assert at.session_state["result"]["selected"]["method"] == "pilot_mmse"
    assert at.warning
