
---

## 1. REST storitev na Bottle + Hypercorn + CockroachDB + LDAP  
Ta dokument opisuje arhitekturo in ključne komponente REST storitve, ki temelji na Python-skem mikrostrežniškem ogrodju **Bottle**, poganja jo **Hypercorn** kot ASGI/WSGI strežnik, za shranjevanje podatkov uporablja **CockroachDB** (porazdeljena podatkovna baza s konsenzusom RAFT) in izvaja avtorizacijo prek **LDAP**.

---

### 1.1 Komponente sistema

| Komponenta    | Namen                                                                                      |
|---------------|--------------------------------------------------------------------------------------------|
| **Bottle**    | Framework za definiranje HTTP rout in handlerjev.                                          |
| **Hypercorn** | ASGI/WSGI strežnik (HTTP/1.1, HTTP/2, HTTP/3) z vmesnikom za asinhrono obdelavo zahtev.    |
| **CockroachDB** | Porazdeljena SQL baza, uporablja RAFT konsenzusni algoritem za replikacijo in fault-tolerance. |
| **LDAP**      | Centralni imenik uporabnikov, loči naročnike (subscribers) od nenaročnikov.                |


### 1.2 CockroachDB kot porazdeljena baza  
- **Porazdeljenost**: podatki razpršeni čez več nodov (na večih strežnikih), vsaka tabela je razdeljena na range-je.  
- **RAFT**: konsenzusni algoritem, ki zagotavlja, da ima vsak range več replika-leaderjev in followerjev; pri pisnih operacijah se doseže konsenz med nodi, kar zagotavlja odpornost na padce in konsistentnost (CP v CAP).  
- **Prednosti**: horizontalna skalabilnost, avtomatska replikacija in samodejno premeščanje podatkov, visoka razpoložljivost in trajnost.  

---

### 1.3 Povezava na LDAP  
- **Cilj**: centralizacija avtentikacije in avtorizacije  
- **Skupine**:  
  - `subscribers` → dostop do osnovnih + dodatnih endpointov (npr. `/history`)  
  - `non-subscribers` → samo osnovni endpointi (npr. `/data`)  
- **Proces**: ob prijavi (`/login`) se preveri uporabniško ime/geslo v LDAP; ob uspehu se v JWT shranijo atributi (npr. `role: subscriber`)

## 1.4 Povzetek LDAP uporabnikov

| UID   | CN   | SN      | Email             | Skupina          | DN                                      |
|-------|------|---------|-------------------|------------------|-----------------------------------------|
| beno  | Beno | Batina  | beno@beno.com     | subscribers      | `uid=beno,ou=People,dc=ksp,dc=si`       |
| jano  | Jano | Gracler | jano@jano.com     | non-subscribers  | `uid=jano,ou=People,dc=ksp,dc=si`       |


---

### 1.5 IP naslovi

| Vrsta       | Naslovi                                                                                        |
|-------------|------------------------------------------------------------------------------------------------|
| **bind**          | – `192.168.7.101:4333` <br> – `[2001:1470:fffd:99:20c:29ff:fec1:3126]:4333`               |
| **quic_bind**     | – `192.168.7.101:4433` <br> – `[2001:1470:fffd:99:20c:29ff:fec1:3126]:4433`               |
| **insecure_bind** | – `192.168.7.101:8080` <br> – `[2001:1470:fffd:99:20c:29ff:fec1:3126]:8080`               |

Dodatne TLS nastavitve:

```toml
certfile = "certs/fullchain.pem"
keyfile  = "certs/privkey.pem"

use_reloader      = true
loglevel          = "debug"
accesslog         = "/dev/stdout"
errorlog          = "/dev/stdout"
access_log_format = "%(h)s \"%(r)s\" %(H)s → %(s)s %(b)s bytes in %(D)sµs"

```
### 1.6 Povzetek uporabljenih piškotkov

| Ime piškotka          | Namen                                                         | Vsebina                                    | Pot (`Path`) | Signed (secret) | Secure | HttpOnly |
|-----------------------|---------------------------------------------------------------|--------------------------------------------|--------------|-----------------|--------|----------|
| `uporabnik`           | Identifikacija prijavljenega uporabnika in prikaz imena v UI  | Besedilna vrednost: `cn + " " + sn`        | `/`          | Da              | Ne¹    | Ne¹      |
| `narocnik`            | Seznam LDAP skupin (subscribers/non-subscribers) za avtorizacijo | JSON niz, npr. `["subscribers"]` ali `["non-subscribers"]` | `/`          | Da              | Ne¹    | Ne¹      |
| `id_igre` (konstanta `ID_IGRE_COKOLADNI_PISKOT`) | Shranjevanje tekočega ID igre (KSP ali KSPOV)          | Številčna vrednost (ID igre) kot niz       | `/`          | Da              | Ne¹    | Ne¹      |



