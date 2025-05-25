# Python virtual environment (if needed)
python3 -m venv .venv
source .venv/bin/activate

# Done
deactivate

pip install bottle #for REST API
pip install hypercorn # for handling http connection
pip install aioquic # for Http/3 connection
pip install python-dotenv # for shared secrets
pip install ldap3 # for ladp cennection

# For testing http/3 with self-signed certificate
curl -Lo http3_client.py \
  https://raw.githubusercontent.com/aiortc/aioquic/master/examples/http3_client.py

python3 http3_client.py https://127.0.0.1:8334/ -v --insecure

# Generate a quick self-signed certificate:
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -sha256 -days 365 -key ca-key.pem -out ca.pem
openssl genrsa -out privkey.pem 4096
openssl req -new -sha256 -subj "/CN=KSP" -key privkey.pem -out cert.csr
echo "subjectAltName=IP:192.168.7.101,IP:88.200.24.237,IP:2001:1470:fffd:99:20c:29ff:fec1:3126" >> extfile.cnf #IP needs to be configured correctly
openssl x509 -req -sha256 -days 365 -in cert.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf -CAcreateserial
cat cert.pem >> fullchain.pem
cat ca.pem >> fullchain.pem
sudo cp ca.pem /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates
# When you do that you need to upload ca.pem file to the browser

# http3 development:  

#LAPD server -> admin pass: beno
sudo apt install slapd ldap-utils
sudo dpkg-reconfigure slapd
# DNS domain name: ksp.si
# Organization name: ksp

# check for dc=ksp, dc=si
sudo grep -R olcSuffix /etc/ldap/slapd.d

#for encripted password => user name == password
userPassword: slappasswd -s pass

# cd to where the populate.ldif is
ldapadd -x -D "cn=admin,dc=ksp,dc=si" -W -f populate.ldif

# check if corectly inside
ldapsearch -x -LLL -H ldap:/// -b dc=ksp,dc=si '(objectClass=*)'

# check on witch port and ip is listening
sudo ss -tulnp | grep slapd

#Change the IP
sudo nano /etc/default/slapd

#Start server
sudo systemctl start slapd

#Stop the server
sudo systemctl stop slapd
sudo systemctl disable slapd


# Download cert -> install for database
sudo apt install -y python3-dev libpq-dev
pip install psycopg2
curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/44769303-8be5-4c0f-8c1c-13c2db0524ea/cert'


# How to run application (http/1.1, http/2, http/3)
hypercorn --config conf/hypercornAll.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1, http/2)
hypercorn --config conf/hypercornBase.toml   spletni_umesnik:asgi_app

# How to run application (http/1.1)
hypercorn --config conf/hypercornDep.toml   spletni_umesnik:app

