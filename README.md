# Steps to run the backend

## Step 1 
Create a virtual environment with Python 3.10 and activate the environment
```
py -3.10 -m venv venv310
venv310\Scripts\activate
```
## Step 2
Install the dependencies with this command
```
pip install -r requirements.txt
```
## Step 3
If you run the backend the first time, you need to run this command to create the database
```
python -m scripts.ingest_database
```
## Step 4
To run the backend just put this command
```
python -m app.main
```

# To Run with NGROK
Open a new terminal, in cmd
```
cd C:\Users\darkandy\Downloads\NGROK
ngrok http 8000
```
Open a new terminal in powershell
```
cd C:\Users\darkandy\Downloads\NGROK
.\ngrok http 8000
```

# To screencast the phone with scrcpy

```
open_a_terminal_here
scrcpy --no-audio
```