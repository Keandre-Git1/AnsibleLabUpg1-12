# Configuration Management med Ansible – 12 laborationer

Det här repot innehåller alla laborationer i kursen. Varje labb ligger i en egen mapp. Slutprojektet, med alla moment samlade och arkitekturmotiveringen, ligger i **[Lab12](Lab12/)**.

## Miljö

| Nod | Roll |
|---|---|
| adminkea | Kontrollnod med Ansible |
| nodekea1.local | Webbserver (Apache) |
| nodekea2.local | Flask-app med Gunicorn och Nginx |
| nodekea3.local | Databasserver (MariaDB) |

Alla noder kör Ubuntu 24.04. Namnen slås upp med mDNS (avahi).

## Laborationer

| Labb | Innehåll | Redovisning |
|---|---|---|
| [Lab1](Lab1/) | Miljöuppsättning och lösenordsfri SSH | `Screenshotlabb1.png` |
| [Lab2](Lab2/) | Ad-hoc-kommandon | `lab2kommando.txt` |
| [Lab3](Lab3/) | Första playbooken och idempotens | `sakerstallweb.yaml`, `lab3kommando.txt` |
| [Lab4](Lab4/) | Användar- och behörighetshantering | `users.yml`, `Bevisfördevopsadmin.png` |
| [Lab5](Lab5/) | Roller med ansible-galaxy (VG) | [README](Lab5/README.md) |
| [Lab6](Lab6/) | Jinja2-mallar | `index.html.j2`, skärmdumpar |
| [Lab7](Lab7/) | Ansible Vault (VG) | [README](Lab7/README.md) |
| [Lab8](Lab8/) | CMDB och Configuration Items (VG) | [README](Lab8/README.md) |
| [Lab9](Lab9/) | Dynamiskt inventory | `Scripts/script.py`, skärmdumpar |
| [Lab10](Lab10/) | Flerskiktsapplikation (VG) | [README](Lab10/README.md) |
| [Lab11](Lab11/) | Jämförelse Ansible och Puppet | `CM-verktyg.md` |
| [Lab12](Lab12/) | Slutprojekt och arkitekturmotivering | [README](Lab12/README.md), [ARCHITECTURE.md](Lab12/ARCHITECTURE.md) |


## Köra de tidigare labbarna

Varje labb körs från sin egen mapp. Labb 3–8 använder en statisk `inventory.ini`, och från Lab 9 används det dynamiska inventoryt `Scripts/script.py`.

| Labb | Kommando (körs i labbens mapp) |
|---|---|
| Lab2 | Ad-hoc-kommandona finns i `lab2kommando.txt` |
| Lab3 | `ansible-playbook -i inventory.ini sakerstallweb.yaml -K` |
| Lab4 | `ansible-playbook -i ../Lab3/inventory.ini users.yml -K` |
| Lab5 | `ansible-playbook -i inventory.ini site.yml -K` |
| Lab6 | Ingen egen playbook – mallen körs av webserver-rollen i Lab7 (se Lab7-raden) |
| Lab7 | `ansible-playbook -i inventory.ini site.yml -K` |
| Lab8 | `ansible-playbook -i inventory.ini site.yml -K` |
| Lab9 | `ansible-inventory -i Scripts/script.py --list` och `ansible -i Scripts/script.py all -m ping` |
| Lab10 | `ansible-playbook -i Scripts/script.py site.yml -K` |
| Lab12 | `ansible-playbook -i Scripts/script.py site.yml -K` |

Lab 7, 8, 10 och 12 läser vault-lösenordet från `~/vault-secretpasswd.txt` (se `ansible.cfg` i respektive mapp).

## Köra slutprojektet

```bash
cd Lab12
ansible-galaxy collection install -r requirements.yml
chmod +x Scripts/script.py
ansible-playbook -i Scripts/script.py site.yml -K
```

Vault-lösenordet ska ligga i `~/vault-secretpasswd.txt` på kontrollnoden, utanför repot. Mer om körning och verifiering finns i [Lab12/README.md](Lab12/README.md).

## Säkerhet

- Databaslösenordet är krypterat med Ansible Vault (`group_vars/all/vault.yml`).
- Vault-lösenordet och SSH-nycklarna finns bara på kontrollnoden och ligger aldrig i Git.
- `.gitignore` utesluter `.vault_pass`, loggar, `.retry`-filer och genererade rapporter.