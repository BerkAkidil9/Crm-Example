# Django CRM Project Startup Guide

## Required Commands to Start the Project from Scratch

### 1. Open Terminal/PowerShell and go to the project folder:
```powershell
cd "C:\Users\berka\Desktop\GITHUB REPOSITORıES\env"
```

### 2. Start the Django server:
```powershell
.\new_env\Scripts\python.exe manage.py runserver
```

### 3. Go to the following address in your browser:
```
http://127.0.0.1:8000/
```

## Alternative Commands (If the above does not work):

### If Python module is not found:
```powershell
# First install the required packages
.\new_env\Scripts\python.exe -m pip install -r requirements.txt

# Then start the server
.\new_env\Scripts\python.exe manage.py runserver
```

### If the port is in use:
```powershell
# Stop running Python processes
taskkill /f /im python.exe

# Then start the server
.\new_env\Scripts\python.exe manage.py runserver
```

## Start with Single Command (Recommended):
```powershell
cd "C:\Users\berka\Desktop\GITHUB REPOSITORıES\env" && .\new_env\Scripts\python.exe manage.py runserver
```

## Note:
- To stop the server, press `Ctrl+C` in the terminal
- The project will run at http://127.0.0.1:8000/
- If you get an error, run `taskkill /f /im python.exe` first
