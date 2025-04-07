#!/usr/bin/env python3
if __name__ == "__main__":
    import sys
    import uvicorn
    import dotenv
    import pathlib

    args = sys.argv[1:] if sys.argv[0] == "python" else sys.argv
    if len(args) == 1:
        print("No argument supplied. Please specify 'prod' or 'dev'")
        exit(1)

    arg = args[1]
    if arg != "prod" and arg != "dev":
        print("Argument must be 'prod' or 'dev'")
        exit(1)
    if arg == "prod":
        file = pathlib.Path("./.env")
        if file.is_file():
            dotenv.load_dotenv(dotenv_path="./.env")
        uvicorn.run("buddy.src.main:app", reload=False)
    else:
        file = pathlib.Path("./development.env")
        if not file.is_file():
            print("Cannot find 'development.env' file")
            exit(1)
        dotenv.load_dotenv(dotenv_path="./development.env")
        uvicorn.run("buddy.src.main:app", reload=True)



