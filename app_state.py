import gc
import hashlib

import streamlit as st


class AppState:
    """Manage Streamlit session state."""

    @staticmethod
    def initialize() -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "repositories" not in st.session_state:
            st.session_state.repositories = {}

        if "github_url" not in st.session_state:
            st.session_state.github_url = ""

    @staticmethod
    def reset_chat() -> None:
        st.session_state.messages = []
        gc.collect()

    @staticmethod
    def repository_key(github_url: str) -> str:
        return hashlib.sha256(github_url.encode("utf-8")).hexdigest()