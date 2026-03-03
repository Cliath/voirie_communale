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
    QPushButton, QLabel, QSizePolicy, QMessageBox, QCheckBox, QFrame, QToolButton
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsSettings

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
            'chkVoirie', 'chkVoirieDep', 'chkOsmRoutes', 'chkBDTopoRoutesNom', 'chkMajic',
            'chkScanEtatMajor', 'chkScanCassini', 'chkScan50_1950', 'chkWazeTiles', 'chkPhotoAeriennes',
            'chkBDOrtho', 'chkMNTLidar', 'chkPlanIGN'
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


class PhotoAeriennesDialog(QDialog):
    """Dialogue de sélection des photographies aériennes historiques IGN."""

    # (typename WMS, libellé affiché)
    SOURCES = [
        ('ORTHOIMAGERY.ORTHOPHOTOS.1950-1965', 'Photos aériennes 1950-1965 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS.1965-1980', 'Photos aériennes 1965-1980 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS.1980-1995', 'Photos aériennes 1980-1995 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS2000-2005',  'Photos aériennes 2000-2005 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS2006-2010',  'Photos aériennes 2006-2010 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS2011-2015',  'Photos aériennes 2011-2015 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS2016-2020',  'Photos aériennes 2016-2020 (IGN Géoplateforme)'),
        ('ORTHOIMAGERY.ORTHOPHOTOS2021-2023',  'Photos aériennes 2021-2023 (IGN Géoplateforme)'),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photographies aériennes historiques")
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)

        desc = QLabel(
            "Sélectionnez les périodes à charger depuis la Géoplateforme IGN :"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        self._checkboxes = []
        for typename, label in self.SOURCES:
            chk = QCheckBox(label)
            chk.setChecked(True)
            chk.setProperty('typename', typename)
            layout.addWidget(chk)
            self._checkboxes.append(chk)

        layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_ok = QPushButton("Charger")
        self.btn_ok.setDefault(True)
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def selected_sources(self):
        """Retourne la liste des (typename, libellé) cochés."""
        return [
            (chk.property('typename'), chk.text().split(' (')[0])
            for chk in self._checkboxes
            if chk.isChecked()
        ]


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
        """Réactive le bouton Enregistrer après une modification."""
        self.btn_save.setText("Enregistrer")
        self.btn_save.setEnabled(True)
        self.editor.textChanged.disconnect(self._on_modified)


class SettingsDialog(QDialog):
    """Dialogue de paramètres du plugin."""

    _NS = "chemins_ruraux"

    @staticmethod
    def get(key, default, value_type=None):
        """Lit un paramètre depuis QgsSettings."""
        s = QgsSettings()
        full_key = f"chemins_ruraux/{key}"
        if value_type is not None:
            return s.value(full_key, default, type=value_type)
        return s.value(full_key, default)

    @staticmethod
    def set(key, value):
        """Enregistre un paramètre dans QgsSettings."""
        QgsSettings().setValue(f"chemins_ruraux/{key}", value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres - Voirie Communale")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # --- Comportement ---
        lbl_comportement = QLabel("<b>Comportement après chargement</b>")
        layout.addWidget(lbl_comportement)

        self.chk_auto_zoom = QCheckBox("Zoom automatique sur la commune")
        self.chk_auto_zoom.setChecked(self.get('auto_zoom', True, bool))
        layout.addWidget(self.chk_auto_zoom)

        self.chk_auto_reorder = QCheckBox("Réordonnancement automatique des couches")
        self.chk_auto_reorder.setChecked(self.get('auto_reorder', True, bool))
        layout.addWidget(self.chk_auto_reorder)

        layout.addSpacing(4)
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)
        layout.addSpacing(4)

        # --- Mémorisation automatique ---
        lbl_memo = QLabel("<b>Mémorisation automatique</b>")
        layout.addWidget(lbl_memo)

        last_insee = self.get('last_insee', '') or ''
        row = QHBoxLayout()
        row.addWidget(QLabel("Dernier code INSEE chargé :"))
        self.lbl_insee = QLabel(f"<b>{last_insee}</b>" if last_insee else "<i>(aucun)</i>")
        row.addWidget(self.lbl_insee)
        row.addStretch()
        layout.addLayout(row)

        note = QLabel(
            "<small><i>Le code INSEE et la sélection des couches sont mémorisés "
            "automatiquement à chaque chargement.</i></small>"
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addSpacing(12)

        # --- Boutons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setDefault(True)
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self._save_and_accept)
        self.btn_cancel.clicked.connect(self.reject)

    def _save_and_accept(self):
        self.set('auto_zoom', self.chk_auto_zoom.isChecked())
        self.set('auto_reorder', self.chk_auto_reorder.isChecked())
        self.accept()


class LauncherDialog(QDialog):
    """Barre de lancement du plugin : accès rapide aux fonctionnalités principales."""

    _BTN_STYLE = """
        QToolButton {
            font-size: 12px;
            padding: 10px 6px 8px 6px;
            border: 1px solid #c8c8c8;
            border-radius: 6px;
            background: #f7f7f7;
            min-width: 105px;
            min-height: 72px;
        }
        QToolButton:hover:enabled {
            background: #ddeeff;
            border-color: #4a90d9;
        }
        QToolButton:pressed:enabled {
            background: #b8d4f0;
        }
        QToolButton:disabled {
            color: #aaaaaa;
            background: #f0f0f0;
            border-color: #ddd;
        }
    """

    def __init__(self, parent=None, callbacks=None):
        super().__init__(parent)
        callbacks = callbacks or {}
        self.setWindowTitle("Voirie Communale")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setSizeGripEnabled(False)

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        buttons_def = [
            (
                "📂",
                "Charger\ndes données",
                "Ouvre le panneau de chargement des données",
                callbacks.get('charger'),
            ),
            (
                "✏️",
                "Numériser\ndes données",
                "Numérisation des voies (fonctionnalité à venir)",
                None,
            ),
            (
                "📋",
                "Liste des\ntâches",
                "Ouvre le gestionnaire de tâches",
                callbacks.get('todo'),
            ),
            (
                "⚙️",
                "Paramètres",
                "Paramètres du plugin",
                callbacks.get('settings'),
            ),
            (
                "ℹ️",
                "À propos",
                "Informations sur le plugin Voirie Communale",
                callbacks.get('about'),
            ),
        ]

        for icon, label, tooltip, callback in buttons_def:
            btn = QToolButton()
            btn.setText(f"{icon}\n{label}")
            btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(self._BTN_STYLE)
            btn.setEnabled(callback is not None)
            if callback:
                btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())
