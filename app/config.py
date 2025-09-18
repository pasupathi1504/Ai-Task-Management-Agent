import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://ai_tasks:ai_tasks_pw@localhost:5432/ai_tasks",
)
