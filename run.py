"""
Run this file to run the debugger
"""
import uvicorn
import dotenv

dotenv.load_dotenv(dotenv_path="./development.env")

from buddy.src.main import app
uvicorn.run(app)

