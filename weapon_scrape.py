from io import StringIO
import re
import sys
import certifi
import pandas as pd
import requests
from bs4 import BeautifulSoup

PAGES = [
    "https://bg3.wiki/wiki/List_of_uncommon_weapons",
    "https://bg3.wiki/wiki/List_of_rare_weapons",
    "https://bg3.wiki/wiki/List_of_very_rare_weapons",
    "https://bg3.wiki/wiki/List_of_legendary_weapons",
]

headers = {
    "User-Agent": "bg3-random-build/1.0"
}

session = requests.Session()
session.headers.update(headers)

def fetch(url):
    r = session.get(url, verify=certifi.where(), timeout=30)
    r.raise_for_status()
    return r.text

def is_generic_enchanted_weapon(name):
    return ("+1" in name or "+2" in name)

def infer_dual_wield(item_url):
    html = fetch(item_url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    if "versatile" in text:
        return "yes"

    if "two-handed" in text:
        return "no"

    return "yes"


weapon_rows = []

for url in PAGES:
    html = fetch(url)
    table = pd.read_html(StringIO(html))[0]

    soup = BeautifulSoup(html, "html.parser")

    # Map visible item names to their wiki links
    links = {}

    for a in soup.select("a[href^='/wiki/']"):
        name = a.get_text(strip=True)
        href = a.get("href")

        if name and href:
            links[name] = "https://bg3.wiki" + href

    for item in table["Item"].dropna():
        item_name = str(item).strip()

        if is_generic_enchanted_weapon(item_name):
            continue

        item_url = links.get(item_name)

        if item_url:
            try:
                dual_wield = infer_dual_wield(item_url)
            except Exception as e:
                print(f"Could not inspect {item_name}: {e}")
                dual_wield = "manual"
        else:
            dual_wield = "manual"

        weapon_rows.append({
            "item_name": item_name,
            "dual_wield_option": dual_wield,
            "generic_caster_staff": "",
            "monk_gloves": "",
        })

out = (
    pd.DataFrame(weapon_rows)
    .drop_duplicates(subset=["item_name"])
    .sort_values("item_name")
)

out.to_csv("weapons.csv", index=False)
print(f"Wrote {len(out)} weapons to weapons.csv")
