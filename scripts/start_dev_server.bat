@echo off
set DEBUG=True
cd /d E:\Projects\pyloomweb
"C:\Program Files\Python312\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
