# -*- coding: utf-8 -*-
"""
Voirie Communale - Dialogue principal
Copyright (C) 2026 Yann Schwarz <yann.schwarz@ign.fr>
Licence : GNU GPL v2+
"""

import os
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QSizePolicy, QMessageBox
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont

# Importer la classe du fichier UI compilé
from .chemins_ruraux_dialog_base import Ui_CheminsRurauxDialogBase


class CheminsRurauxDialog(QtWidgets.QDialog, Ui_CheminsRurauxDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(CheminsRurauxDialog, self).__init__(parent)
        self.setupUi(self)
        # Liste de toutes les cases à cocher de sélection de couches
        self._layer_checkboxes = [
            'chkCadastre', 'chkCommune', 'chkBAN',
            'chkVoirie', 'chkVoirieDep', 'chkOsmRoutes', 'chkBDTopoRoutesNom', 'chkRpgSna', 'chkMajic',
            'chkScanEtatMajor', 'chkScanCassini'
        ]
        # Utiliser 'clicked' (pas 'stateChanged') pour les clics utilisateur sur la case maître
        # afin d'éviter le cycle tristate 0→1→2 qui passe par l'état partiel au premier clic
        self.chkToutSelectionner.clicked.connect(self._on_tout_clicked)
        # Mettre à jour l'état de chkToutSelectionner quand une case individuelle change
        for name in self._layer_checkboxes:
            getattr(self, name).stateChanged.connect(self._update_tout_selectionner)

    def _on_tout_clicked(self, checked):
        """Coche ou décoche toutes les cases."""
        for name in self._layer_checkboxes:
            getattr(self, name).setChecked(checked)

    def _update_tout_selectionner(self):
        """Met à jour la case maître : cochée si toutes les cases le sont."""
        self.chkToutSelectionner.blockSignals(True)
        all_checked = all(getattr(self, name).isChecked() for name in self._layer_checkboxes)
        self.chkToutSelectionner.setChecked(all_checked)
        self.chkToutSelectionner.blockSignals(False)


class TodoDialog(QDialog):
    """Fenêtre d'édition du fichier TODO.md."""

    def __init__(self, todo_path, parent=None):
        super().__init__(parent)
        self.todo_path = todo_path
        self.setWindowTitle("ToDo - Voirie Communale")
        self.resize(600, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        layout = QVBoxLayout(self)

        # Éditeur
        self.editor = QTextEdit()
        font = QFont("Consolas", 10)
        self.editor.setFont(font)
        self.editor.setAcceptRichText(False)
        layout.addWidget(self.editor)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_close = QPushButton("Fermer")
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.btn_save.clicked.connect(self._save)
        self.btn_close.clicked.connect(self.close)

        self._load()

    def _load(self):
        """Charge le contenu de TODO.md."""
        try:
            with open(self.todo_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
        except Exception as e:
            self.editor.setPlainText(f"# TODO\n")

    def _save(self):
        """Enregistre le contenu dans TODO.md."""
        try:
            with open(self.todo_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.btn_save.setText("Enregistré ✓")
            self.btn_save.setEnabled(False)
            # Réactiver après modification
            self.editor.textChanged.connect(self._on_modified)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'enregistrer :\n{e}")

    def _on_modified(self):
        self.btn_save.setText("Enregistrer")
        self.btn_save.setEnabled(True)
        self.editor.textChanged.disconnect(self._on_modified)
