import os
from typing import Any

import streamlit as st
from llama_index.core import PromptTemplate, Settings, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq


class RAGEngineFactory:
    """Create and configure LlamaIndex query engines."""

    PROMPT = PromptTemplate(
        """
Context information is below.
---------------------
{context_str}
---------------------

Answer the query using only the context above.

Be precise and concise. If the answer cannot be found in the context,
respond with: "I don't know."

Query: {query_str}

Answer:
"""
    )

    @staticmethod
    @st.cache_resource
    def get_llm() -> Groq:
        api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "Set GROQ_API_KEY or OPENAI_API_KEY before loading a repository."
            )

        return Groq(
            api_key=api_key,
            model="openai/gpt-oss-20b",
            # model="llama-3.1-70b-versatile",
        )

    @staticmethod
    @st.cache_resource
    def get_embedding_model() -> HuggingFaceEmbedding:
        return HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5",
            trust_remote_code=True,
        )

    def build(self, documents: list[Any]) -> Any:
        Settings.llm = self.get_llm()
        Settings.embed_model = self.get_embedding_model()

        index = VectorStoreIndex.from_documents(
            documents=documents,
            transformations=[MarkdownNodeParser()],
            show_progress=True,
        )

        query_engine = index.as_query_engine(streaming=True)
        query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": self.PROMPT}
        )

        return query_engine