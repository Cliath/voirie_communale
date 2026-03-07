#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer un package ZIP du plugin Voirie Communale
Ce ZIP est installable directement dans QGIS
"""

import os
import sys
import zipfile
from pathlib import Path

# Import de la version
try:
    from version import __version__
except ImportError:
    __version__ = "0.1.0"

# Fichiers et dossiers à inclure dans le ZIP
FILES_TO_INCLUDE = [
    '__init__.py',
    'chemins_ruraux.py',
    'chemins_ruraux_dialog.py',
    'chemins_ruraux_dialog_base.py',
    'resources.py',
    'version.py',
    'metadata.txt',
    'icon.png',
    'README.md',
    'CHANGELOG.md',
    'layer_order.json',
]

# Dossiers à inclure (récursif)
FOLDERS_TO_INCLUDE = [
    'i18n',  # Traductions (si présent)
]

# Fichiers à exclure
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.git',
    '.venv',
    'venv',
    '.idea',
    '.vscode',
    '*.zip',
    'compile*.py',
    'compile.bat',
    'compile.sh',
    '*.ui',  # Fichiers source UI (on garde les .py compilés)
    '*.qrc',  # Fichiers source resources (on garde les .py compilés)
    'temp_*.ui',
]

def should_exclude(file_path):
    """Vérifie si un fichier doit être exclu"""
    file_str = str(file_path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if file_str.endswith(pattern[1:]):
                return True
        elif pattern in file_str:
            return True
    return False

def create_plugin_zip(output_dir='releases'):
    """Crée un ZIP du plugin prêt à être installé dans QGIS"""
    
    print(f"=== Création du package Voirie Communale v{__version__} ===\n")
    
    # Nom du plugin et du fichier ZIP
    plugin_name = 'chemins_ruraux'
    zip_filename = f"{plugin_name}-{__version__}.zip"
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    zip_path = output_path / zip_filename
    if zip_path.exists():
        zip_path.unlink()
        print(f"✓ Ancien ZIP supprimé")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in FILES_TO_INCLUDE:
            file_path = Path(filename)
            if file_path.exists():
                arcname = f"{plugin_name}/{filename}"
                # metadata.txt doit être sans BOM : configparser QGIS ne le supporte pas
                if filename == 'metadata.txt':
                    content = file_path.read_bytes()
                    if content[:3] == b'\xef\xbb\xbf':
                        content = content[3:]
                    zipf.writestr(arcname, content)
                else:
                    zipf.write(file_path, arcname)
                print(f"✓ Ajouté : {filename}")
            else:
                print(f"⚠ Ignoré (non trouvé) : {filename}")
        for folder_name in FOLDERS_TO_INCLUDE:
            folder_path = Path(folder_name)
            if folder_path.exists() and folder_path.is_dir():
                for file_path in folder_path.rglob('*'):
                    if file_path.is_file() and not should_exclude(file_path):
                        arcname = f"{plugin_name}/{file_path}"
                        zipf.write(file_path, arcname)
                        print(f"✓ Ajouté : {file_path}")
    
    # Afficher les informations
    file_size = zip_path.stat().st_size
    file_size_kb = file_size / 1024
    
    print(f"\n{'='*60}")
    print(f"✓ Package créé avec succès !")
    print(f"{'='*60}")
    print(f"Fichier : {zip_path}")
    print(f"Taille  : {file_size_kb:.2f} KB ({file_size} octets)")
    print(f"Version : {__version__}")
    print(f"\n{'='*60}")
    print(f"Installation dans QGIS :")
    print(f"1. Ouvrir QGIS")
    print(f"2. Menu : Extensions → Installer/Gérer les extensions")
    print(f"3. Onglet : Installer depuis un ZIP")
    print(f"4. Sélectionner : {zip_path.absolute()}")
    print(f"5. Cliquer : Installer l'extension")
    print(f"{'='*60}\n")
    
    return zip_path


def main():
    """Fonction principale"""
    # Changer vers le répertoire du script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        create_plugin_zip()
        return 0
    except Exception as e:
        print(f"\n✗ Erreur lors de la création du package : {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
