# build_files.sh
sudo apt-get install -y postgresql postgresql-contrib libpq-dev
pip install -r requirements.txt
python3.9 manage.py collectstatic