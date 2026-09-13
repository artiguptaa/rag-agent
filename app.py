from streamlit_app import GitHubRAGApp
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    GitHubRAGApp().run()