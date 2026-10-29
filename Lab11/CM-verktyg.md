# Ansible vs Puppet

## Arkitektur

### Ansible (Push)
- Processen startas från en **central kontrollnod** som ansluter till målnoderna via **SSH** (Linux) eller **WinRM** (Windows).
- Varje task skickas som en **modul** (Python på Linux, PowerShell på Windows) till noden, körs där och **raderas sedan**.
- Ingen agent behövs på målnoderna.

### Puppet (Pull)
- En **lokal agent** på målnoden kontaktar regelbundet (standard: var 30:e minut) en central **Puppet Server** via **HTTPS** (port 8140).
- Servern **kompilerar koden till en katalog** (en ritning över önskat tillstånd).
- Agenten **hämtar hem (pullar)** katalogen och verkställer den **deklarativt** lokalt.

## Exekveringsordning

### Ansible
- Tasks körs **uppifrån och ned, i exakt den ordning du skrivit dem**.
- Ansible kontrollerar **inte** i förväg om ordningen är logisk. Om ett steg beror på något som inte finns än, **misslyckas det när det körs**.
- Exempel: skapa **först databasen**, sedan användaren och dess rättigheter.

### Puppet
- Koden beskriver **önskat tillstånd**, inte en sekvens av steg.
- Resurser utan uttryckliga beroenden körs i den ordning de står i manifestet (standard sedan Puppet 3.3).
- Beroenden måste ändå **anges uttryckligen** med `require`, `before`, `notify` eller `->`. Undantaget är vissa inbyggda *autorequires*, till exempel att en fil kräver sin föräldrakatalog.
- Puppet bygger en beroendegraf och **avbryter vid cirkulära beroenden**.



## Jämförelsetabell där du listar Arkitektur, Språk/Syntax, Fördelar/Nackdelar

| Egenskap | Ansible (Push) | Puppet (Pull) |
| :--- | :--- | :--- |
| **Arkitektur** | **Agentlös.** Kontrollnoden pushar tillfälliga Python-skript via SSH/WinRM direkt till målnoderna. | **Agentbaserad.** En lokal agent på målnoden pullar en kompilerad ritning (katalog) via HTTPS. |
| **Språk / Syntax** | **YAML.** Koden körs **sekventiellt** (rad för rad). Du måste skriva allt i logisk ordning (t.ex. skapa databas *innan* användare). | **Puppet DSL** (Ruby-baserat). Koden är **strikt deklarativ**. Puppet räknar själv ut rätt ordning via beroendegrafer. |
| **Fördelar** | • Extremt snabb att komma igång med.<br>• Ingen programvara krävs på målnoderna.<br>• Enkel YAML-syntax. | • Skalar mycket bra i enorma miljöer.<br>• Driftsäker (agenten rättar automatiskt till avvikelser var 30:e minut). |
| **Nackdelar** | • Kan bli långsammare vid tusentals samtidiga SSH-anslutningar.<br>• Kräver öppna SSH/WinRM-portar in på målnoderna. | • Hög tröskel att lära sig eget kodspråk (DSL).<br>• Kräver installation och hantering av agenter och SSL-certifikat. |

