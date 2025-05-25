sudo apt install -y python3-dev libpq-dev
pip install psycopg2
curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/44769303-8be5-4c0f-8c1c-13c2db0524ea/cert'