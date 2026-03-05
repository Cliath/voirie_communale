# -*- coding: utf-8 -*-
"""
Voirie Communale - Plugin QGIS
Recensement de la voirie communale (voies communales et chemins ruraux).
Copyright (C) 2026 Yann Schwarz <yann.schwarz@ign.fr>
Licence : GNU GPL v2+
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog, QDialog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer, QgsMessageLog,
                       Qgis, QgsApplication, QgsLayerTreeGroup, QgsLayerTreeLayer,
                       QgsCoordinateTransform, QgsSettings,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsSingleSymbolRenderer,
                       QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol, QgsFeature, QgsField,
                       QgsGeometry, QgsPointXY,
                       QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
                       QgsTextBufferSettings)
import re
import os
import os.path
import urllib.parse
import urllib.request
import json

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .chemins_ruraux_dialog import CheminsRurauxDialog, TodoDialog, PhotoAeriennesDialog, LauncherDialog, SettingsDialog
# Import version information
from .version import __version__, get_changelog


# Dictionnaire fixe : forme_juridique_abregee → (libellé_complet, couleur_hex)
# Groupes sémantiques par couleur :
#   blues foncés  → État / institutions nationales
#   blues clairs  → Collectivités territoriales
#   bleus-gris    → Établissements publics
#   teals         → Intercommunalité / syndicats
#   verts         → Associations / fondations / mutuelles
#   oranges/ambre → Agriculture / foncier
#   rouges        → Sociétés commerciales de capitaux
#   roses/violets → Sociétés civiles / coopératives
#   gris          → Divers / non identifié
MAJIC_FORMES_JURIDIQUES = {
    # ── État et institutions nationales ──────────────────────────────────────
    'ETAT':  ("État",                                          '#0d3b6e'),
    'BDF':   ("Banque de France",                              '#174b82'),
    'INP':   ("Institut national public",                      '#1e5799'),
    # ── Collectivités territoriales ──────────────────────────────────────────
    'DEPT':  ("Département",                                   '#2471a3'),
    'MET':   ("Métropole",                                     '#2e86c1'),
    'COM':   ("Commune",                                       '#3498db'),
    'COMU':  ("Communauté urbaine",                            '#5dade2'),
    'CCOM':  ("Communauté de communes",                        '#76c4e8'),
    'COME':  ("Commune (établissement)",                       '#5dade2'),
    'CCMU':  ("Communauté de communes (fiscalité multiple)",   '#5dade2'),
    'COLL':  ("Collectivité",                                  '#7fb3d3'),
    'CTOM':  ("Collectivité d'outre-mer",                      '#aed6f1'),
    '7510':  ("Commune (code INSEE 7510)",                     '#3498db'),
    '7520':  ("Commune associée / déléguée (code INSEE 7520)", '#5dade2'),
    # ── Établissements publics ───────────────────────────────────────────────
    'EP':    ("Établissement public",                          '#1a5276'),
    'EPA':   ("Établissement public administratif",            '#1f618d'),
    'EPIC':  ("Établissement public industriel et commercial", '#2874a6'),
    'EPLS':  ("Établissement public local spécialisé",        '#2e86c1'),
    'REGI':  ("Régie",                                        '#3498db'),
    'CCAS':  ("Centre communal d'action sociale",              '#4fa3d1'),
    'CIAS':  ("Centre intercommunal d'action sociale",         '#6cb6da'),
    'HOSP':  ("Hôpital / établissement de santé public",       '#85c1e9'),
    'SDIS':  ("Service départemental d'incendie et de secours",'#a9cce3'),
    'MSA':   ("Mutualité sociale agricole",                    '#abebc6'),
    'ORGI':  ("Organisme de gestion immobilière public",       '#7fb3d3'),
    'EE':    ("Établissement d'enseignement public",           '#5b9bd5'),
    'EN':    ("École nationale",                               '#5b9bd5'),
    'IDE':   ("Établissement de droit public divers",          '#7fb3d3'),
    # ── Intercommunalité / syndicats ─────────────────────────────────────────
    'SIVU':  ("Syndicat intercommunal à vocation unique",      '#148f77'),
    'SIVO':  ("Syndicat intercommunal à vocation multiple",    '#1abc9c'),
    'SYCO':  ("Syndicat de communes",                         '#1abc9c'),
    'SYMC':  ("Syndicat mixte de communes",                    '#17a589'),
    'SYMI':  ("Syndicat mixte",                                '#1abc9c'),
    'SIH':   ("Syndicat intercommunal hospitalier",            '#76d7c4'),
    'PETR':  ("Pôle d'équilibre territorial et rural",         '#a2d9ce'),
    'GIP':   ("Groupement d'intérêt public",                   '#7dcea0'),
    'GCS':   ("Groupement de coopération sanitaire",           '#a9dfb8'),
    'GCSP':  ("Groupement de coopération sanitaire privé",     '#a9dfb8'),
    'CE':    ("Communauté d'établissements / chef d'exploitation", '#27ae60'),
    'CEP':   ("Communauté d'établissements public",            '#2ecc71'),
    'CCAM':  ("Chambre consulaire des arts et métiers",        '#82e0aa'),
    'CCM':   ("Chambre de commerce et de métiers",             '#82e0aa'),
    'SEM':   ("Société d'économie mixte",                      '#117a65'),
    'OHLM':  ("Office HLM",                                    '#1d8348'),
    'OPRO':  ("Office professionnel",                          '#1d8348'),
    # ── Associations / fondations / mutuelles ────────────────────────────────
    'ASS':   ("Association",                                   '#229954'),
    'FON':   ("Fondation",                                     '#52be80'),
    'MUT':   ("Mutuelle",                                      '#7dcea0'),
    'ACEE':  ("Association loi 1901 (établissement)",          '#a9dfb8'),
    'GIE':   ("Groupement d'intérêt économique",               '#27ae60'),
    'GPAS':  ("Groupement pastoral",                           '#58d68d'),
    'SSRG':  ("Société sportive à responsabilité garantie",    '#82e0aa'),
    'SSRS':  ("Société sportive (autre)",                      '#a9dfb8'),
    'IRC':   ("Institution de retraite complémentaire",        '#7dcea0'),
    'IRE':   ("Institution de retraite d'entreprise",          '#7dcea0'),
    '6412':  ("Société d'assurance mutuelle",                  '#5d6d7e'),
    # ── Agriculture / foncier ────────────────────────────────────────────────
    'GAEC':  ("Groupement agricole d'exploitation en commun",  '#e67e22'),
    'EARL':  ("Exploitation agricole à responsabilité limitée",'#f39c12'),
    'GFA':   ("Groupement foncier agricole",                   '#f0a500'),
    'GFR':   ("Groupement foncier rural",                      '#f5b041'),
    'GFO':   ("Groupement foncier",                            '#f8c471'),
    'GAF':   ("Groupement agri-forestier",                     '#fad7a0'),
    'SCEA':  ("Société civile d'exploitation agricole",        '#f9e79f'),
    'SICA':  ("Société d'intérêt collectif agricole",          '#f7dc6f'),
    'CUMA':  ("Coopérative d'utilisation de matériel agricole",'#f4d03f'),
    'COAG':  ("Coopérative agricole",                          '#d4ac0d'),
    'AFR':   ("Association foncière de remembrement",          '#b7950b'),
    'AFU':   ("Association foncière urbaine",                  '#9a7d0a'),
    'EXP':   ("Exploitation agricole individuelle",            '#f0b27a'),
    # ── Sociétés commerciales de capitaux ────────────────────────────────────
    'SA':    ("Société anonyme",                               '#c0392b'),
    'SAM':   ("Société anonyme mutualiste",                    '#e74c3c'),
    'SAFR':  ("Société anonyme fermière rurale",               '#ec7063'),
    'SARL':  ("Société à responsabilité limitée",              '#e74c3c'),
    'SAS':   ("Société par actions simplifiée",                '#ec7063'),
    'SNC':   ("Société en nom collectif",                      '#f1948a'),
    'SCA':   ("Société en commandite par actions",             '#cd6155'),
    'SE':    ("Société européenne",                            '#a93226'),
    'SLRL':  ("Société libre à responsabilité limitée",        '#e74c3c'),
    'STE':   ("Société (autre)",                               '#f1948a'),
    # ── Sociétés civiles / coopératives ──────────────────────────────────────
    'SC':    ("Société civile",                                '#8e44ad'),
    'SCI':   ("Société civile immobilière",                    '#9b59b6'),
    'SCM':   ("Société civile de moyens",                      '#a569bd'),
    'SCCP':  ("Société civile de construction-vente",          '#af7ac5'),
    'SCOP':  ("Société coopérative ouvrière de production",    '#7d3c98'),
    'SCPI':  ("Société civile de placement immobilier",        '#6c3483'),
    'SCOM':  ("Société coopérative et mutualiste",             '#5b2c6f'),
    # ── Divers identifiés ──────────────────────────────────────────────────────
    'CSBI':  ("Caisse scolaire de bienfaisance",                '#717d7e'),
    'DISU':  ("Divers (usage inconnu)",                         '#717d7e'),
    'PM':    ("Personne morale (divers)",                       '#717d7e'),
    'RAC':   ("Régie autonome communale",                       '#717d7e'),
    'RV':    ("Résidence / divers",                             '#717d7e'),
    'AUDA':  ("Autre administration",                           '#717d7e'),
    'AUDP':  ("Autre de droit privé",                           '#717d7e'),
    'AUEP':  ("Autre entité publique",                          '#717d7e'),
    'AUPE':  ("Autre personne étrangère",                       '#717d7e'),
    'AUPM':  ("Autre personne morale",                          '#717d7e'),
    'AURS':  ("Autre à régime spécial",                         '#717d7e'),
    'AUTA':  ("Autre titre administratif",                      '#717d7e'),
    'AUTC':  ("Autre titre collectif",                          '#717d7e'),
    'INR':   ("Institut national de recherche",                 '#717d7e'),
}
# Couleur par défaut pour les codes non répertoriés
_MAJIC_COLOR_UNKNOWN = '#95a5a6'

# Groupes et couleurs exacts de l'application Koumoul
# Source : configuration de https://koumoul.com/data-fair/app/carte-des-parcelles-des-personnes-morales-majic
# Le champ groupe_personne est un entier (0-9)
MAJIC_GROUPES = {
    0: ("Personnes morales non remarquables", "#FF0000"),
    1: ("État",                               "#F79F11"),
    2: ("Région",                             "#068031"),
    3: ("Département",                        "#6CF163"),
    4: ("Commune",                            "#45C6E6"),
    5: ("Office HLM",                         "#F551E4"),
    6: ("Sociétés d'économie mixte",          "#FFFA00"),
    7: ("Copropriétaires",                    "#04147C"),
    8: ("Associés",                           "#6F2002"),
    9: ("Établissements publics ou organismes associés", "#0521DB"),
}
_MAJIC_GROUPE_DEFAULT_COLOR = "#A337F5"


class CheminsRuraux:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # Log plugin version
        QgsMessageLog.logMessage(
            f"Voirie Communale v{__version__} charg\u00e9",
            "CheminsRuraux",
            Qgis.Info
        )
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CheminsRuraux_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Voirie Communale')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CheminsRuraux', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/chemins_ruraux/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Voirie Communale - Recensement'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.add_action(
            icon_path,
            text=self.tr(u'\u00c0 propos'),
            callback=self.show_about,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        self.add_action(
            icon_path,
            text=self.tr(u'ToDo'),
            callback=self.show_todo,
            add_to_toolbar=False,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Voirie Communale'),
                action)
            self.iface.removeToolBarIcon(action)

    def show_about(self):
        """Affiche la boîte de dialogue \u00c0 propos."""
        msg = QMessageBox(self.iface.mainWindow())
        msg.setWindowTitle(self.tr("\u00c0 propos - Voirie Communale"))
        msg.setIconPixmap(QIcon(':/plugins/chemins_ruraux/icon.png').pixmap(64, 64))
        msg.setText(
            f"<b>Voirie Communale</b> v{__version__}<br><br>"
            "Plugin QGIS pour le recensement de la voirie communale<br>"
            "(voies communales et chemins ruraux).<br><br>"
            "<b>Auteur :</b> Yann Schwarz &lt;yann.schwarz@ign.fr&gt;<br>"
            "<b>Licence :</b> GNU GPL v2+<br>"
            "<b>Source :</b> <a href='https://github.com/Cliath/chemins_ruraux'>"
            "github.com/Cliath/chemins_ruraux</a>"
        )
        msg.setTextFormat(1)  # Qt::RichText
        msg.exec_()

    def show_todo(self):
        """Ouvre la fenêtre ToDo (lit/écrite dans le profil utilisateur QGIS)."""
        todo_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), 'chemins_ruraux')
        os.makedirs(todo_dir, exist_ok=True)
        todo_path = os.path.join(todo_dir, 'TODO.md')
        # Créer le fichier avec un contenu initial s'il n'existe pas encore
        if not os.path.exists(todo_path):
            plugin_todo = os.path.join(os.path.dirname(__file__), 'TODO.md')
            if os.path.exists(plugin_todo):
                import shutil
                shutil.copy2(plugin_todo, todo_path)
            else:
                with open(todo_path, 'w', encoding='utf-8') as f:
                    f.write('# TODO - Voirie Communale\n\n## En cours\n\n## À faire\n\n## Idées\n')
        dlg = TodoDialog(todo_path, parent=self.iface.mainWindow())
        dlg.exec_()

    def validate_and_load(self):
        """Valide le code INSEE et charge les données selon le bouton radio sélectionné"""
        
        # Récupérer le code INSEE saisi par l'utilisateur
        code_insee = self.dlg.txtCodeInsee.text().strip().upper()
        
        # Validation du code INSEE français
        # Format attendu : 2 caractères (département) + 3 chiffres (commune)
        # Départements métropole : 01-19, 2A, 2B, 21-95
        # DOM-TOM : 971-976 (3 chiffres + 2 chiffres)
        insee_pattern = re.compile(
            r'^('
            r'0[1-9]\d{3}|'           # 01-09 + 3 chiffres
            r'[1-8]\d{4}|'            # 10-89 + 3 chiffres  
            r'9[0-5]\d{3}|'           # 90-95 + 3 chiffres
            r'2[AB]\d{3}|'            # 2A/2B (Corse) + 3 chiffres
            r'97[1-6]\d{2}|'          # 971-976 (DOM) + 2 chiffres
            r'98[4-8]\d{2}'           # 984-988 (TOM) + 2 chiffres
            r')$'
        )
        
        if not code_insee:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Code INSEE manquant",
                "Veuillez saisir le code INSEE de la commune (5 chiffres).\n"
                "Exemple : 75056 pour Paris, 13055 pour Marseille, 2A004 pour Ajaccio."
            )
            return
        
        if not insee_pattern.match(code_insee):
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Code INSEE invalide",
                f"Le code INSEE '{code_insee}' est invalide.\n\n"
                "Format attendu :\n"
                "- Métropole : 2 chiffres (département) + 3 chiffres (commune)\n"
                "  Exemples : 75056 (Paris), 13055 (Marseille), 69123 (Lyon)\n"
                "- Corse : 2A ou 2B + 3 chiffres\n"
                "  Exemple : 2A004 (Ajaccio)\n"
                "- DOM-TOM : 971-976 ou 984-988 + 2 chiffres\n"
                "  Exemples : 97105 (Basse-Terre), 98411 (Nouméa)"
            )
            return

        # Mémoriser le code INSEE et la sélection des couches
        SettingsDialog.set('last_insee', code_insee)
        checked_layers = [n for n in self.dlg._layer_checkboxes if getattr(self.dlg, n).isChecked()]
        SettingsDialog.set('checked_layers', checked_layers)

        # Vérifier quelles données charger
        cadastre_checked = self.dlg.chkCadastre.isChecked()
        commune_checked = self.dlg.chkCommune.isChecked()
        ban_checked = self.dlg.chkBAN.isChecked()
        voirie_checked = self.dlg.chkVoirie.isChecked()
        voirie_dep_checked = self.dlg.chkVoirieDep.isChecked()
        osm_routes_checked = self.dlg.chkOsmRoutes.isChecked()
        bdtopo_routesnom_checked = hasattr(self.dlg, 'chkBDTopoRoutesNom') and self.dlg.chkBDTopoRoutesNom.isChecked()
        majic_checked = self.dlg.chkMajic.isChecked()
        scan_etat_major_checked = hasattr(self.dlg, 'chkScanEtatMajor') and self.dlg.chkScanEtatMajor.isChecked()
        scan_cassini_checked = hasattr(self.dlg, 'chkScanCassini') and self.dlg.chkScanCassini.isChecked()
        scan50_1950_checked = hasattr(self.dlg, 'chkScan50_1950') and self.dlg.chkScan50_1950.isChecked()
        waze_tiles_checked = hasattr(self.dlg, 'chkWazeTiles') and self.dlg.chkWazeTiles.isChecked()
        osmfr_checked = hasattr(self.dlg, 'chkOsmFR') and self.dlg.chkOsmFR.isChecked()
        photo_aeriennes_checked = hasattr(self.dlg, 'chkPhotoAeriennes') and self.dlg.chkPhotoAeriennes.isChecked()
        bd_ortho_checked = hasattr(self.dlg, 'chkBDOrtho') and self.dlg.chkBDOrtho.isChecked()
        mnt_lidar_checked = hasattr(self.dlg, 'chkMNTLidar') and self.dlg.chkMNTLidar.isChecked()
        plan_ign_checked = hasattr(self.dlg, 'chkPlanIGN') and self.dlg.chkPlanIGN.isChecked()

        # La commune est obligatoire dès qu'une donnée nécessite un filtre géométrique BBOX
        needs_bbox = voirie_checked or voirie_dep_checked or osm_routes_checked or bdtopo_routesnom_checked
        if needs_bbox:
            commune_checked = True
        
        if not cadastre_checked and not commune_checked and not ban_checked and not voirie_checked and not voirie_dep_checked and not osm_routes_checked and not bdtopo_routesnom_checked and not majic_checked and not scan_etat_major_checked and not scan_cassini_checked and not scan50_1950_checked and not waze_tiles_checked and not osmfr_checked and not photo_aeriennes_checked and not bd_ortho_checked and not mnt_lidar_checked and not plan_ign_checked:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Sélection requise",
                "Veuillez cocher au moins un type de données à charger."
            )
            return
        
        # Charger les données sélectionnées
        results = []
        loaded_layers = []
        commune_layer = None

        # Si photos aériennes cochées, ouvrir le dialogue de sélection avant la progression
        photo_aeriennes_sources = []
        if photo_aeriennes_checked:
            dlg_photos = PhotoAeriennesDialog(parent=self.iface.mainWindow())
            if dlg_photos.exec_() != QDialog.Accepted:
                photo_aeriennes_checked = False
            else:
                photo_aeriennes_sources = dlg_photos.selected_sources()
                if not photo_aeriennes_sources:
                    photo_aeriennes_checked = False

        # Compter le nombre d'étapes pour la barre de progression
        steps = sum([
            cadastre_checked, commune_checked, ban_checked,
            voirie_checked, voirie_dep_checked, osm_routes_checked,
            bdtopo_routesnom_checked, majic_checked,
            scan_etat_major_checked, scan_cassini_checked, scan50_1950_checked,
            waze_tiles_checked, osmfr_checked, bd_ortho_checked, mnt_lidar_checked, plan_ign_checked
        ]) + len(photo_aeriennes_sources)

        progress = QProgressDialog(
            "Chargement des données en cours...",
            None,  # pas de bouton Annuler
            0, steps,
            self.iface.mainWindow()
        )
        progress.setWindowTitle("Voirie Communale")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(1500)  # apparaît après 1,5 s d'attente
        progress.setMinimumWidth(400)
        current_step = 0

        def advance(label):
            nonlocal current_step
            current_step += 1
            progress.setLabelText(label)
            progress.setValue(current_step)
            QApplication.processEvents()

        if cadastre_checked:
            advance(f"Chargement du cadastre ({code_insee})...")
            cadastre_success, cadastre_layers = self.load_cadastre_wms(code_insee)
            results.append(('Cadastre', cadastre_success))
            loaded_layers.extend(cadastre_layers)
        
        if commune_checked:
            advance(f"Chargement de l'emprise communale ({code_insee})...")
            commune_success, commune_layer = self.load_commune_wfs(code_insee)
            results.append(('Emprise communale', commune_success))
            if commune_layer:
                loaded_layers.append(commune_layer)

        # Extraire le BBOX de la commune pour les couches nécessitant un filtre géométrique
        # On itère sur les features (pas layer.extent() qui renvoie l'extent serveur complet)
        commune_bbox = None
        if needs_bbox and commune_layer and commune_layer.isValid():
            for feat in commune_layer.getFeatures():
                if feat.hasGeometry():
                    b = feat.geometry().boundingBox()
                    commune_bbox = (b.xMinimum(), b.yMinimum(), b.xMaximum(), b.yMaximum())
                    break

        if needs_bbox and commune_bbox is None:
            # La commune n'a pas pu être chargée : impossible de filtrer les couches BBOX-dépendantes
            progress.close()
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Emprise communale indisponible",
                f"Impossible de charger l'emprise de la commune {code_insee}.\n\n"
                "Les couches nécessitant un filtre géographique (Voirie, OSM Routes, BD TOPO) "
                "ne peuvent pas être chargées sans ce prérequis.\n\n"
                "Vérifiez le code INSEE et votre connexion internet."
            )
            self.dlg.raise_()
            self.dlg.activateWindow()
            return

        if ban_checked:
            advance(f"Chargement des adresses BAN ({code_insee})...")
            ban_success, ban_layer = self.load_ban_wfs(code_insee)
            results.append(('Adresses BAN', ban_success))
            if ban_layer:
                loaded_layers.append(ban_layer)
        
        if voirie_checked:
            advance(f"Chargement de la voirie communale ({code_insee})...")
            voirie_success, voirie_layer = self.load_voirie_wfs(code_insee, commune_bbox)
            results.append(('Voirie communale', voirie_success))
            if voirie_layer:
                loaded_layers.append(voirie_layer)
        
        if voirie_dep_checked:
            advance(f"Chargement de la voirie départementale ({code_insee})...")
            voirie_dep_success, voirie_dep_layer = self.load_voirie_dep_wfs(code_insee, commune_bbox)
            results.append(('Voirie départementale', voirie_dep_success))
            if voirie_dep_layer:
                loaded_layers.append(voirie_dep_layer)

        if osm_routes_checked:
            advance(f"Chargement des routes OSM ({code_insee})...")
            osm_success, osm_layer = self.load_osm_roads(code_insee, commune_bbox)
            results.append(('Routes OSM', osm_success))
            if osm_layer:
                loaded_layers.append(osm_layer)



        if bdtopo_routesnom_checked:
            advance(f"Chargement BD TOPO Routes nommées ({code_insee})...")
            bdtopo_routesnom_success, bdtopo_routesnom_layer = self.load_bdtopo_routesnom_wfs(code_insee, commune_bbox)
            results.append(('BD TOPO Routes numérotées ou nommées', bdtopo_routesnom_success))
            if bdtopo_routesnom_layer:
                loaded_layers.append(bdtopo_routesnom_layer)

        if majic_checked:
            advance(f"Chargement des parcelles MAJIC ({code_insee})...")
            majic_success, majic_layer = self.load_majic_parcelles(code_insee)
            results.append(('Parcelles MAJIC', majic_success))
            if majic_layer:
                loaded_layers.append(majic_layer)
            elif not majic_success:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Erreur MAJIC",
                    "Impossible de charger les parcelles MAJIC pour la commune sélectionnée.\n\n"
                    "Vérifiez la connexion internet, le code INSEE, ou consultez le journal des messages pour plus de détails."
                )

        if scan_etat_major_checked:
            advance(f"Chargement Carte d'État-Major ({code_insee})...")
            em_success, em_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.ETATMAJOR40', f"Carte d'État-Major")
            results.append(("Carte d'État-Major", em_success))
            loaded_layers.extend(em_layers)

        if scan_cassini_checked:
            advance(f"Chargement Carte de Cassini ({code_insee})...")
            cassini_success, cassini_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.CASSINI', 'Carte de Cassini')
            results.append(('Carte de Cassini', cassini_success))
            loaded_layers.extend(cassini_layers)

        if scan50_1950_checked:
            advance(f"Chargement SCAN 50\u00ae 1950 ({code_insee})...")
            scan50_success, scan50_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN50.1950', 'SCAN 50\u00ae 1950')
            results.append(('SCAN 50\u00ae 1950', scan50_success))
            loaded_layers.extend(scan50_layers)

        if waze_tiles_checked:
            advance("Chargement Waze...")
            waze_success, waze_layers = self.load_xyz_tile_layer(
                'https://www.waze.com/row-tiles/editor/roads/{z}/{x}/{y}/tile.png',
                'Waze',
                zmin=0, zmax=19
            )
            results.append(('Waze', waze_success))
            loaded_layers.extend(waze_layers)

        if osmfr_checked:
            advance("Chargement OSM France...")
            osmfr_success, osmfr_layers = self.load_xyz_tile_layer(
                'https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
                'OSM France',
                zmin=0, zmax=20
            )
            results.append(('OSM France', osmfr_success))
            loaded_layers.extend(osmfr_layers)

        if bd_ortho_checked:
            advance("Chargement BD ORTHO\u00ae 20 cm...")
            bdortho_success, bdortho_layers = self._load_wms_layer('HR.ORTHOIMAGERY.ORTHOPHOTOS', 'BD ORTHO\u00ae 20 cm', 'EPSG:2154')
            results.append(('BD ORTHO\u00ae 20 cm', bdortho_success))
            loaded_layers.extend(bdortho_layers)

        if mnt_lidar_checked:
            advance("Chargement MNT LiDAR HD...")
            mntlidar_success, mntlidar_layers = self._load_wms_layer('IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW', 'MNT LiDAR HD', 'EPSG:4326')
            results.append(('MNT LiDAR HD', mntlidar_success))
            loaded_layers.extend(mntlidar_layers)

        if plan_ign_checked:
            advance("Chargement PLAN IGN J+1...")
            planign_success, planign_layers = self._load_wms_layer('GEOGRAPHICALGRIDSYSTEMS.MAPS.BDUNI.J1', 'PLAN IGN J+1', 'EPSG:3857')
            results.append(('PLAN IGN J+1', planign_success))
            loaded_layers.extend(planign_layers)

        for typename, display_name in photo_aeriennes_sources:
            advance(f"Chargement {display_name}...")
            ph_success, ph_layers = self.load_scan_historique_wms(typename, display_name)
            results.append((display_name, ph_success))
            loaded_layers.extend(ph_layers)

        # Fermer la boîte de progression
        progress.setValue(steps)
        progress.close()

        # Récupérer le nom de la commune pour nommer le groupe
        commune_name = self._get_commune_name(code_insee, commune_layer)

        # Réordonner les couches dans le panneau selon l'ordre canonique
        if SettingsDialog.get('auto_reorder', True, bool):
            self._reorder_layers(code_insee)

        # Regrouper toutes les couches dans un groupe dédié
        self._group_commune_layers(code_insee, commune_name)

        # Zoomer sur l'emprise de la commune
        success_count = sum(1 for _, success in results if success)
        if success_count > 0 and SettingsDialog.get('auto_zoom', True, bool):
            canvas = self.iface.mapCanvas()
            zoom_extent = None
            # Utiliser la couche commune chargée, ou en chercher une dans le projet
            zoom_commune = commune_layer
            if zoom_commune is None or not zoom_commune.isValid():
                for layer_id, layer in QgsProject.instance().mapLayers().items():
                    if isinstance(layer, QgsVectorLayer) and layer.name() == f"Commune {code_insee}":
                        zoom_commune = layer
                        break
            if zoom_commune and zoom_commune.isValid():
                zoom_commune.updateExtents()
                zoom_extent = zoom_commune.extent()
                if not zoom_extent.isEmpty():
                    project_crs = canvas.mapSettings().destinationCrs()
                    commune_crs = zoom_commune.crs()
                    if commune_crs and commune_crs != project_crs:
                        transform = QgsCoordinateTransform(commune_crs, project_crs, QgsProject.instance())
                        zoom_extent = transform.transformBoundingBox(zoom_extent)
                    zoom_extent.scale(1.05)
            if zoom_extent and not zoom_extent.isEmpty():
                canvas.setExtent(zoom_extent)
                canvas.refresh()
            else:
                canvas.zoomToFullExtent()
                canvas.refresh()

        # Message récapitulatif si plusieurs types de données ont été chargés
        if len(results) > 1:
            if success_count == len(results):
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Chargement terminé",
                    f"Toutes les données ont été chargées avec succès pour le code INSEE {code_insee}."
                )
            elif success_count > 0:
                success_types = [name for name, success in results if success]
                failed_types = [name for name, success in results if not success]
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Chargement partiel",
                    f"Chargé avec succès : {', '.join(success_types)}\n"
                    f"Échec : {', '.join(failed_types)}\n\n"
                    "Consultez le journal des messages pour plus de détails."
                )

        # TOUJOURS ramener le dialogue au premier plan à la fin
        self.dlg.raise_()
        self.dlg.activateWindow()

    def load_bdtopo_routesnom_wfs(self, code_insee, bbox=None):
        """Charge les routes numérotées ou nommées depuis le WFS BD TOPO IGN Géoplateforme.

        Args:
            code_insee: Code INSEE de la commune
            bbox: Emprise de la commune (xmin, ymin, xmax, ymax) en EPSG:4326 (toujours fourni)

        Returns:
            tuple: (bool, QgsVectorLayer ou None)
        """
        success, layer = self.load_wfs_layer(
            typename="BDTOPO_V3:route_numerotee_ou_nommee",
            layer_name=f"BD TOPO Routes numérotées ou nommées {code_insee}",
            crs="EPSG:4326",
            bbox=bbox,
            geom_field="geometrie"
        )

        # Appliquer une symbologie catégorisée sur 'type_de_route'
        if layer and layer.isValid():
            from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol
            categories = []
            # Exemple de catégories (adapter selon les valeurs réelles du champ type_de_route)
            color_map = {
                'Autoroute': '#FF0000',
                'Nationale': '#0000FF',
                'Départementale': '#00AA00',
                'Route intercommunale': '#FF69B4',
                'Voie communale': '#FFD700',
                'Chemin rural': '#A0522D'
            }
            for route_type, color in color_map.items():
                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                symbol.setColor(QColor(color))
                category = QgsRendererCategory(route_type, symbol, route_type)
                categories.append(category)
            renderer = QgsCategorizedSymbolRenderer('type_de_route', categories)
            layer.setRenderer(renderer)
            layer.triggerRepaint()

        if not any([
            self.dlg.chkCadastre.isChecked(),
            self.dlg.chkCommune.isChecked(),
            self.dlg.chkBAN.isChecked(),
            self.dlg.chkVoirie.isChecked(),
            self.dlg.chkVoirieDep.isChecked(),
            self.dlg.chkOsmRoutes.isChecked(),
        ]):
            if success:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "BD TOPO Routes numérotées ou nommées chargées",
                    f"Les routes numérotées ou nommées BD TOPO de la commune {code_insee} ont été chargées avec succès."
                )
            else:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "BD TOPO Routes numérotées ou nommées non disponible",
                    f"Impossible de charger les routes numérotées ou nommées BD TOPO pour le code INSEE {code_insee}.\n\n"
                    "Consultez le journal des messages pour plus de détails."
                )

        return success, layer

    def load_xyz_tile_layer(self, url, display_name, zmin=0, zmax=19):
        """Charge une couche de tuiles XYZ.

        Args:
            url (str): URL du service XYZ avec {z}/{x}/{y} comme variables de tuile
            display_name (str): Nom affiché dans le panneau des couches
            zmin (int): Niveau de zoom minimum
            zmax (int): Niveau de zoom maximum

        Returns:
            tuple: (bool, list) - (succès, liste des couches chargées)
        """
        try:
            uri = f"type=xyz&url={url}&zmax={zmax}&zmin={zmin}"
            self._remove_layers_by_name(display_name)
            layer = QgsRasterLayer(uri, display_name, 'wms')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                QgsMessageLog.logMessage(
                    f"Tuiles XYZ chargées : {display_name}",
                    "CheminsRuraux",
                    Qgis.Info
                )
                return True, [layer]
            else:
                QgsMessageLog.logMessage(
                    f"Impossible de charger les tuiles XYZ : {display_name} \u2014 URI : {uri}",
                    "CheminsRuraux",
                    Qgis.Warning
                )
                return False, []
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Erreur chargement tuiles XYZ {display_name} : {str(e)}",
                "CheminsRuraux",
                Qgis.Critical
            )
            return False, []

    def load_cadastre_wms(self, code_insee):
        """Charge les couches cadastrales WMS pour le code INSEE donné
        
        Returns:
            tuple: (bool, list) - (succès, liste des couches chargées)
        """
        
        # URL du service WMS INSPIRE du cadastre (DGFiP)
        wms_url = f"https://inspire.cadastre.gouv.fr/scpc/{code_insee}.wms"
        
        # Configuration des paramètres WMS communs
        crs = "EPSG:2154"  # Lambert 93
        format_type = "image/png"
        
        # Liste pour stocker les couches créées
        created_layers = []
        
        # Toutes les couches disponibles sur le service INSPIRE
        layers_to_load = [
            {'name': 'CP.CadastralParcel', 'title': 'Parcelles cadastrales'},
            {'name': 'BU.Building', 'title': 'Bâtiments'},
            {'name': 'SUBFISCAL', 'title': 'Subdivisions fiscales'},
            {'name': 'LIEUDIT', 'title': 'Lieux-dits'},
            {'name': 'AMORCES_CAD', 'title': 'Amorces cadastrales'},
            {'name': 'CLOTURE', 'title': 'Clôtures'},
            {'name': 'DETAIL_TOPO', 'title': 'Détails topographiques'},
            {'name': 'HYDRO', 'title': 'Hydrographie'},
            {'name': 'VOIE_COMMUNICATION', 'title': 'Voies de communication'},
            {'name': 'BORNE_REPERE', 'title': 'Bornes et repères'}
        ]
        
        # Créer un groupe dans l'arbre des couches
        root = QgsProject.instance().layerTreeRoot()
        group_name = f"Cadastre - {code_insee}"
        self._remove_group_by_name(group_name)
        cadastre_group = root.addGroup(group_name)
        
        loaded_count = 0
        errors = []
        
        for layer_info in layers_to_load:
            # Construction de l'URI WMS
            uri = f"crs={crs}&format={format_type}&layers={layer_info['name']}&styles&url={wms_url}"
            
            QgsMessageLog.logMessage(
                f"Tentative de chargement : {layer_info['title']}",
                "CheminsRuraux",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"URI WMS : {uri}",
                "CheminsRuraux",
                Qgis.Info
            )
            
            # Créer la couche WMS
            wms_layer = QgsRasterLayer(uri, layer_info['title'], 'wms')
            
            if wms_layer.isValid():
                # Ajouter la couche au projet sans l'afficher immédiatement
                QgsProject.instance().addMapLayer(wms_layer, False)
                # Ajouter la couche au groupe
                cadastre_group.addLayer(wms_layer)
                created_layers.append(wms_layer)
                loaded_count += 1
                QgsMessageLog.logMessage(
                    f"✓ Couche {layer_info['title']} chargée avec succès",
                    "CheminsRuraux",
                    Qgis.Success
                )
            else:
                error_msg = f"Échec du chargement de {layer_info['title']}"
                errors.append(layer_info['title'])
                QgsMessageLog.logMessage(
                    f"✗ {error_msg}",
                    "CheminsRuraux",
                    Qgis.Warning
                )
                QgsMessageLog.logMessage(
                    f"Erreur détaillée : {wms_layer.error().message()}",
                    "CheminsRuraux",
                    Qgis.Warning
                )
        
        if loaded_count > 0:
            # Si c'est le seul type de données chargé, afficher un message
            if not self.dlg.chkCommune.isChecked() and not self.dlg.chkBAN.isChecked():
                message = f"{loaded_count} couche(s) cadastrale(s) chargée(s) avec succès."
                if errors:
                    message += f"\n\nCouches en erreur : {', '.join(errors)}"
                    message += "\n\nConsultez le journal des messages (Vue → Panneaux → Journal des messages) pour plus de détails."
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Cadastre chargé",
                    message
                )
            return True, created_layers
        else:
            # Si c'est le seul type de données chargé, afficher un message d'erreur
            if not self.dlg.chkCommune.isChecked() and not self.dlg.chkBAN.isChecked():
                error_details = "Aucune couche n'a pu être chargée.\n\n"
                error_details += f"Code INSEE : {code_insee}\n"
                error_details += f"URL : {wms_url}\n\n"
                error_details += "Vérifiez :\n"
                error_details += "1. Le code INSEE est correct\n"
                error_details += "2. Votre connexion internet\n"
                error_details += "3. Le journal des messages pour plus de détails"
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Erreur de chargement",
                    error_details
                )
            return False, []

    def load_scan_historique_wms(self, layer_name_wms, display_name):
        """Charge un scan historique IGN (EPSG:2154). Délègue à _load_wms_layer."""
        return self._load_wms_layer(layer_name_wms, display_name, 'EPSG:2154')

    def load_wms_epsg3857(self, layer_name_wms, display_name):
        """Charge une couche WMS IGN en EPSG:3857. Délègue à _load_wms_layer."""
        return self._load_wms_layer(layer_name_wms, display_name, 'EPSG:3857')

    def _load_wms_layer(self, layer_name_wms, display_name, crs='EPSG:2154'):
        """Charge une couche WMS depuis la Géoplateforme IGN (wms-r).

        Args:
            layer_name_wms: Nom de la couche WMS (typename)
            display_name: Nom affiché dans QGIS
            crs: CRS demandé au serveur (ex: 'EPSG:2154', 'EPSG:3857', 'IGNF:WGS84G')

        Returns:
            tuple: (bool, list) - (succès, liste des couches créées)
        """
        WMS_URL = "https://data.geopf.fr/wms-r"
        uri = f"crs={crs}&format=image/png&layers={layer_name_wms}&styles&url={WMS_URL}"

        QgsMessageLog.logMessage(
            f"Chargement WMS ({crs}) : {display_name}",
            "CheminsRuraux", Qgis.Info
        )

        self._remove_layers_by_name(display_name)
        wms_layer = QgsRasterLayer(uri, display_name, 'wms')

        if wms_layer.isValid():
            QgsProject.instance().addMapLayer(wms_layer)
            QgsMessageLog.logMessage(
                f"✓ {display_name} chargée avec succès",
                "CheminsRuraux", Qgis.Success
            )
            return True, [wms_layer]
        else:
            QgsMessageLog.logMessage(
                f"✗ Impossible de charger {display_name} : {wms_layer.error().message()}",
                "CheminsRuraux", Qgis.Warning
            )
            return False, []

    # URL du service WFS IGN Géoplateforme (constante pour tous les services WFS)
    WFS_IGN_URL = "https://data.geopf.fr/wfs"

    def _reorder_layers(self, code_insee):
        """Réordonne les couches chargées dans le panneau selon un ordre canonique.

        Ordre canonique (du haut vers le bas) :
        vecteurs détaillés → emprise → fonds raster → rasters historiques.
        Les couches absentes sont ignorées.
        """
        root = QgsProject.instance().layerTreeRoot()

        # Ordre désiré : index 0 = tout en haut du panneau
        canonical_order = [
            f"BD TOPO Routes numérotées ou nommées {code_insee}",
            f"DGCL Voirie communale retenue DSR 2025 {code_insee}",
            f"DGCL Voirie départementale retenue DGF 2025 {code_insee}",
            f"OSM Routes {code_insee}",
            f"Adresses BAN {code_insee}",
            f"Parcelles MAJIC {code_insee}",
            f"Commune {code_insee}",
            "PLAN IGN J+1",
            "Waze",
            "OSM France",
            f"Cadastre - {code_insee}",
            "BD ORTHO\u00ae 20 cm",
            "MNT LiDAR HD",
            "Photos aériennes 1950-1965",
            "Photos aériennes 1965-1980",
            "Photos aériennes 1980-1995",
            "Photos aériennes 2000-2005",
            "Photos aériennes 2006-2010",
            "Photos aériennes 2011-2015",
            "Photos aériennes 2016-2020",
            "Photos aériennes 2021-2023",
            "SCAN 50\u00ae 1950",
            "Carte de Cassini",
            "Carte d'\u00c9tat-Major",
        ]

        # Traitement en ordre inversé : on insère successivement en position 0
        # → le dernier traité se retrouve en tête, soit l'ordre canonique final
        for name in reversed(canonical_order):
            target = None
            for child in root.children():
                if isinstance(child, QgsLayerTreeGroup) and child.name() == name:
                    target = child
                    break
                elif isinstance(child, QgsLayerTreeLayer):
                    layer = child.layer()
                    if layer and layer.name() == name:
                        target = child
                        break
            if target is None:
                continue
            # clone() copie le nœud (et ses enfants pour les groupes)
            # sans dupliquer les objets QgsMapLayer sous-jacents
            clone = target.clone()
            root.insertChildNode(0, clone)
            root.removeChildNode(target)

        QgsMessageLog.logMessage(
            f"Couches réordonnées selon l'ordre canonique pour {code_insee}",
            "CheminsRuraux",
            Qgis.Info
        )

    def _remove_layers_by_name(self, layer_name):
        """Supprime toutes les couches du projet portant ce nom exact."""
        to_remove = [
            lid for lid, lyr in QgsProject.instance().mapLayers().items()
            if lyr.name() == layer_name
        ]
        for lid in to_remove:
            QgsProject.instance().removeMapLayer(lid)

    def _remove_group_by_name(self, group_name):
        """Supprime récursivement un groupe (et ses couches) dans l'arbre des couches."""
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group:
            # Supprimer d'abord les couches du projet
            for child in group.findLayers():
                QgsProject.instance().removeMapLayer(child.layerId())
            root.removeChildNode(group)

    def _get_commune_name(self, code_insee, commune_layer=None):
        """Récupère le nom de la commune depuis sa couche chargée ou les couches du projet.

        Returns:
            str or None: Nom de la commune, ou None si non trouvé
        """
        def _extract_nom(lyr):
            for feature in lyr.getFeatures():
                try:
                    val = feature.attribute('nom_officiel')
                    if val:
                        return str(val)
                except KeyError:
                    pass
            return None

        if commune_layer and commune_layer.isValid():
            nom = _extract_nom(commune_layer)
            if nom:
                return nom

        commune_layer_name = f"Commune {code_insee}"
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == commune_layer_name:
                nom = _extract_nom(lyr)
                if nom:
                    return nom
        return None

    def _group_commune_layers(self, code_insee, commune_name=None):
        """Regroupe les couches de données spécifiques à la commune dans un groupe dédié.

        Seules les couches filtrées sur la commune (vecteurs + cadastre) sont regroupées.
        Les fonds raster communs (PLAN IGN, Waze, BD ORTHO, etc.) restent à la racine.

        Le groupe est nommé "{code_insee} - {nom_commune}" ou "{code_insee}" si le nom est inconnu.
        Si le groupe existe déjà (rechargement partiel), les nouvelles couches y sont ajoutées
        sans supprimer les couches du chargement précédent.
        Les couches dans le groupe sont ensuite réordonnées selon l'ordre canonique.
        """
        root = QgsProject.instance().layerTreeRoot()

        group_name = f"{code_insee} - {commune_name}" if commune_name else code_insee

        # Ordre canonique des couches à l'intérieur du groupe (haut → bas)
        canonical_order_in_group = [
            f"BD TOPO Routes num\u00e9rot\u00e9es ou nomm\u00e9es {code_insee}",
            f"DGCL Voirie communale retenue DSR 2025 {code_insee}",
            f"DGCL Voirie d\u00e9partementale retenue DGF 2025 {code_insee}",
            f"OSM Routes {code_insee}",
            f"Adresses BAN {code_insee}",
            f"Parcelles MAJIC {code_insee}",
            f"Commune {code_insee}",
            f"Cadastre - {code_insee}",
        ]
        canonical_names = set(canonical_order_in_group)

        # Identifier les nœuds à la RACINE à déplacer et la position du premier.
        # On ne touche pas aux nœuds déjà à l'intérieur du groupe existant.
        to_move = []
        first_idx = None
        for i, child in enumerate(root.children()):
            node_name = None
            if isinstance(child, QgsLayerTreeGroup):
                node_name = child.name()
            elif isinstance(child, QgsLayerTreeLayer):
                layer = child.layer()
                if layer:
                    node_name = layer.name()
            if node_name in canonical_names:
                if first_idx is None:
                    first_idx = i
                to_move.append(child)

        # Chercher un groupe existant pour cette commune
        existing_group = root.findGroup(group_name)

        if existing_group:
            # Le groupe existe déjà (rechargement partiel) : ajouter les nouvelles couches
            # sans supprimer celles qui n'ont pas été rechargées.
            for node in to_move:
                clone = node.clone()
                existing_group.addChildNode(clone)
                root.removeChildNode(node)
            target_group = existing_group
        elif to_move:
            # Créer le groupe à la position du premier nœud correspondant
            target_group = root.insertGroup(first_idx, group_name)

            # Déplacer les nœuds dans le groupe (clone + suppression originale)
            for node in to_move:
                clone = node.clone()
                target_group.addChildNode(clone)
                root.removeChildNode(node)

            target_group.setExpanded(True)
        else:
            return

        # Réordonner les couches à l'intérieur du groupe selon l'ordre canonique.
        # Technique identique à _reorder_layers : insertion en position 0 en ordre inversé.
        for name in reversed(canonical_order_in_group):
            target = None
            for child in target_group.children():
                if isinstance(child, QgsLayerTreeLayer):
                    layer = child.layer()
                    if layer and layer.name() == name:
                        target = child
                        break
            if target is None:
                continue
            clone = target.clone()
            target_group.insertChildNode(0, clone)
            target_group.removeChildNode(target)

        QgsMessageLog.logMessage(
            f"Couches regroup\u00e9es et r\u00e9ordonn\u00e9es dans '{group_name}'",
            "CheminsRuraux",
            Qgis.Info
        )

    def load_wfs_layer(self, typename, layer_name, code_insee=None, crs="EPSG:4326",
                       bbox=None, style_callback=None, geom_field="geom"):
        """Charge une couche WFS depuis l'IGN Géoplateforme.

        Deux chemins selon le type de filtre :
        - code_insee : URL HTTP GetFeature + CQL_FILTER (provider WFS QGIS)
        - bbox       : urllib direct + GeoJSON fichier + provider OGR
                       (le provider WFS QGIS ajoute toujours BBOX=-90,-180,90,180
                        ce qui provoque un conflit ou ignore le CQL_FILTER)
        """
        if bbox:
            return self._load_wfs_bbox(typename, layer_name, bbox, crs, geom_field, style_callback)

        # --- Chemin code_insee : provider WFS QGIS ---
        uri_string = (
            f"{self.WFS_IGN_URL}?"
            f"service=WFS&version=2.0.0&request=GetFeature&"
            f"typename={typename}&srsname={crs}"
        )
        if code_insee:
            uri_string += f"&CQL_FILTER=code_insee='{code_insee}'"

        QgsMessageLog.logMessage(f"WFS code_insee: {uri_string}", "CheminsRuraux", Qgis.Info)
        wfs_layer = QgsVectorLayer(uri_string, layer_name, "WFS")

        if wfs_layer.isValid() and wfs_layer.featureCount() > 0:
            self._remove_layers_by_name(layer_name)
            QgsProject.instance().addMapLayer(wfs_layer)
            if style_callback:
                style_callback(wfs_layer)
            QgsMessageLog.logMessage(f"✓ {layer_name} ({wfs_layer.featureCount()} entité(s))", "CheminsRuraux", Qgis.Success)
            return True, wfs_layer
        else:
            QgsMessageLog.logMessage(f"✗ {layer_name} : {wfs_layer.error().message()}", "CheminsRuraux", Qgis.Warning)
            return False, None

    def _load_wfs_bbox(self, typename, layer_name, bbox, crs="EPSG:4326", geom_field="geom", style_callback=None):
        """Charge une couche WFS filtrée par BBOX via urllib + /vsimem/ (RAM GDAL, aucun fichier disque).

        urllib télécharge le GeoJSON, gdal.FileFromMemBuffer l'écrit dans la RAM de GDAL (/vsimem/),
        OGR lit depuis la RAM. Aucun fichier créé sur le disque.
        """
        from osgeo import gdal

        xmin, ymin, xmax, ymax = bbox
        url = (
            f"{self.WFS_IGN_URL}?"
            f"service=WFS&version=2.0.0&request=GetFeature"
            f"&typename={typename}&srsname={crs}"
            f"&outputFormat=application/json"
            f"&BBOX={xmin},{ymin},{xmax},{ymax},{crs}"
        )
        QgsMessageLog.logMessage(f"WFS BBOX: {url}", "CheminsRuraux", Qgis.Info)

        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                payload = resp.read()
        except Exception as exc:
            QgsMessageLog.logMessage(f"✗ Téléchargement WFS BBOX {typename}: {exc}", "CheminsRuraux", Qgis.Warning)
            return False, None

        vsimem_path = f"/vsimem/{typename.replace(':', '_').replace('.', '_')}.json"
        gdal.FileFromMemBuffer(vsimem_path, payload)
        layer = QgsVectorLayer(vsimem_path, layer_name, "ogr")
        if not layer.isValid() or layer.featureCount() == 0:
            gdal.Unlink(vsimem_path)
            QgsMessageLog.logMessage(f"✗ {layer_name} : couche invalide ou vide", "CheminsRuraux", Qgis.Warning)
            return False, None

        self._remove_layers_by_name(layer_name)
        QgsProject.instance().addMapLayer(layer)
        if style_callback:
            style_callback(layer)
        QgsMessageLog.logMessage(f"✓ {layer_name} ({layer.featureCount()} entité(s))", "CheminsRuraux", Qgis.Success)
        return True, layer

    def load_commune_wfs(self, code_insee):
        """Charge l'emprise de la commune depuis le WFS Admin Express IGN
        
        Returns:
            tuple: (bool, QgsVectorLayer ou None) - (succès, couche chargée)
        """
        success, layer = self.load_wfs_layer(
            typename="LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:commune",
            layer_name=f"Commune {code_insee}",
            code_insee=code_insee,
            crs="EPSG:4326"
        )
        
        # Afficher le message seulement si c'est le seul chargement
        if not self.dlg.chkCadastre.isChecked() and not self.dlg.chkBAN.isChecked():
            if success:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Emprise communale chargée",
                    f"L'emprise de la commune {code_insee} a été chargée avec succès."
                )
            else:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Emprise communale non disponible",
                    f"Impossible de charger l'emprise pour le code INSEE {code_insee}.\n\n"
                    "Consultez le journal des messages pour plus de détails."
                )
        
        return success, layer
    
    def apply_ban_style(self, layer,
                         regex_chemin=r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b',
                         regex_voie=r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b'):
        """Applique un style différencié à la couche BAN selon le type de voie

        Args:
            layer: La couche QgsVectorLayer BAN à styliser
            regex_chemin: Expression régulière QGIS pour détecter les chemins ruraux
            regex_voie: Expression régulière QGIS pour détecter les voies communales
        """
        
        # Créer une expression qui catégorise les voies
        # Recherche dans le champ nom_voie les mots-clés
        field_name = 'nom_voie'
        
        # Vérifier que le champ existe
        if layer.fields().indexOf(field_name) == -1:
            QgsMessageLog.logMessage(
                f"Le champ '{field_name}' n'existe pas dans la couche BAN",
                "CheminsRuraux",
                Qgis.Warning
            )
            return
        
        # Définir les catégories avec expressions regex QGIS
        # regexp_match retourne la position (>0) si trouvé, 0 sinon
        expression = f"""
        CASE 
            WHEN regexp_match("{field_name}", '{regex_chemin}') > 0 THEN 'Chemin rural'
            WHEN regexp_match("{field_name}", '{regex_voie}') > 0 THEN 'Voie communale'
            ELSE 'Autre'
        END
        """
        
        # Créer les symboles pour chaque catégorie
        categories = []
        
        # Chemin rural - Marron/Orange
        symbol_chemin = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '#D2691E',  # Chocolat
            'size': '3',
            'outline_color': '#8B4513',  # Saddle brown
            'outline_width': '0.5'
        })
        categories.append(QgsRendererCategory('Chemin rural', symbol_chemin, 'Chemin rural'))
        
        # Voie communale - Bleu
        symbol_voie = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '#4169E1',  # Royal blue
            'size': '3',
            'outline_color': '#191970',  # Midnight blue
            'outline_width': '0.5'
        })
        categories.append(QgsRendererCategory('Voie communale', symbol_voie, 'Voie communale'))
        
        # Autre - Gris
        symbol_autre = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '#808080',  # Gris
            'size': '2.5',
            'outline_color': '#505050',
            'outline_width': '0.5'
        })
        cat_autre = QgsRendererCategory('Autre', symbol_autre, 'Autre')
        cat_autre.setRenderState(False)  # Désactiver par défaut
        categories.append(cat_autre)
        
        # Créer et appliquer le renderer catégorisé
        renderer = QgsCategorizedSymbolRenderer(expression, categories)
        layer.setRenderer(renderer)
        
        # Configurer les étiquettes avec le nom de la voie
        # Afficher uniquement pour les chemins ruraux et voies communales
        
        label_settings = QgsPalLayerSettings()
        label_settings.isExpression = True
        label_settings.fieldName = (
            f"CASE "
            f"WHEN regexp_match(\"{field_name}\", '{regex_chemin}') > 0 THEN \"{field_name}\" "
            f"WHEN regexp_match(\"{field_name}\", '{regex_voie}') > 0 THEN \"{field_name}\" "
            f"ELSE '' END"
        )
        label_settings.enabled = True
        label_settings.placement = QgsPalLayerSettings.AroundPoint
        
        # Format du texte
        text_format = QgsTextFormat()
        text_format.setSize(8)
        text_format.setColor(QColor(0, 0, 0))  # Noir
        
        # Ajouter un buffer blanc autour du texte pour meilleure lisibilité
        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(0.5)
        buffer.setColor(QColor(255, 255, 255))  # Blanc
        text_format.setBuffer(buffer)
        
        label_settings.setFormat(text_format)
        
        # Appliquer les étiquettes à la couche
        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)
        
        layer.triggerRepaint()
        
        QgsMessageLog.logMessage(
            "Style différencié et étiquettes appliqués à la couche BAN (Chemins ruraux / Voies communales)",
            "CheminsRuraux",
            Qgis.Success
        )
    
    def load_ban_wfs(self, code_insee):
        """Charge les adresses de la Base Adresse Nationale (BAN)
        
        Returns:
            tuple: (bool, QgsVectorLayer ou None) - (succès, couche chargée)
        """
        
        # Charger les adresses BAN sans message d'attente
        success, layer = self.load_wfs_layer(
            typename="BAN.DATA.GOUV:ban",
            layer_name=f"Adresses BAN {code_insee}",
            code_insee=code_insee,
            crs="EPSG:4326",
            style_callback=lambda lyr: self.apply_ban_style(
                lyr,
                regex_chemin=SettingsDialog.get('ban_regex_chemin', r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b') or r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b',
                regex_voie=SettingsDialog.get('ban_regex_voie', r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b') or r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b',
            )
        )
        
        # Afficher le message seulement si c'est le seul chargement
        if not self.dlg.chkCadastre.isChecked() and not self.dlg.chkCommune.isChecked():
            if success:
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Adresses BAN chargées",
                    f"{layer.featureCount()} adresse(s) de la commune {code_insee} ont été chargées avec succès."
                )
            else:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "Adresses BAN non disponibles",
                    f"Impossible de charger les adresses pour le code INSEE {code_insee}.\n\n"
                    "Consultez le journal des messages pour plus de détails."
                )
        
        return success, layer
    
    def load_voirie_wfs(self, code_insee, bbox=None):
        """Charge la voirie communale depuis le WFS DGCL (filtre BBOX)."""
        return self.load_wfs_layer(
            typename="DGCL.2025:voirie_communale",
            layer_name=f"DGCL Voirie communale retenue DSR 2025 {code_insee}",
            crs="EPSG:4326",
            bbox=bbox,
            geom_field="geom"
        )

    def load_voirie_dep_wfs(self, code_insee, bbox=None):
        """Charge la voirie départementale depuis le WFS DGCL (filtre BBOX)."""
        return self.load_wfs_layer(
            typename="DGCL.2025:voirie_departementale",
            layer_name=f"DGCL Voirie départementale retenue DGF 2025 {code_insee}",
            crs="EPSG:4326",
            bbox=bbox,
            geom_field="geom"
        )


    def load_majic_parcelles(self, code_insee):
        """Charge les parcelles des personnes morales (MAJIC) sous forme de polygones.

        Stratégie en deux étapes :
        1. Récupère les attributs MAJIC depuis l'API Koumoul (DGFiP) pour la commune.
        2. Charge les polygones de parcelles depuis le WFS IGN Géoplateforme
           (CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle), filtrés par commune.
        3. Crée une couche polygone mémoire avec uniquement les parcelles MAJIC.

        Args:
            code_insee: Code INSEE de la commune (5 caractères)

        Returns:
            tuple: (bool, QgsVectorLayer ou None)
        """

        # ── Étape 1 : attributs MAJIC depuis Koumoul ──────────────────────────
        BASE_URL = "https://koumoul.com/data-fair/api/v1/datasets/parcelles-des-personnes-morales/lines"
        SELECT = ",".join([
            "code_parcelle", "denomination", "groupe_personne",
            "forme_juridique_abregee", "numero_siren", "contenance_parcelle",
            "nature_culture", "adresse"
        ])

        QgsMessageLog.logMessage(
            f"MAJIC : chargement des attributs pour {code_insee}",
            "CheminsRuraux", Qgis.Info
        )

        majic_by_parcelle = {}
        size = 1000
        after = None

        try:
            while True:
                params = {
                    'qs': f'code_commune:{code_insee}',
                    'size': size,
                    'select': SELECT
                }
                if after:
                    params['after'] = after
                url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"

                req = urllib.request.Request(
                    url, headers={'User-Agent': 'QGIS-VoirieCommunale/1.0'}
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))

                for r in data.get('results', []):
                    cp = r.get('code_parcelle')
                    if cp:
                        majic_by_parcelle[cp] = r

                next_url = data.get('next')
                batch_len = len(data.get('results', []))
                if not next_url or batch_len < size:
                    break
                after_qs = urllib.parse.parse_qs(
                    urllib.parse.urlparse(next_url).query
                )
                after = (after_qs.get('after') or [None])[0]
                if not after:
                    break

        except Exception as e:
            QgsMessageLog.logMessage(
                f"MAJIC : erreur API Koumoul : {e}",
                "CheminsRuraux", Qgis.Critical
            )
            return False, None

        if not majic_by_parcelle:
            QgsMessageLog.logMessage(
                f"MAJIC : aucune parcelle trouvée pour {code_insee}",
                "CheminsRuraux", Qgis.Warning
            )
            return False, None

        QgsMessageLog.logMessage(
            f"MAJIC : {len(majic_by_parcelle)} parcelles MAJIC trouvées pour {code_insee}",
            "CheminsRuraux", Qgis.Info
        )

        # ── Étape 2 : polygones depuis le WFS IGN ─────────────────────────────
        # Extraire code_dep et code_com selon le format du code INSEE
        import re as _re
        if _re.match(r'97[1-6]', code_insee):
            code_dep = code_insee[:3]
            code_com = code_insee[3:]
        else:
            code_dep = code_insee[:2]
            code_com = code_insee[2:]

        WFS_URL = "https://data.geopf.fr/wfs"
        wfs_params_base = {
            'SERVICE': 'WFS',
            'VERSION': '2.0.0',
            'REQUEST': 'GetFeature',
            'TYPENAMES': 'CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle',
            'CQL_FILTER': f"code_dep='{code_dep}' AND code_com='{code_com}'",
            'OUTPUTFORMAT': 'application/json',
            'COUNT': 1000
        }

        wfs_features = []
        start_index = 0

        try:
            while True:
                params = dict(wfs_params_base)
                params['STARTINDEX'] = start_index
                url = f"{WFS_URL}?{urllib.parse.urlencode(params)}"
                QgsMessageLog.logMessage(
                    f"MAJIC WFS parcelles (startIndex={start_index}) : {url}",
                    "CheminsRuraux", Qgis.Info
                )
                req = urllib.request.Request(
                    url, headers={'User-Agent': 'QGIS-VoirieCommunale/1.0'}
                )
                with urllib.request.urlopen(req, timeout=60) as response:
                    fc = json.loads(response.read().decode('utf-8'))

                batch = fc.get('features', [])
                wfs_features.extend(batch)
                if len(batch) < 1000:
                    break
                start_index += 1000

        except Exception as e:
            QgsMessageLog.logMessage(
                f"MAJIC : erreur WFS IGN parcelles : {e}",
                "CheminsRuraux", Qgis.Critical
            )
            return False, None

        QgsMessageLog.logMessage(
            f"MAJIC : {len(wfs_features)} polygones WFS chargés pour {code_insee}",
            "CheminsRuraux", Qgis.Info
        )

        # ── Étape 3 : jointure et création de la couche polygone ─────────────
        uri = (
            "MultiPolygon?crs=EPSG:4326"
            "&field=code_parcelle:string"
            "&field=denomination:string"
            "&field=groupe_personne:integer"
            "&field=forme_juridique:string"
            "&field=numero_siren:string"
            "&field=contenance_m2:integer"
            "&field=nature_culture:string"
            "&field=adresse:string"
            "&field=section:string"
            "&field=numero:string"
        )
        layer = QgsVectorLayer(uri, f"Parcelles MAJIC {code_insee}", "memory")
        provider = layer.dataProvider()

        def geojson_to_qgsgeometry(geom_dict):
            """Convertit un dict GeoJSON geometry en QgsGeometry (Polygon/MultiPolygon)."""
            gtype = geom_dict.get('type', '')
            coords = geom_dict.get('coordinates', [])
            if gtype == 'Polygon':
                rings = [[QgsPointXY(x, y) for x, y in ring] for ring in coords]
                return QgsGeometry.fromPolygonXY(rings)
            elif gtype == 'MultiPolygon':
                polys = [
                    [[QgsPointXY(x, y) for x, y in ring] for ring in poly]
                    for poly in coords
                ]
                return QgsGeometry.fromMultiPolygonXY(polys)
            return QgsGeometry()

        features = []
        matched = 0
        for wfs_feat in wfs_features:
            props = wfs_feat.get('properties', {})
            idu = props.get('idu', '')
            # Correction : tester aussi code_parcelle sans padding, sans majuscules, etc.
            candidates = [idu, idu.lstrip('0'), idu.upper(), idu.lower()]
            majic_match = None
            for c in candidates:
                if c in majic_by_parcelle:
                    majic_match = majic_by_parcelle[c]
                    break
            if not majic_match:
                continue

            m = majic_match
            geom_dict = wfs_feat.get('geometry')
            if not geom_dict:
                continue
            geom = geojson_to_qgsgeometry(geom_dict)
            if geom.isNull():
                continue

            feat = QgsFeature()
            feat.setGeometry(geom)
            groupe = m.get('groupe_personne')
            feat.setAttributes([
                idu,
                m.get('denomination', ''),
                int(groupe) if groupe is not None else None,
                m.get('forme_juridique_abregee', ''),
                m.get('numero_siren', ''),
                m.get('contenance_parcelle'),
                m.get('nature_culture', ''),
                m.get('adresse', ''),
                props.get('section', ''),
                props.get('numero', ''),
            ])
            features.append(feat)
            matched += 1

        provider.addFeatures(features)
        layer.updateExtents()

        # ── Rendu catégorisé par groupe_personne (légende identique à Koumoul) ──
        # Seuls les groupes présents dans les données sont ajoutés
        unique_groupes = sorted({
            int(v['groupe_personne'])
            for v in majic_by_parcelle.values()
            if v.get('groupe_personne') is not None
        })
        cat_styles = []
        for g in unique_groupes:
            libelle, couleur = MAJIC_GROUPES.get(g, (f'Groupe {g}', _MAJIC_GROUPE_DEFAULT_COLOR))
            symbol = QgsFillSymbol.createSimple({
                'color': couleur,
                'outline_color': '#333333',
                'outline_width': '0.25',
            })
            cat_styles.append(QgsRendererCategory(g, symbol, libelle))
        layer.setRenderer(QgsCategorizedSymbolRenderer('groupe_personne', cat_styles))

        self._remove_layers_by_name(f"Parcelles MAJIC {code_insee}")
        QgsProject.instance().addMapLayer(layer)

        QgsMessageLog.logMessage(
            f"MAJIC : {matched} parcelles polygones chargées pour {code_insee} "
            f"({len(majic_by_parcelle) - matched} non géolocalisées dans WFS)",
            "CheminsRuraux", Qgis.Info
        )
        return True, layer

    def load_osm_roads(self, code_insee, bbox=None):
        """Charge les routes OSM via Overpass API.

        Args:
            code_insee: Code INSEE de la commune
            bbox: Emprise de la commune (xmin, ymin, xmax, ymax) en EPSG:4326 (toujours fourni)

        Returns:
            tuple: (bool, QgsVectorLayer ou None)
        """
        xmin, ymin, xmax, ymax = bbox
        south, west, north, east = ymin, xmin, ymax, xmax

        query = (
            "[out:json][timeout:120];"
            "("
            f"way[\"highway\"][\"ref\"~\"^(C|R)\"]({south},{west},{north},{east});"
            f"relation[\"route\"][\"ref\"~\"^(C|R)\"]({south},{west},{north},{east});"
            ");"
            "out geom;"
        )

        QgsMessageLog.logMessage(
            f"Requête Overpass OSM (routes ref C/R) pour {code_insee}",
            "CheminsRuraux",
            Qgis.Info
        )

        try:
            data = urllib.parse.urlencode({"data": query}).encode("utf-8")
            request = urllib.request.Request(
                "https://overpass-api.de/api/interpreter",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read().decode("utf-8")
        except Exception as exc:
            QgsMessageLog.logMessage(
                f"Erreur Overpass OSM: {exc}",
                "CheminsRuraux",
                Qgis.Warning
            )
            QMessageBox.warning(
                self.iface.mainWindow(),
                "OSM non disponible",
                "Impossible de télécharger les routes OSM.\n"
                "Consultez le journal des messages pour plus de détails."
            )
            return False, None

        try:
            data_json = json.loads(payload)
        except Exception as exc:
            QgsMessageLog.logMessage(
                f"Erreur parsing JSON Overpass: {exc}",
                "CheminsRuraux",
                Qgis.Warning
            )
            return False, None

        elements = data_json.get("elements", [])
        relation_refs = {}
        for elem in elements:
            if elem.get("type") == "relation":
                ref_val = elem.get("tags", {}).get("ref")
                if not ref_val:
                    continue
                for member in elem.get("members", []):
                    if member.get("type") == "way":
                        relation_refs.setdefault(member.get("ref"), set()).add(ref_val)

        layer_name = f"OSM Routes {code_insee}"
        uri = "LineString?crs=EPSG:4326&field=ref:string&field=name:string&field=highway:string&field=rel_ref:string"
        filtered_layer = QgsVectorLayer(uri, layer_name, "memory")
        filtered_provider = filtered_layer.dataProvider()

        def add_way_to_layer(tags, geometry_points, ref_value, rel_ref_value):
            highway = tags.get("highway")
            if not highway:
                return False
            chosen_ref = ref_value or rel_ref_value
            if not chosen_ref:
                return False
            ref_text = str(chosen_ref).strip().upper()
            if not (ref_text.startswith("C") or ref_text.startswith("R")):
                return False
            points = [QgsPointXY(p["lon"], p["lat"]) for p in geometry_points if "lon" in p and "lat" in p]
            if len(points) < 2:
                return False
            feat = QgsFeature(filtered_layer.fields())
            feat.setGeometry(QgsGeometry.fromPolylineXY(points))
            feat.setAttribute("ref", chosen_ref)
            feat.setAttribute("name", tags.get("name", ""))
            feat.setAttribute("highway", highway)
            feat.setAttribute("rel_ref", rel_ref_value or "")
            filtered_provider.addFeature(feat)
            return True

        matched_count = 0
        added_way_ids = set()

        # 1. Ways de premier niveau (avec geometry inline)
        for elem in elements:
            if elem.get("type") != "way":
                continue
            if "geometry" not in elem:
                continue
            way_id = elem.get("id")
            tags = elem.get("tags", {})
            ref_value = tags.get("ref")
            rel_ref_value = ", ".join(sorted(relation_refs[way_id])) if way_id in relation_refs else None
            if add_way_to_layer(tags, elem["geometry"], ref_value, rel_ref_value):
                matched_count += 1
                added_way_ids.add(way_id)

        # 2. Members des relations (ways avec geometry dans les membres)
        for elem in elements:
            if elem.get("type") != "relation":
                continue
            rel_ref = elem.get("tags", {}).get("ref", "")
            if not rel_ref:
                continue
            for member in elem.get("members", []):
                if member.get("type") != "way":
                    continue
                if "geometry" not in member:
                    continue
                way_id = member.get("ref")
                if way_id in added_way_ids:
                    continue
                tags = member.get("tags", {}) or {}
                if add_way_to_layer(tags, member["geometry"], tags.get("ref"), rel_ref):
                    matched_count += 1
                    added_way_ids.add(way_id)

        if matched_count == 0:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Aucune route C/R",
                "Aucune route avec un 'ref' commençant par C ou R n'a été trouvée."
            )
            return False, None

        self._remove_layers_by_name(layer_name)
        QgsProject.instance().addMapLayer(filtered_layer)
        self._style_osm_layer(filtered_layer)
        return True, filtered_layer

    def _style_osm_layer(self, layer):
        """Applique un style catégorisé CE / C / R basé sur le champ ref, avec étiquettes."""
        from qgis.core import QgsRuleBasedRenderer, QgsLineSymbol

        def make_sym(color, width='0.5'):
            return QgsLineSymbol.createSimple({
                'color': color, 'width': width,
                'capstyle': 'round', 'joinstyle': 'round',
            })

        root = QgsRuleBasedRenderer.Rule(None)

        rules = [
            ('"ref" LIKE \'CE%\'',                           make_sym('#27ae60', '0.6'), 'CE – Chemin d\'exploitation'),
            ('"ref" LIKE \'C%\' AND "ref" NOT LIKE \'CE%\'', make_sym('#e67e22', '0.6'), 'C – Voie communale'),
            ('"ref" LIKE \'R%\'',                            make_sym('#c0392b', '0.6'), 'R – Chemin rural'),
        ]

        for expr, sym, label in rules:
            rule = QgsRuleBasedRenderer.Rule(sym)
            rule.setLabel(label)
            rule.setFilterExpression(expr)
            root.appendChild(rule)

        layer.setRenderer(QgsRuleBasedRenderer(root))

        # Étiquettes : ref en priorité, sinon name
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = "coalesce(nullif(\"ref\",''), nullif(\"name\",''))"
        label_settings.isExpression = True
        label_settings.enabled = True
        label_settings.placement = QgsPalLayerSettings.Line

        text_format = QgsTextFormat()
        text_format.setSize(7)
        text_format.setColor(QColor(40, 40, 40))

        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(0.8)
        buffer.setColor(QColor(255, 255, 255))
        text_format.setBuffer(buffer)

        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()

    def run(self):
        """Ouvre la barre de lancement du plugin."""
        if self.first_start:
            self.first_start = False
            self.launcher = LauncherDialog(
                parent=self.iface.mainWindow(),
                callbacks={
                    'charger':   self.open_charger_dialog,
                    'todo':      self.show_todo,
                    'settings':  self.show_settings,
                    'about':     self.show_about,
                }
            )
            self.launcher.setWindowTitle(f"Voirie Communale v{__version__}")

        self.launcher.show()
        self.launcher.raise_()
        self.launcher.activateWindow()

    def show_settings(self):
        """Ouvre le dialogue de paramètres."""
        dlg = SettingsDialog(parent=self.iface.mainWindow())
        dlg.exec_()

    def open_charger_dialog(self):
        """Ouvre le dialogue de chargement des données."""
        if not hasattr(self, 'dlg') or self.dlg is None:
            self.dlg = CheminsRurauxDialog()
            self.dlg.setWindowTitle(f"Voirie Communale v{__version__} – Chargement des données")
            self.dlg.btnLoadCadastre.clicked.connect(self.validate_and_load)
        # Restaurer le dernier code INSEE
        last_insee = SettingsDialog.get('last_insee', '')
        if last_insee:
            self.dlg.txtCodeInsee.setText(last_insee)
        # Restaurer l'état des cases à cocher
        saved_checked = SettingsDialog.get('checked_layers', None)
        if saved_checked is not None:
            if isinstance(saved_checked, str):
                saved_checked = [saved_checked] if saved_checked else []
            for name in self.dlg._layer_checkboxes:
                widget = getattr(self.dlg, name, None)
                if widget:
                    widget.setChecked(name in saved_checked)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
