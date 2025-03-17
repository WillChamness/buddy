"""
Run this file to run the debugger
"""
import os
import uvicorn

with open("development.env", "r") as f:
    lines = f.readlines()

for line in lines:
    key, val = line.split("=")[0].strip(), line.split("=")[1].strip().replace('"', '')
    print(f"{key}: {val}")
    os.environ[key] = val

from buddy.src.main import app
uvicorn.run(app)

