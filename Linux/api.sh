#!/bin/bash
cd ../fastapi/ && uvicorn main:app --reload --host $1 --port 8000
