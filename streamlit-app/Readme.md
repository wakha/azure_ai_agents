### Create venv and install libraries

```ps
python -m -venv .venv

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

.venv/Scripts/activate

pip install -r requirements.txt
```

### Run streamlit 

```ps
streamlit run streamlit-freshdesk.py
```
