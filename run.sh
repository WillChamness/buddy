#!/bin/bash

if [ -z "$1" ]; then
   echo "No argument supplied. Please specify 'dev' or 'prod'."
   exit 1
fi

if [ "$1" != "dev" ] && [ "$1" != "prod" ]; then
   echo "Argument must be 'dev' or 'prod'"
   exit 1
fi

if [ "$1" = "dev" ]; then
   if [ ! -f development.env ]; then
      echo "Cannot find development.env file"
      exit 1
   fi
   export $(cat development.env | xargs)
   uvicorn buddy.src.main:app --reload
else
   if [ ! -f .env ]; then
      echo "Cannot find .env file"
      exit 1
   fi
   export $(cat .env | xargs)
   uvicorn buddy.src.main:app
fi

