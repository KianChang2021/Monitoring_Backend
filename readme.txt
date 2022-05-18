Server serve for main 
waitress-serve --port=8084 main:app

Server serve for monitoring_service
waitress-serve --port=8085 Monitoring_api:app

python version 3.8.6

Pip install (direct opy and paste in terminal can ady)
=====================
pip install pyodbc
pip install schedule
pip install requests
pip install flask
pip install psutil

