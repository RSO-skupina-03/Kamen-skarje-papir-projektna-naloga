# Python virtual environment (if needed)
python3 -m venv .venv
source .venv/bin/activate

# Done
deactivate

pip install bottle #for REST API
pip install hypercorn # for handling http connection
pip install aioquic # for Http/3 connection
pip install python-dotenv # for shared secrets

# For testing http/3 with self-signed certificate
curl -Lo http3_client.py \
  https://raw.githubusercontent.com/aiortc/aioquic/master/examples/http3_client.py

python3 http3_client.py https://127.0.0.1:8334/ -v --insecure

# Generate a quick self-signed certificate (for testing only):
openssl req -x509 -nodes -newkey rsa:4096 \
  -keyout certs/privkey.pem \
  -out certs/fullchain.pem \
  -days 365 \
  -config certs/v3.ext

# How to run application (http/1.1, http/2, http/3)
hypercorn --config conf/hypercornAll.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1, http/2)
hypercorn --config conf/hypercornBase.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1)
hypercorn --config conf/hypercornDep.toml   spletni_umesnik:app

