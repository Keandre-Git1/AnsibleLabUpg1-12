#!/usr/bin/env python3
"""Dynamiskt Ansible-inventory (Lab 9).

Ansible anropar skriptet på två sätt:
  inventory.py --list        -> hela inventoryt som JSON
  inventory.py --host <namn> -> variabler för en host (vi returnerar {})
"""
import argparse
import json

# "Källan" till servrarna. I ett riktigt scenario hämtas detta från ett
# API, en databas eller en molnleverantör i stället för att vara hårdkodat.
# En server kan ligga i flera grupper (groups är en lista).
SERVERS = [
    {"name": "nodekea1.local", "user": "nodekea1", "groups": ["webservers", "nodes"]},
    {"name": "nodekea3.local", "user": "nodekea3", "groups": ["nodes", "dbservers"]},
    {"name": "nodekea2.local", "user": "nodekea2", "groups": ["flaskwebserver", "nodes"]},
]


def build_inventory():
    hostvars = {}
    groups = {}
    for s in SERVERS:
        hostvars[s["name"]] = {
            "ansible_host": s["name"],
            "ansible_user": s["user"],
        }
        for g in s["groups"]:
            groups.setdefault(g, {"hosts": []})["hosts"].append(s["name"])

    inventory = {"_meta": {"hostvars": hostvars}}
    inventory.update(groups)
    inventory["all"] = {"children": list(groups)}
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--host")
    args = parser.parse_args()

    if args.host:
        print(json.dumps({}))  # allt finns redan i _meta
    else:
        print(json.dumps(build_inventory(), indent=2))


if __name__ == "__main__":
    main()
