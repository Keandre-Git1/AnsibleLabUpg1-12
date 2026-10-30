# Lab 8: Hantering av CMDB och Configuration Items (VG)

Den sista playen i `site.yml` samlar in fakta från alla noder och skriver en rapport i Markdown för varje server. Rapporten fungerar som en Configuration Item (CI) i en CMDB.

## Så fungerar det

1. `gather_facts: true` hämtar Ansible facts från noderna: hostname, CPU, RAM, OS, IP-adresser, upptid och diskar.
2. `ansible.builtin.package_facts` hämtar listan över installerade paket.
3. `ansible.builtin.template` fyller i mallen `templates/gatherindex.html.j2` och sparar rapporten på kontrollnoden (`delegate_to: localhost`).

```bash
ansible-playbook -i inventory.ini site.yml -K
```

## Rapporter

| Server | Roll | Rapport |
|---|---|---|
| nodekea1 (10.6.69.85) | Webbserver (Apache) | [nodekea1_inventory_report.md](nodekea1_inventory_report.md) |
| nodekea3 (10.6.69.102) | Databasserver (MariaDB) | [nodekea3_inventory_report.md](nodekea3_inventory_report.md) |

## G- och VG-krav

| Krav | Var |
|---|---|
| CI:er: hostname, CPU, RAM (totalt och ledigt), OS-version | Överst i varje rapport |
| Playbook som samlar in fakta och skriver en rapport per server | Sista playen i `site.yml` |
| **VG:** relationer mellan servrarna | Avsnittet *Relationer* nedan |
| **VG:** alla IP-adresser, Hyper-V, installerade paket, hårddiskinfo och upptid | Avsnittet *VG-Nivå* i varje rapport |

## Relationer mellan servrarna (VG)

Ett beroende betyder att en server behöver en annan för att fungera. Pilen visar vem som pratar med vem.

```
adminkea (kontrollnod) ──SSH/Ansible──► nodekea1 (Apache)
                       ──SSH/Ansible──► nodekea3 (MariaDB)
```

| Från | Till | Hur | Varför |
|---|---|---|---|
| adminkea | nodekea1 | SSH, port 22 | Ansible konfigurerar webbservern |
| adminkea | nodekea3 | SSH, port 22 | Ansible konfigurerar databasservern |
| adminkea | nodekea1/nodekea3 | mDNS (avahi) | Namnen `nodekea1.local` och `nodekea3.local` slås upp med mDNS |

I den här labben finns inget beroende mellan webbservern och databasen. Apache visar en statisk sida, och databasanvändaren `admintest` får bara logga in från `localhost`. I Lab 10 tillkommer beroendet webbnod → databasnod (`nodekea2 → nodekea3:3306`).

### Impact analysis: vad händer om en server går ner?

| Om den här går ner | Påverkas | Konsekvens |
|---|---|---|
| adminkea | Ingen tjänst | Webbsidan och databasen fortsätter fungera, men vi kan inte köra Ansible eller uppdatera konfigurationen |
| nodekea1 | Bara webbsidan | Startsidan på nodekea1 går inte att nå. Databasen påverkas inte |
| nodekea3 | Bara databasen | `varandb` går inte att nå. Webbsidan påverkas inte, eftersom den inte använder databasen |
| mDNS (avahi) på en nod | Ansible mot den noden | `.local`-namnet går inte att slå upp, så Ansible når inte noden. Tjänsterna på noden fortsätter fungera |

## Koppling till en CMDB

En CMDB (Configuration Management Database) är en databas över alla Configuration Items i en miljö och hur de hänger ihop. Varje rapport här motsvarar en CI-post: servern är CI:n, och fälten (CPU, RAM, OS, IP, paket, diskar) är dess attribut. Tabellen *Relationer* motsvarar CMDB:ns kopplingar mellan CI:er, och den används för impact analysis, alltså att se vad som påverkas om något går sönder.

Eftersom rapporterna skapas av en playbook kan de köras om när som helst och visar då alltid aktuellt läge. I en riktig miljö skulle samma playbook skicka datan som JSON till en CMDB via dess API i stället för att skriva Markdown-filer.
