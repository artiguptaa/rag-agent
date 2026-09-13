import asyncio
from typing import Any

import streamlit as st

from app_state import AppState
from rag_engine import RAGEngineFactory
from repository_service import GitHubRepositoryService
from response_streamer import AsyncResponseStreamer


class GitHubRAGApp:
    """Coordinate the Streamlit UI and application workflow."""

    def __init__(self) -> None:
        self.repository_service = GitHubRepositoryService()
        self.engine_factory = RAGEngineFactory()
        self.streamer = AsyncResponseStreamer()

    def run(self) -> None:
        AppState.initialize()
        self.render_sidebar()
        self.render_header()
        self.render_chat_history()
        self.handle_chat_input()

    def render_sidebar(self) -> None:
        with st.sidebar:
            st.header("Add your GitHub repository")

            github_url = st.text_input(
                "GitHub repository URL",
                value=st.session_state.github_url,
                placeholder="https://github.com/user/repository",
            )
            st.session_state.github_url = github_url

            if st.button("Load Repository", use_container_width=True):
                self.load_repository(github_url)

            if st.session_state.repositories:
                st.success("Repository ready for chat.")

    def load_repository(self, github_url: str) -> None:
        if not github_url.strip():
            st.warning("Enter a GitHub repository URL first.")
            return

        repository_key = AppState.repository_key(github_url)

        if repository_key in st.session_state.repositories:
            st.success("Repository already loaded.")
            return

        status = st.status("Preparing repository...", expanded=True)

        try:
            status.write("Downloading and extracting repository content...")
            content = self.run_async(
                self.repository_service.ingest_repository,
                github_url,
            )
            status.write("Repository content extracted.")

            status.write("Parsing repository documents...")
            documents = self.run_async(
                self.repository_service.load_documents,
                content,
            )
            status.write(f"Parsed {len(documents)} document(s).")

            status.write("Loading the language model and embedding model...")
            status.write("Creating chunks and generating embeddings...")
            query_engine = self.run_async(
                self.engine_factory.build,
                documents,
            )
            status.write("Vector index created.")

            st.session_state.repositories[repository_key] = query_engine
            status.update(
                label="Repository is ready for chat.",
                state="complete",
                expanded=False,
            )
        except Exception as error:
            status.update(
                label="Repository loading failed.",
                state="error",
                expanded=True,
            )
            st.error(f"Could not process repository: {error}")

    @staticmethod
    def run_async(function: Any, *args: Any) -> Any:
        async def execute() -> Any:
            return await asyncio.to_thread(function, *args)

        return asyncio.run(execute())

    def render_header(self) -> None:
        header_column, action_column = st.columns([6, 1])

        with header_column:
            st.header("Chat with GitHub using RAG")

        with action_column:
            if st.button("Clear", use_container_width=True):
                AppState.reset_chat()
                st.rerun()

    def render_chat_history(self) -> None:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def handle_chat_input(self) -> None:
        prompt = st.chat_input("Ask a question about the repository")

        if not prompt:
            return

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response = self.stream_response(prompt, response_placeholder)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

    def stream_response(self, prompt: str, response_placeholder: Any) -> str:
        github_url = st.session_state.github_url.strip()

        if not github_url:
            message = "Please load a GitHub repository first."
            response_placeholder.error(message)
            return message

        repository_key = AppState.repository_key(github_url)
        query_engine = st.session_state.repositories.get(repository_key)

        if query_engine is None:
            message = "Please load a GitHub repository first."
            response_placeholder.error(message)
            return message

        async def consume_stream() -> str:
            complete_response = ""

            try:
                async for chunk in self.streamer.stream(query_engine, prompt):
                    complete_response += chunk
                    response_placeholder.markdown(complete_response + "▌")

                response_placeholder.markdown(complete_response)
                return complete_response
            except Exception as error:
                message = f"An error occurred while generating the response: {error}"
                response_placeholder.error(message)
                return message

        return asyncio.run(consume_stream())