### 1.7 Povzetek REST storitev

| Endpoint               | Metode          | Namen                                                  | Avtorizacija             |
|------------------------|-----------------|--------------------------------------------------------|--------------------------|
| `/`                    | GET, HEAD       | Prikaz prijavne strani (`views/log.tpl`), param `?valid=0` za napako prijave | javno                   |
| `/end/`                | GET, HEAD       | Prikaz glavnega menija (`views/zacetni_menu.tpl`)      | cookie `uporabnik`       |
| `/zacetni_menu/`       | PUT, HEAD       | Obdelava prijave; nastavitev piškotkov in preusmeritev na `/end/` | javno                   |
| `/nova_igra_ksp/`      | GET, HEAD       | Ustvari novo “čokoladni piskot” igro (ksp), nastavi cookie `id_igre` | cookie `uporabnik`       |
| `/ksp/`                | GET, HEAD       | Prikaz ali ostvaritev poteze v igri KSP (`views/ksp.tpl`) | cookie `uporabnik`       |
| `/ksp/`                | POST, HEAD      | Izbira orožja in posodobitev stanja igre               | cookie `uporabnik`       |
| `/zgodovina_ksp/`      | GET, HEAD       | Prikaz zgodovine (HTML) (`views/zgodovina_ksp.tpl`)     | samo za `subscribers`    |
| `/brisi_ksp/`          | DELETE, HEAD    | Pobriše zgodovino iger KSP                              | samo za `subscribers`    |
| `/zgodovina_ksp/json/` | GET, HEAD       | Vrne zgodovino KSP v JSON formatu                      | samo za `subscribers`    |
| `/zgodovina_ksp/xml/`  | GET, HEAD       | Vrne zgodovino KSP v XML formatu                       | samo za `subscribers`    |

---

| Endpoint                     | Metode          | Namen                                                   | Avtorizacija             |
|------------------------------|-----------------|---------------------------------------------------------|--------------------------|
| `/nova_igra_kspov/`          | GET, HEAD       | Ustvari novo igro KSPOV, nastavi cookie `id_igre`       | cookie `uporabnik`       |
| `/kspov/`                    | GET, HEAD       | Prikaz ali poteza v igri KSPOV (`views/kspov.tpl`)       | cookie `uporabnik`       |
| `/kspov/`                    | POST, HEAD      | Izbira orožja in posodobitev stanja igre KSPOV          | cookie `uporabnik`       |
| `/zgodovina_kspov/`          | GET, HEAD       | Prikaz zgodovine KSPOV (HTML) (`views/zgodovina_kspov.tpl`) | samo za `subscribers`    |
| `/brisi_kspov/`              | DELETE, HEAD    | Pobriše zgodovino iger KSPOV                            | samo za `subscribers`    |
| `/zgodovina_kspov/json/`     | GET, HEAD       | JSON zgodovina KSPOV                                    | samo za `subscribers`    |
| `/zgodovina_kspov/xml/`      | GET, HEAD       | XML zgodovina KSPOV                                     | samo za `subscribers`    |

# Povzetek Prometheus + Grafana rešitve

1. **Node Exporter**  
   - Agent, nameščen na Linux gostitelju (npr. `127.0.0.1:9100`).  
   - Izvaja zbiranje strojnih metrik (CPU, pomnilnik, disk, omrežje, uptime…).

2. **Prometheus**  
   - Periodično “scrape-a” metrike iz Node Exporterja.  
   - Shrani jih kot časovne vrste v svojo bazo.  
   - Omogoča poizvedovanje (PromQL) in definiranje alarmov.

3. **Grafana**  
   - Priklopljena na Prometheus kot data-source.  
   - Izrisuje niz vizualnih panelov (gauge, grafi, tabelarični prikazi):  
     - **Quick CPU / Mem / Disk** (trenutni odstotki obremenitev).  
     - **Basic CPU / Mem / Net / Disk** (časovne serije zadnjih 24 ur).  
     - **Network Traffic** (hitrost recv/trans po vmesnikih).  
     - **Disk Space Used** (zasedenost particij).  
     - Razširjeni sklopi: procesi, systemd, časovne sinhronizacije, …  
   - Interaktivno nastavljanje obdobja, osveževanja, filtriranja po job/host.

4. **Prednosti**  
   - Centralizirano zbiranje in arhiviranje metrik.  
   - Prilagodljivi dashboardi in vizualizacije.  
   - Enostavno alarmiranje in notifikacije (e-pošta, Slack, PagerDuty…).  
   - Skalabilno in visoko zmogljivo za več gostiteljev hkrati.

