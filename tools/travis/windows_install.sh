choco install python3 --pre 
export PATH="/c/Python38:/c/Python38/Scripts:$PATH"

# create new empty venv
which python
python -m venv ~/venv
ls -ltr ~/venv
ls -ltr ~/venv/Scripts
source ~/venv/Scripts/activate
