# build_files.sh
apt get install -y postgresql postgresql-contrib libpq-dev
pip install -r requirements.txt
python3 manage.py collectstatic