# -*- coding: utf-8 -*-
"""
Voirie Communale - Dialogue principal
Copyright (C) 2026 Yann Schwarz <yann.schwarz@ign.fr>
Licence : GNU GPL v2+
"""

from qgis.PyQt import QtWidgets

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
            'chkVoirie', 'chkVoirieDep', 'chkOsmRoutes', 'chkBDTopoRoutesNom', 'chkRpgSna', 'chkMajic'
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
