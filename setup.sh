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

# Generate a quick self-signed certificate:
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -sha256 -days 365 -key ca-key.pem -out ca.pem
openssl genrsa -out privkey.pem 4096
openssl req -new -sha256 -subj "/CN=KSP" -key privkey.pem -out cert.csr
echo "subjectAltName=IP:127.0.0.1" >> extfile.cnf #IP needs to be configured correctly
openssl x509 -req -sha256 -days 365 -in cert.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf -CAcreateserial
cat cert.pem > fullchain.pem
cat ca.pem > fullchain.pem
sudo cp ca.pem /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates
# When you do that you need to upload ca.pem file to the browser

# http3 development: https://github.com/kelmenhorst/quic-censorship/blob/main/browsers.md

# How to run application (http/1.1, http/2, http/3)
hypercorn --config conf/hypercornAll.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1, http/2)
hypercorn --config conf/hypercornBase.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1)
hypercorn --config conf/hypercornDep.toml   spletni_umesnik:app

