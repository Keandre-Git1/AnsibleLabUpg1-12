# Arkitekturmotivering & Systemdokumentation

**Författare:** Keandre Mendoza  
**Datum:** 2026-10-30  
**Kurs:** Automation med Ansible  

---

## 1. Systemöversikt & Verktygsval

Miljön består av en kontrollnod och tre Ubuntu 24.04-noder. nodekea1 kör Apache, nodekea2 kör en Flask-app i Gunicorn bakom Nginx och nodekea3 kör MariaDB. Allt sätts upp med en körning av `site.yml`.

### Val av verktyg

Vi valde Ansible för att vår miljö är liten och för att Ansible är agentless. Puppet och SaltStack använder oftast en master och en agent på varje nod. Puppets agent kollar noden var 30:e minut och rättar till det som har ändrats, och Salt är snabbt när man har många servrar. Det passar stora miljöer, men för tre noder är den extra infrastrukturen inte värd det. Ansible är också lättare att lära sig: playbooks skrivs i YAML och körs uppifrån och ned, medan Puppet har ett eget språk. Nackdelen är att Ansible inte rättar till ändringar på noderna av sig själv, utan bara när vi kör playbooken. Det är okej i en labbmiljö.

### Agentless vs. Agent-based

Ansible använder en push-modell. Vi kör playbooken från kontrollnoden, och Ansible ansluter till noderna med SSH och skickar ut ändringarna. Noderna behöver bara SSH och Python, som redan finns på Ubuntu. Vi slipper alltså installera och uppdatera en agent på varje nod, och det finns ingen masterserver som kan gå sönder. SSH används redan för administration, så inga nya portar behöver öppnas, och vi bestämmer själva när ändringar rullas ut.

### Mapp- och rollstruktur

- `site.yml` är huvudplaybooken. Varje play kopplar en roll till en grupp av servrar, och den sista playen skriver en rapport om varje nod.
- `roles/` har fyra roller som skapades med `ansible-galaxy role init`: `common` (användare och SSH-nyckel), `webserver` (Apache), `db` (MariaDB) och `flaskapp` (Nginx, Gunicorn och Flask).
- `group_vars/all/vault.yml` innehåller det krypterade databaslösenordet.
- `Scripts/script.py` är vårt dynamiska inventory.
- `templates/gatherindex.html.j2` är mallen för rapporten.

Uppdelningen gör projektet lättare att förvalta. Ska databasen ändras öppnar vi bara `roles/db`. Rollerna går också att återanvända: `common` körs på alla noder, och en ny webbserver behöver bara läggas i rätt grupp.

## 2. Säkerhet & Hemligheter (Secrets Management)

### Ansible Vault

Databaslösenordet ligger i `group_vars/all/vault.yml`, som är krypterad med Ansible Vault (AES256). I Git syns det bara som krypterad text. Rollerna använder variabeln `vault_db_passwd` i stället för att skriva lösenordet direkt. Vault-lösenordet ligger i `~/vault-secretpasswd.txt` på kontrollnoden, som `ansible.cfg` pekar på. Filen ligger utanför repot och står dessutom i `.gitignore`. Vi har inga API-nycklar, men de skulle skyddas på samma sätt. Databasanvändaren `admintest` får bara logga in från webbnodens IP, så ett läckt lösenord går inte att använda från en annan dator. En svaghet är att lösenordet ligger i klartext i `/opt/app.py` på webbnoden. Filen kan bara läsas av root och gruppen www-data. En förbättring vore `no_log: true` på de tasks som hanterar lösenordet, så att det inte kan synas med `--diff`.

### Behörighetshöjning & SSH

Vi loggar in med SSH-nycklar i stället för lösenord. `ansible.cfg` pekar på `~/.ssh/devops_admin`, och den privata nyckeln finns bara på kontrollnoden. Rollen `common` skapar systemanvändaren `devops_admin` på alla noder och lägger in den publika nyckeln i `authorized_keys`. Vi kör inte som root, utan loggar in som en vanlig användare och använder `become: true` för att få sudo. Vi kör med `-K`, så sudo-lösenordet skrivs in vid varje körning och sparas ingenstans. En förbättring vore att använda `become` bara på de tasks som kräver det, och att ge `devops_admin` sudo bara för de kommandon som behövs.

## 3. Skalbarhet & Dynamik

### Dynamiska vs. Statiska Inventories

Ett statiskt inventory är en fil där varje server skrivs in för hand. Vi använder ett dynamiskt inventory, `Scripts/script.py`, som skriver ut alla servrar och grupper som JSON när Ansible kör det. Grupperna bestämmer vilka roller en server får. Lägger vi till en server i gruppen `webservers` får den Apache nästa gång playbooken körs, utan att vi ändrar i playbooks eller roller. Just nu är serverlistan skriven direkt i skriptet. I en större miljö skulle skriptet hämta servrarna från ett API eller en molnleverantör, och då växer inventoryt av sig självt.

### Jinja2 & Variabelseparation

Vi använder Jinja2-mallar för filer som ska se olika ut på olika servrar. `index.html.j2` fyller i nodens namn, IP och operativsystem med Ansible facts, och `gatherindex.html.j2` bygger rapporten om varje nod. Lösenordet hålls utanför koden genom att ligga som variabel i `group_vars`. Tanken med att skilja kod från variabler är att rollerna ska vara likadana i Dev, Test och Produktion, och att bara variablerna ändras. Varje miljö får då egna `group_vars` och ett eget inventory, och samma `site.yml` körs mot alla. I vårt projekt är IP-adresserna till databasen och webbnoden fortfarande skrivna direkt i rollerna `db` och `flaskapp`. Nästa steg för att kunna köra samma kod i flera miljöer är att flytta dem till `group_vars`.

## 4. Drift, Optimering & Återhämtning

### Idempotens

Idempotens betyder att man kan köra samma playbook många gånger och få samma resultat. Är allt redan rätt ändras ingenting. Ansibles moduler beskriver hur det ska se ut, inte vad som ska göras: `apt` installerar bara paket som saknas och `service` startar bara tjänster som är stoppade. I databasrollen skapas tabellen med `CREATE TABLE IF NOT EXISTS` och testdatan läggs in med `INSERT IGNORE` och `UNIQUE`, så inget dubbleras. Idempotens gör det säkert att köra playbooken igen efter ett fel, och det är också vår återhämtning: har något ändrats på en nod återställer en ny körning rätt läge. Vid en andra körning visar ändå två saker `changed`. Rapporten skrivs om eftersom den innehåller live-värden som ledigt minne. Tabell-tasken räknas som ändrad av modulen, fast tabellen inte skapas på nytt.

### Felsökning & Verifiering

Före en körning kan vi göra en syntaxkontroll med `--syntax-check` och en torrkörning med `--check --diff`, som visar vad som skulle ändras utan att ändra något. Handlers gör att tjänster bara startas om när något har ändrats: MariaDB när bind-adressen ändras, Gunicorn när appen eller tjänstefilen ändras, Nginx laddas om när proxyn ändras och Apache startas om när startsidan ändras. Efter utrullningen verifierade vi i tre steg. `systemctl status` visar att gunicorn, nginx och mariadb körs. `curl http://10.6.69.83/` returnerar data från databasen, så hela kedjan Nginx → Gunicorn → Flask → MariaDB fungerar. Till sist lade vi in en ny rad direkt i databasen och såg att den syntes i svaret utan omstart (se README). En förbättring vore att lägga in hälsokontrollerna i en playbook, till exempel med modulen `uri`, så att de körs automatiskt.
