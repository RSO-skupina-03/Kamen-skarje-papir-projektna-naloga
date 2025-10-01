
# Rock Paper Scissors Web Application and Command Line Application

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Project overview
This project contains a web and command line application for the game [Rock Paper Scissors](https://en.wikipedia.org/wiki/Rock_paper_scissors#/media/File:Rock-paper-scissors.svg) and the game [Rock Paper Scissors Water Fire](https://en.wikipedia.org/wiki/Rock_paper_scissors#/media/File:Rpsfw_game.svg). It runs on Linux. The web application supports HTTP/1.1, HTTP/2, and HTTP/3, and user information is stored on an LDAP server. The Rock Paper Scissors game is played for 7 rounds and the Rock Paper Scissors Water Fire game is played for 15 rounds.

**Tech stack:**
- Frontend: HTML, CSS and JavaScript
- Backend: Bottle (WSGI), Hypercorn (ASGI/WSGI server)
- Database: CockroachDB (postgreSQL)
---
## Project stucture
```
.
├─ Kamen-skarje-papir-projektna-naloga/
│  ├─ certs/                  # Self-signed certificates for HTTP/2, HTTP/3
│  ├─ conf/                   # Configuration files for Hypercorn           
│  ├─ datoteke/               # Json files for application data
│  ├─ static/                 # Frontend scripts                  
|  |  ├─ script.js
|  |  └─ style.css      
│  ├─ views/                  # Diffrent HTML pages
|  ├─ .env                    # Environment variables
|  ├─ model.py                # Logic for game
|  ├─ spletni_umesnik.py      # REST services, web interface
|  ├─ tekstovni_umesnik.py    # Logic for command line interface
|  └─ populate.ldif           # Example of LDAP users
```

---

## Installation & Build
Before running the web application, you need to install the required Python libraries and set up the LDAP server. An example of users for the LDAP server is provided in the `populate.ldif` file, where passwords are stored as hash values (username == password).
```bash
# Required Python libraries for the web application
python3 -m venv .venv
source .venv/bin/activate
sudo apt install -y python3-dev libpq-dev
pip install psycopg2 bottle hypercorn aioquic python-dotenv ldap3

# LDAP server setup
sudo apt install slapd ldap-utils
sudo dpkg-reconfigure slapd

#for encripted password
userPassword: slappasswd -s pass
ldapadd -x -D "cn=admin,dc=ksp,dc=si" -W -f populate.ldif

#Start LDAP server
sudo systemctl start slapd

#Stop LDAP server
sudo systemctl stop slapd
```

Certificates are self-signed and created with OpenSSL. Feel free to use any other certificates, but you need to place them in the `conf` folder.  

If you want to recreate self-signed certificates, below is the script I used to generate my certificate:

```bash
# Generate self-signed certificate
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -sha256 -days 365 -key ca-key.pem -out ca.pem
openssl genrsa -out privkey.pem 4096
openssl req -new -sha256 -subj "/CN=KSP" -key privkey.pem -out cert.csr
echo "subjectAltName=IP:127.0.0.1" >> extfile.cnf #IP configuration
openssl x509 -req -sha256 -days 365 -in cert.csr -CA ca.pem -CAkey ca-key.pem -out cert.pem -extfile extfile.cnf -CAcreateserial
cat cert.pem >> fullchain.pem
cat ca.pem >> fullchain.pem
sudo cp ca.pem /usr/local/share/ca-certificates/ca.crt
sudo update-ca-certificates

# After you create certificate, you need to upload the ca.pem file to the browser
```

---
## Running Application
The web application can be run in three different configurations:

- `hypercornAll.toml`: HTTP/1.1, HTTP/2, HTTP/3  
- `hypercornBase.toml`: HTTP/2  
- `hypercornDep.toml`: HTTP/1.1  

The following table represents the ports on which the web application is listening.  
Currently, the IP address is set to localhost (`127.0.0.1`).  

| Protocol     | Port |
|:------------:|:----:|
| **HTTP/1.1** | 8080 |
| **HTTP/2**   | 4333 |
| **HTTP/3**   | 4433 |

```bash
# How to run application for HTTP/1.1, HTTP/2 and HTTP/3
hypercorn --config conf/hypercornAll.toml   spletni_umesnik:asgi_app

# How to run application for HTTP/2
hypercorn --config conf/hypercornBase.toml   spletni_umesnik:asgi_app

# How to run application for HTTP/1.1
hypercorn --config conf/hypercornDep.toml   spletni_umesnik:app

# How to run application for command line
python tekstovni_umesnik.py
```

---