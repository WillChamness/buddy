"""
Run dev
"""
if __name__ == "__main__":
    import uvicorn
    import dotenv
    dotenv.load_dotenv(dotenv_path="./development.env")
    uvicorn.run("buddy.src.main:app", reload=True)

