#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de compilation pour le plugin QGIS Voirie Communale
Ignore les widgets QGIS personnalisés lors de la compilation
"""

import sys
import os
import re

try:
    from PyQt5 import uic
    from PyQt5.pyrcc_main import processResourceFile
except ImportError:
    print("Erreur: PyQt5 n'est pas installé")
    print("Installation: pip install PyQt5")
    sys.exit(1)

def compile_resources():
    """Compile resources.qrc -> resources.py"""
    print("Compilation de resources.qrc...")
    try:
        processResourceFile(['resources.qrc'], 'resources.py', False)
        print("✓ resources.py créé")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def compile_ui_with_qgis_widgets():
    """Compile voirie_communale_dialog_base.ui avec support des widgets QGIS"""
    print("\nCompilation de voirie_communale_dialog_base.ui...")
    
    try:
        # Lire le fichier UI
        with open('voirie_communale_dialog_base.ui', 'r', encoding='utf-8') as f:
            ui_content = f.read()
        
        # Créer un fichier UI temporaire sans les widgets QGIS personnalisés
        temp_ui = ui_content.replace('QgsMapLayerComboBox', 'QComboBox')
        temp_ui = temp_ui.replace('<header>qgis.gui</header>', '<header>PyQt5.QtWidgets</header>')
        
        # Supprimer les propriétés spécifiques QGIS
        temp_ui = re.sub(r'<property name="filters">.*?</property>', '', temp_ui, flags=re.DOTALL)
        
        # Écrire le fichier temporaire
        with open('temp_dialog.ui', 'w', encoding='utf-8') as f:
            f.write(temp_ui)
        
        # Compiler le fichier temporaire
        with open('temp_dialog.ui', 'r', encoding='utf-8') as ui_file:
            with open('voirie_communale_dialog_base.py', 'w', encoding='utf-8') as py_file:
                uic.compileUi(ui_file, py_file)
        
        # Lire le fichier compilé
        with open('voirie_communale_dialog_base.py', 'r', encoding='utf-8') as f:
            py_content = f.read()
        
        # Restaurer les imports QGIS
        py_content = py_content.replace('from PyQt5 import QtCore, QtGui, QtWidgets',
                                       'from qgis.PyQt import QtCore, QtGui, QtWidgets\nfrom qgis.gui import QgsMapLayerComboBox')
        py_content = py_content.replace('self.mMapLayerComboBox = QtWidgets.QComboBox',
                                       'self.mMapLayerComboBox = QgsMapLayerComboBox')
        
        # Écrire le fichier final
        with open('voirie_communale_dialog_base.py', 'w', encoding='utf-8') as f:
            f.write(py_content)
        
        # Supprimer le fichier temporaire
        os.remove('temp_dialog.ui')
        
        print("✓ voirie_communale_dialog_base.py créé")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        if os.path.exists('temp_dialog.ui'):
            os.remove('temp_dialog.ui')
        return False

if __name__ == '__main__':
    print("=== Compilation du plugin Voirie Communale ===\n")
    
    # Changer vers le répertoire du script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = True
    success = compile_resources() and success
    success = compile_ui_with_qgis_widgets() and success
    
    if success:
        print("\n✓ Compilation terminée avec succès!")
        sys.exit(0)
    else:
        print("\n✗ Erreurs lors de la compilation")
        sys.exit(1)
