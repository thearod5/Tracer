python3 -m venv env
env/bin/python3 -m pip install --upgrade pip
env/bin/pip3 install -r requirements.txt
mkdir -p "cache/.test"
rm -f .env && echo "PATH_TO_ROOT=\"$PWD\"" >>.env && echo "PATH_TO_DATASETS=\"\"" >>.env
