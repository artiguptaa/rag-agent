import tempfile
from pathlib import Path
from typing import Any

from gitingest import ingest
from llama_index.core import SimpleDirectoryReader


class GitHubRepositoryService:
    """Download and prepare GitHub repository content."""

    CONTENT_FILE = "content.md"

    def ingest_repository(self, github_url: str) -> str:
        _, _, content = ingest(github_url)

        Path(self.CONTENT_FILE).write_text(
            content,
            encoding="utf-8",
        )

        return content

    def load_documents(self, content: str) -> list[Any]:
        with tempfile.TemporaryDirectory() as temp_dir:
            content_path = Path(temp_dir) / "repository_content.md"
            content_path.write_text(content, encoding="utf-8")

            reader = SimpleDirectoryReader(input_dir=temp_dir)
            return reader.load_data()