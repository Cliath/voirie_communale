# -*- coding: utf-8 -*-
"""Patch pour remplacer les regex codées en dur dans apply_ban_style par les paramètres."""
import re

path = r"d:\chemins_ruraux\chemins_ruraux.py"
with open(path, encoding="utf-8") as f:
    src = f.read()

# ---- 1. Expression CASE du renderer ----
old_expr = (
    "        expression = f\"\"\"\n"
    "        CASE \n"
    "            WHEN regexp_match(\"{field_name}\", '(?i)(che(?:min)?|sen(?:tier)?) rural|\\\\\\\\bC\\\\.?R\\\\.?\\\\\\\\b') > 0 THEN 'Chemin rural'\n"
    "            WHEN regexp_match(\"{field_name}\", '(?i)(voi(?:e)?) (com(?:munale)?)|\\\\\\\\bV\\\\.?C\\\\.?\\\\\\\\b') > 0 THEN 'Voie communale'\n"
    "            ELSE 'Autre'\n"
    "        END\n"
    "        \"\"\""
)
new_expr = (
    "        expression = f\"\"\"\n"
    "        CASE \n"
    "            WHEN regexp_match(\"{field_name}\", '{regex_chemin}') > 0 THEN 'Chemin rural'\n"
    "            WHEN regexp_match(\"{field_name}\", '{regex_voie}') > 0 THEN 'Voie communale'\n"
    "            ELSE 'Autre'\n"
    "        END\n"
    "        \"\"\""
)
if old_expr in src:
    src = src.replace(old_expr, new_expr, 1)
    print("OK: expression CASE renderer remplacée")
else:
    print("ERREUR: expression CASE renderer non trouvée")

# ---- 2. Expression CASE des étiquettes ----
old_lbl = (
    "        label_settings.fieldName = (\n"
    "            f\"CASE \"\n"
    "            f\"WHEN regexp_match(\\\"{field_name}\\\", '(?i)(che(?:min)?|sen(?:tier)?) rural|\\\\\\\\bC\\\\.?R\\\\.?\\\\\\\\b') > 0 THEN \\\"{field_name}\\\" \"\n"
    "            f\"WHEN regexp_match(\\\"{field_name}\\\", '(?i)(voi(?:e)?) (com(?:munale)?)|\\\\\\\\bV\\\\.?C\\\\.?\\\\\\\\b') > 0 THEN \\\"{field_name}\\\" \"\n"
    "            f\"ELSE '' END\"\n"
    "        )"
)
new_lbl = (
    "        label_settings.fieldName = (\n"
    "            f\"CASE \"\n"
    "            f\"WHEN regexp_match(\\\"{field_name}\\\", '{regex_chemin}') > 0 THEN \\\"{field_name}\\\" \"\n"
    "            f\"WHEN regexp_match(\\\"{field_name}\\\", '{regex_voie}') > 0 THEN \\\"{field_name}\\\" \"\n"
    "            f\"ELSE '' END\"\n"
    "        )"
)
if old_lbl in src:
    src = src.replace(old_lbl, new_lbl, 1)
    print("OK: expression CASE étiquettes remplacée")
else:
    print("ERREUR: expression CASE étiquettes non trouvée")

# ---- 3. style_callback dans load_ban_wfs ----
old_cb = "            style_callback=self.apply_ban_style\n        )"
new_cb = (
    "            style_callback=lambda lyr: self.apply_ban_style(\n"
    "                lyr,\n"
    "                regex_chemin=SettingsDialog.get('ban_regex_chemin', r'(?i)(che(?:min)?|sen(?:tier)?) rural|\\bC\\.?R\\.?\\b') or r'(?i)(che(?:min)?|sen(?:tier)?) rural|\\bC\\.?R\\.?\\b',\n"
    "                regex_voie=SettingsDialog.get('ban_regex_voie', r'(?i)(voi(?:e)?) (com(?:munale)?)|\\bV\\.?C\\.?\\b') or r'(?i)(voi(?:e)?) (com(?:munale)?)|\\bV\\.?C\\.?\\b',\n"
    "            )\n"
    "        )"
)
if old_cb in src:
    src = src.replace(old_cb, new_cb, 1)
    print("OK: style_callback remplacé")
else:
    print("ERREUR: style_callback non trouvé")

with open(path, "w", encoding="utf-8") as f:
    f.write(src)
print("Fichier sauvegardé.")
