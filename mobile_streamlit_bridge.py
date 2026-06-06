from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from classic_navigation import get_classic_quiz_mode
from mobile_ranking import load_mobile_rankings_request
from mobile_score_sync import save_mobile_score_request


BASE_DIR = Path(__file__).resolve().parent
MOBILE_APP_DIR = BASE_DIR / "mobile_app"
MOBILE_AUDIO_MANIFEST = MOBILE_APP_DIR / "data" / "audio_manifest.json"
DRIVE_AUDIO_DOWNLOAD_BASE = "https://drive.google.com/uc?export=download&id="
COMPONENT_VOCAB_AUDIO_BASE = "./audio/"
COMPONENT_SENTENCE_AUDIO_BASE = "./sentence-audio/"
MOBILE_RANKING_CACHE_TTL_SEC = 120
SUPPORTED_MOBILE_LANGS = {"ja", "zh", "ko"}
MOBILE_CLASSIC_LINK_LABELS = {
    "ja": "従来のStreamlit版を開く",
    "zh": "打开传统 Streamlit 版",
    "ko": "기존 Streamlit 버전 열기",
}

_mobile_component = components.declare_component(
    "esperanto_mobile_pwa",
    path=str(MOBILE_APP_DIR),
)


TRUE_VALUES = {"1", "true", "yes", "on"}


def _query_flag(name: str) -> bool:
    try:
        return str(st.query_params.get(name, "")).strip().lower() in TRUE_VALUES
    except Exception:
        return False


def should_render_mobile_app(is_mobile: bool) -> bool:
    """Use the browser-side mobile app unless the user explicitly asks for classic Streamlit."""
    if _query_flag("classic"):
        return False
    if _query_flag("mobile_app"):
        return True
    return bool(is_mobile)


def _mobile_audio_config() -> dict:
    try:
        config = dict(st.secrets.get("mobile_audio", {}))
    except Exception:
        config = {}
    vocab_base_url = str(config.get("vocab_base_url", "")).strip() or COMPONENT_VOCAB_AUDIO_BASE
    sentence_base_url = str(config.get("sentence_base_url", "")).strip() or COMPONENT_SENTENCE_AUDIO_BASE
    drive_download_base_url = str(config.get("drive_download_base_url", "")).strip() or DRIVE_AUDIO_DOWNLOAD_BASE
    manifest_available = MOBILE_AUDIO_MANIFEST.exists()
    enabled = bool(vocab_base_url or sentence_base_url or manifest_available)
    return {
        "enabled": enabled,
        "vocabBaseUrl": vocab_base_url,
        "sentenceBaseUrl": sentence_base_url,
        "driveDownloadBaseUrl": drive_download_base_url,
        "useDriveManifest": manifest_available,
    }


def _mobile_lang_from_source(source: str) -> str:
    suffix = str(source or "").rsplit("_", 1)[-1].lower()
    return suffix if suffix in SUPPORTED_MOBILE_LANGS else "ja"


def _mobile_mode_from_source(source: str) -> str:
    return "sentence" if str(source or "").startswith("sentence") else "vocab"


def render_mobile_app_entry(
    is_mobile: bool,
    *,
    source: str,
    target_lang: str | None = None,
    default_mode: str | None = None,
) -> bool:
    """Render the localStorage-backed mobile app inside Streamlit Cloud.

    Streamlit's built-in static file serving is intentionally limited and does not
    serve arbitrary HTML/JS apps with browser-friendly MIME types. A local
    Streamlit component gives us a Cloud-compatible iframe while keeping desktop
    users on the existing app.
    """
    if not should_render_mobile_app(is_mobile):
        return False

    lang = str(target_lang or _mobile_lang_from_source(source)).strip().lower()
    if lang not in SUPPORTED_MOBILE_LANGS:
        lang = "ja"
    fallback_mode = str(default_mode or _mobile_mode_from_source(source)).strip().lower()
    if fallback_mode not in {"vocab", "sentence"}:
        fallback_mode = "vocab"
    mode = get_classic_quiz_mode(default=fallback_mode)

    st.session_state.setdefault("mobile_score_sync_result", None)
    st.session_state.setdefault("mobile_score_sync_processed", {})
    st.session_state.setdefault("mobile_ranking_result", None)
    st.session_state.setdefault("mobile_ranking_processed", {})
    st.session_state.setdefault("mobile_ranking_cached_result", None)
    st.session_state.setdefault("mobile_ranking_cache_ts", 0.0)

    st.markdown(
        """
        <style>
        div[data-testid="stToolbar"], div[data-testid="stDecoration"],
        header[data-testid="stHeader"], #MainMenu, footer {
            display: none !important;
        }
        div[data-testid="stAppViewContainer"] {
            background: #f7f8f4 !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
        iframe[title*="esperanto_mobile_pwa"] {
            display: block !important;
            width: 100% !important;
            min-height: 640px !important;
            border: 0 !important;
        }
        div[data-testid="stVerticalBlock"],
        div[data-testid="stVerticalBlock"] > div,
        div[data-testid="stElementContainer"] {
            gap: 0 !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    component_value = _mobile_component(
        source=source,
        mobileConfig={
            "source": source,
            "targetLang": lang,
            "defaultMode": mode,
        },
        scoreSyncResult=st.session_state.mobile_score_sync_result,
        rankingResult=st.session_state.mobile_ranking_result,
        audioConfig=_mobile_audio_config(),
        default=None,
        key=f"esperanto_mobile_pwa_{source}",
        height=900,
    )
    if isinstance(component_value, dict) and component_value.get("type") == "save_score":
        request_id = str(component_value.get("requestId", "")).strip()
        processed = st.session_state.mobile_score_sync_processed
        if request_id and request_id not in processed:
            result = save_mobile_score_request(component_value)
            st.session_state.mobile_score_sync_result = result
            processed[request_id] = bool(result.get("ok"))
            if len(processed) > 100:
                for key in list(processed.keys())[:-100]:
                    processed.pop(key, None)
            st.rerun()
    if isinstance(component_value, dict) and component_value.get("type") == "load_rankings":
        request_id = str(component_value.get("requestId", "")).strip()
        processed = st.session_state.mobile_ranking_processed
        if request_id and request_id not in processed:
            force = bool(component_value.get("force"))
            cached = st.session_state.get("mobile_ranking_cached_result")
            cache_age = time.time() - float(st.session_state.get("mobile_ranking_cache_ts") or 0.0)
            if not force and isinstance(cached, dict) and cache_age < MOBILE_RANKING_CACHE_TTL_SEC:
                result = dict(cached)
                result["requestId"] = request_id
            else:
                result = load_mobile_rankings_request(component_value)
                if result.get("ok"):
                    st.session_state.mobile_ranking_cached_result = dict(result)
                    st.session_state.mobile_ranking_cache_ts = time.time()
            st.session_state.mobile_ranking_result = result
            processed[request_id] = bool(result.get("ok"))
            if len(processed) > 100:
                for key in list(processed.keys())[:-100]:
                    processed.pop(key, None)
            st.rerun()
    classic_label = MOBILE_CLASSIC_LINK_LABELS.get(lang, MOBILE_CLASSIC_LINK_LABELS["ja"])
    st.markdown(
        f"""
        <div style="padding: 8px 12px 16px; text-align: center; font-size: 13px;">
            <a href="?classic=1&quiz={mode}" target="_self" rel="nofollow" style="color: #075f46; font-weight: 700;">
                {classic_label}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True
