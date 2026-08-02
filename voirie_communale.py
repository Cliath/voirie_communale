# -*- coding: utf-8 -*-
"""
Voirie Communale - Plugin QGIS
Recensement de la voirie communale (voies communales et chemins ruraux).
Copyright (C) 2026 Yann Schwarz <yann.schwarz@ign.fr>
Licence : GNU GPL v2+
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QEventLoop
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog, QDialog, QApplication
from qgis.core import (QgsProject, QgsVectorLayer, QgsMessageLog, Qgis, QgsApplication,
                       QgsCoordinateTransform)
import re
import os
import os.path

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .voirie_communale_dialog import VoirieCommunaleDialog, TodoDialog, PhotoAeriennesDialog, LauncherDialog, SettingsDialog
# Import version information
from .version import __version__, get_changelog

# Mixins extraits dans des modules dédiés (styles, réseau/chargement, arbre des couches)
from .styles import StylesMixin
from .wfs_loader import WfsLoaderMixin, WfsLoadTask
from .layer_order import LayerOrderMixin


class VoirieCommunale(LayerOrderMixin, WfsLoaderMixin, StylesMixin):
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
            "VoirieCommunale",
            Qgis.Info
        )
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VoirieCommunale_{}.qm'.format(locale))

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


    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VoirieCommunale', message)

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

        icon_path = ':/plugins/voirie_communale/icon.png'
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
        msg.setIconPixmap(QIcon(':/plugins/voirie_communale/icon.png').pixmap(64, 64))
        msg.setText(
            f"<b>Voirie Communale</b> v{__version__}<br><br>"
            "Plugin QGIS pour le recensement de la voirie communale<br>"
            "(voies communales et chemins ruraux).<br><br>"
            "<b>Auteur :</b> Yann Schwarz &lt;yann.schwarz@ign.fr&gt;<br>"
            "<b>Licence :</b> GNU GPL v2+<br>"
            "<b>Source :</b> <a href='https://github.com/Cliath/voirie_communale'>"
            "github.com/Cliath/voirie_communale</a>"
        )
        msg.setTextFormat(1)  # Qt::RichText
        msg.exec_()

    def show_todo(self):
        """Ouvre la fenêtre ToDo (lit/écrite dans le profil utilisateur QGIS)."""
        todo_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), 'voirie_communale')
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
        filaires_bal_checked = hasattr(self.dlg, 'chkFilairesBAL') and self.dlg.chkFilairesBAL.isChecked()
        voirie_checked = self.dlg.chkVoirie.isChecked()
        voirie_dep_checked = self.dlg.chkVoirieDep.isChecked()
        osm_routes_checked = self.dlg.chkOsmRoutes.isChecked()
        bdtopo_routesnom_checked = hasattr(self.dlg, 'chkBDTopoRoutesNom') and self.dlg.chkBDTopoRoutesNom.isChecked()
        bdtopo_troncons_checked = hasattr(self.dlg, 'chkBDTopoTroncons') and self.dlg.chkBDTopoTroncons.isChecked()
        magosm_checked = hasattr(self.dlg, 'chkMagOsm') and self.dlg.chkMagOsm.isChecked()
        majic_checked = self.dlg.chkMajic.isChecked()
        scan_etat_major_checked = hasattr(self.dlg, 'chkScanEtatMajor') and self.dlg.chkScanEtatMajor.isChecked()
        scan_cassini_checked = hasattr(self.dlg, 'chkScanCassini') and self.dlg.chkScanCassini.isChecked()
        scan50_1950_checked = hasattr(self.dlg, 'chkScan50_1950') and self.dlg.chkScan50_1950.isChecked()
        waze_tiles_checked = hasattr(self.dlg, 'chkWazeTiles') and self.dlg.chkWazeTiles.isChecked()
        osmfr_checked = hasattr(self.dlg, 'chkOsmFR') and self.dlg.chkOsmFR.isChecked()
        cosia_checked = hasattr(self.dlg, 'chkCoSIA') and self.dlg.chkCoSIA.isChecked()
        photo_aeriennes_checked = hasattr(self.dlg, 'chkPhotoAeriennes') and self.dlg.chkPhotoAeriennes.isChecked()
        bd_ortho_checked = hasattr(self.dlg, 'chkBDOrtho') and self.dlg.chkBDOrtho.isChecked()
        mnt_lidar_checked = hasattr(self.dlg, 'chkMNTLidar') and self.dlg.chkMNTLidar.isChecked()
        plan_ign_checked = hasattr(self.dlg, 'chkPlanIGN') and self.dlg.chkPlanIGN.isChecked()
        geofoncier_checked = hasattr(self.dlg, 'chkGeofoncier') and self.dlg.chkGeofoncier.isChecked()

        # La commune est obligatoire dès qu'une donnée nécessite un filtre géométrique BBOX
        needs_bbox = voirie_checked or voirie_dep_checked or osm_routes_checked or bdtopo_routesnom_checked or bdtopo_troncons_checked or magosm_checked
        if needs_bbox:
            commune_checked = True

        # Pour les données sans BBOX (WMS globaux, cadastre, BAN, MAJIC), forcer le
        # chargement de la commune pour le zoom uniquement si elle n'est pas déjà dans le projet
        needs_zoom = (cadastre_checked or ban_checked or filaires_bal_checked or majic_checked or
                      scan_etat_major_checked or scan_cassini_checked or scan50_1950_checked or
                      waze_tiles_checked or osmfr_checked or cosia_checked or
                      bd_ortho_checked or mnt_lidar_checked or plan_ign_checked or
                      geofoncier_checked or photo_aeriennes_checked)
        if needs_zoom and not needs_bbox:
            commune_layer_name = f"Commune {code_insee}"
            commune_already_loaded = any(
                lyr.name() == commune_layer_name
                for lyr in QgsProject.instance().mapLayers().values()
            )
            if not commune_already_loaded:
                commune_checked = True
        
        if not cadastre_checked and not commune_checked and not ban_checked and not filaires_bal_checked and not voirie_checked and not voirie_dep_checked and not osm_routes_checked and not magosm_checked and not bdtopo_routesnom_checked and not bdtopo_troncons_checked and not majic_checked and not scan_etat_major_checked and not scan_cassini_checked and not scan50_1950_checked and not waze_tiles_checked and not osmfr_checked and not cosia_checked and not photo_aeriennes_checked and not bd_ortho_checked and not mnt_lidar_checked and not plan_ign_checked and not geofoncier_checked:
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

        # Détecter si la commune peut être réutilisée depuis le projet
        # (needs_bbox a pu forcer commune_checked=True même si la case n'est pas cochée)
        commune_reuse = False
        if commune_checked and not self.dlg.chkCommune.isChecked():
            commune_layer_name = f"Commune {code_insee}"
            for lyr in QgsProject.instance().mapLayers().values():
                if isinstance(lyr, QgsVectorLayer) and lyr.name() == commune_layer_name and lyr.isValid():
                    commune_layer = lyr
                    commune_reuse = True
                    break

        # Déterminer les couches WMS globales déjà présentes (skip = pas de rechargement)
        skip_scan_etat_major = scan_etat_major_checked and self._layer_exists_by_name("Carte d'État-Major")
        skip_scan_cassini    = scan_cassini_checked    and self._layer_exists_by_name("Carte de Cassini")
        skip_scan50          = scan50_1950_checked     and self._layer_exists_by_name("SCAN 50\u00ae 1950")
        skip_waze            = waze_tiles_checked      and self._layer_exists_by_name("Waze")
        skip_osmfr           = osmfr_checked           and self._layer_exists_by_name("OSM France")
        skip_cosia           = cosia_checked           and self._group_exists_by_name("CoSIA (Couverture du Sol par IA)")
        skip_bdortho         = bd_ortho_checked        and self._layer_exists_by_name("BD ORTHO\u00ae 20 cm")
        skip_mntlidar        = mnt_lidar_checked       and self._layer_exists_by_name("MNT LiDAR HD")
        skip_planign         = plan_ign_checked        and self._layer_exists_by_name("PLAN IGN J+1")
        skip_geofoncier      = geofoncier_checked      and self._group_exists_by_name("G\u00e9ofoncier public")

        # Compter le nombre d'étapes pour la barre de progression
        # La commune n'est pas comptée si elle est réutilisée (pas de téléchargement)
        # Les WMS globaux déjà présents ne comptent pas non plus
        steps = sum([
            cadastre_checked, commune_checked and not commune_reuse, ban_checked,
            filaires_bal_checked,
            voirie_checked, voirie_dep_checked, osm_routes_checked, magosm_checked,
            bdtopo_routesnom_checked, bdtopo_troncons_checked, majic_checked,
            scan_etat_major_checked and not skip_scan_etat_major,
            scan_cassini_checked    and not skip_scan_cassini,
            scan50_1950_checked     and not skip_scan50,
            waze_tiles_checked      and not skip_waze,
            osmfr_checked           and not skip_osmfr,
            cosia_checked           and not skip_cosia,
            bd_ortho_checked        and not skip_bdortho,
            mnt_lidar_checked       and not skip_mntlidar,
            plan_ign_checked        and not skip_planign,
            geofoncier_checked      and not skip_geofoncier,
        ]) + sum(1 for _, dn in photo_aeriennes_sources if not self._layer_exists_by_name(dn))

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
            if commune_reuse:
                # Couche existante réutilisée, pas de téléchargement ni de comptage
                pass
            else:
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

        # ── Phase parallèle : téléchargement WFS concurrent ──────────────────────
        # Lecture des options de clip (nécessaires pour Phase 3)
        clip_to_commune = SettingsDialog.get('clip_to_commune', False, bool)
        clip_buffer_m = SettingsDialog.get('clip_buffer_m', 25, int)

        _BAN_REGEX_CHEMIN_DEFAULT = r'(?i)\b(?:ch(?:e(?:m(?:in(?:ement)?)?)?|in)?|sen(?:t(?:e|ier)?)?)\.?\s+r(?:u(?:r(?:al?e?)?)?|al|le)\b|\bC\.?R\.?\b'
        _BAN_REGEX_VOIE_DEFAULT   = r'(?i)\b(?:voi(?:e)?|ch(?:e(?:m(?:in(?:ement)?)?)?)?|rout(?:e)?)\.?\s+c(?:om(?:m(?:un(?:al?e?)?)?)?|al?e?|le)\b|\bV\.?C\.?\b'
        regex_chemin = self._get_regex_setting('ban_regex_chemin', _BAN_REGEX_CHEMIN_DEFAULT)
        regex_voie   = self._get_regex_setting('ban_regex_voie',   _BAN_REGEX_VOIE_DEFAULT)

        # Définir les specs de toutes les tâches WFS à lancer en parallèle.
        # Chaque spec : label, result_key, layer_name, fetch_fn, style_cb, needs_clip
        parallel_specs = []

        if ban_checked:
            parallel_specs.append({
                'label':      f"Adresses BAN ({code_insee})",
                'result_key': 'Adresses BAN',
                'layer_name': f"Adresses BAN {code_insee}",
                'fetch_fn':   lambda: self._fetch_wfs_paginated_to_vsimem(
                    self.WFS_IGN_URL, 'BAN.DATA.GOUV:ban',
                    cql_filter=f"code_insee='{code_insee}'"
                ),
                'style_cb':   lambda lyr: self.apply_ban_style(
                    lyr, regex_chemin=regex_chemin, regex_voie=regex_voie
                ),
                'needs_clip': False,
            })

        if voirie_checked:
            parallel_specs.append({
                'label':      f"Voirie communale ({code_insee})",
                'result_key': 'Voirie communale',
                'layer_name': f"DGCL Voirie communale retenue DSR 2026 {code_insee}",
                'fetch_fn':   lambda: self._fetch_wfs_bbox_to_vsimem(
                    self.WFS_IGN_URL, 'DGF_2026_:_voirie-retenue-communes', commune_bbox
                ),
                'style_cb':   None,
                'needs_clip': True,
            })

        if voirie_dep_checked:
            parallel_specs.append({
                'label':      f"Voirie départementale ({code_insee})",
                'result_key': 'Voirie départementale',
                'layer_name': f"DGCL Voirie départementale retenue DGF 2026 {code_insee}",
                'fetch_fn':   lambda: self._fetch_wfs_bbox_to_vsimem(
                    self.WFS_IGN_URL, 'DGF_2026_:_voirie-retenue-departements', commune_bbox
                ),
                'style_cb':   None,
                'needs_clip': True,
            })

        if osm_routes_checked:
            parallel_specs.append({
                'label':      f"Routes OSM ({code_insee})",
                'result_key': 'Routes OSM',
                'layer_name': f"OSM Routes {code_insee}",
                'fetch_fn':   lambda: self._fetch_osm_roads_to_vsimem(commune_bbox),
                'style_cb':   lambda lyr: self._style_osm_layer(lyr),
                'needs_clip': True,
            })

        if magosm_checked:
            parallel_specs.append({
                'label':      f"MagOSM Routes ({code_insee})",
                'result_key': 'Réseau routier OSM (MagOSM)',
                'layer_name': f"MagOSM Routes {code_insee}",
                'fetch_fn':   lambda: self._fetch_magosm_to_vsimem(commune_bbox),
                'style_cb':   lambda lyr: self._apply_magosm_style(
                    lyr, regex_chemin=regex_chemin, regex_voie=regex_voie
                ),
                'needs_clip': True,
            })

        if bdtopo_routesnom_checked:
            parallel_specs.append({
                'label':      f"BD TOPO Routes nommées ({code_insee})",
                'result_key': 'BD TOPO Routes numérotées ou nommées',
                'layer_name': f"BD TOPO Routes numérotées ou nommées {code_insee}",
                'fetch_fn':   lambda: self._fetch_wfs_bbox_to_vsimem(
                    self.WFS_IGN_URL, 'BDTOPO_V3:route_numerotee_ou_nommee', commune_bbox
                ),
                'style_cb':   lambda lyr: self._apply_bdtopo_routesnom_style(lyr),
                'needs_clip': True,
            })

        if bdtopo_troncons_checked:
            parallel_specs.append({
                'label':      f"BD TOPO Tronçons de route ({code_insee})",
                'result_key': 'BD TOPO Tronçons de route',
                'layer_name': f"BD TOPO Tronçons de route {code_insee}",
                'fetch_fn':   lambda: self._fetch_wfs_paginated_to_vsimem(
                    self.WFS_IGN_URL, 'BDTOPO_V3:troncon_de_route',
                    crs="EPSG:4326", bbox=commune_bbox
                ),
                'style_cb':   lambda lyr: self._apply_bdtopo_troncons_style(
                    lyr, regex_chemin=regex_chemin, regex_voie=regex_voie
                ),
                'needs_clip': True,
            })

        # Lancer toutes les tâches WFS en parallèle
        parallel_count = len(parallel_specs)
        tasks_done_count = [0]   # liste pour mutation dans closure
        task_objects = []

        # Boucle d'événements locale : se termine dès que toutes les tâches
        # sont terminées (signal taskDone), sans scruter activement (pas de
        # time.sleep) tout en gardant l'UI réactive.
        wait_loop = QEventLoop()

        def on_task_done(task):
            tasks_done_count[0] += 1
            advance(f"✓ {task.label} ({tasks_done_count[0]}/{parallel_count})")
            if tasks_done_count[0] >= parallel_count:
                wait_loop.quit()

        for spec in parallel_specs:
            task = WfsLoadTask(spec['label'], spec['fetch_fn'])
            task.taskDone.connect(on_task_done)
            task._spec = spec
            QgsApplication.taskManager().addTask(task)
            task_objects.append(task)

        # Attendre la fin de toutes les tâches (bloque uniquement s'il y en a)
        if parallel_count > 0:
            wait_loop.exec_()

        # ── Phase 3 : créer les couches sur le thread principal ───────────────
        deferred_warnings = []  # messages à afficher après progress.close()
        for task in task_objects:
            spec = task._spec
            if task.success and task.vsimem_path:
                ok, layer = self._make_layer_from_vsimem(
                    task.vsimem_path, spec['layer_name'], spec['style_cb']
                )
                results.append((spec['result_key'], ok))
                if layer:
                    if spec['needs_clip'] and clip_to_commune and commune_layer:
                        layer = self._clip_layer_to_commune(layer, commune_layer, clip_buffer_m)
                    loaded_layers.append(layer)
            else:
                results.append((spec['result_key'], False))
                if task.error_msg:
                    QgsMessageLog.logMessage(
                        f"✗ {spec['result_key']} : {task.error_msg}",
                        "VoirieCommunale", Qgis.Warning
                    )
                    if spec['result_key'] == 'Routes OSM' and task.error_msg == "Aucune route C/R trouvée":
                        deferred_warnings.append((
                            "Aucune route C/R",
                            "Aucune route avec un 'ref' commençant par C ou R n'a été trouvée."
                        ))

        if majic_checked:
            advance(f"Chargement des parcelles MAJIC ({code_insee})...")
            majic_success, majic_layer = self.load_majic_parcelles(code_insee)
            results.append(('Parcelles MAJIC', majic_success))
            if majic_layer:
                loaded_layers.append(majic_layer)
            elif not majic_success:
                deferred_warnings.append((
                    "Erreur MAJIC",
                    "Impossible de charger les parcelles MAJIC pour la commune sélectionnée.\n\n"
                    "Vérifiez la connexion internet, le code INSEE, ou consultez le journal des messages pour plus de détails."
                ))

        if filaires_bal_checked:
            advance(f"Chargement des filaires de voie BAL ({code_insee})...")
            filaires_bal_success, filaires_bal_layer, filaires_bal_no_data = self.load_filaires_bal(code_insee)
            results.append(('Filaires de voie BAL', filaires_bal_success))
            if filaires_bal_layer:
                loaded_layers.append(filaires_bal_layer)
            elif filaires_bal_no_data:
                deferred_warnings.append((
                    "Aucune donnée BAL",
                    "Aucun filaire de voie n'est disponible pour cette commune dans la Base "
                    "Adresse Locale.\n\nToutes les communes n'ont pas encore contribué à ce jeu de données."
                ))
            elif not filaires_bal_success:
                deferred_warnings.append((
                    "Erreur Filaires de voie BAL",
                    "Impossible de charger les filaires de voie BAL pour la commune sélectionnée.\n\n"
                    "Vérifiez la connexion internet, ou consultez le journal des messages pour plus de détails."
                ))

        if scan_etat_major_checked:
            if skip_scan_etat_major:
                results.append(("Carte d'État-Major", True))
                loaded_layers.extend(self._get_layers_by_name("Carte d'État-Major"))
            else:
                advance("Chargement Carte d'État-Major...")
                em_success, em_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.ETATMAJOR40', "Carte d'État-Major")
                results.append(("Carte d'État-Major", em_success))
                loaded_layers.extend(em_layers)

        if scan_cassini_checked:
            if skip_scan_cassini:
                results.append(('Carte de Cassini', True))
                loaded_layers.extend(self._get_layers_by_name('Carte de Cassini'))
            else:
                advance("Chargement Carte de Cassini...")
                cassini_success, cassini_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.CASSINI', 'Carte de Cassini')
                results.append(('Carte de Cassini', cassini_success))
                loaded_layers.extend(cassini_layers)

        if scan50_1950_checked:
            if skip_scan50:
                results.append(('SCAN 50\u00ae 1950', True))
                loaded_layers.extend(self._get_layers_by_name('SCAN 50\u00ae 1950'))
            else:
                advance("Chargement SCAN 50\u00ae 1950...")
                scan50_success, scan50_layers = self.load_scan_historique_wms('GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN50.1950', 'SCAN 50\u00ae 1950')
                results.append(('SCAN 50\u00ae 1950', scan50_success))
                loaded_layers.extend(scan50_layers)

        if waze_tiles_checked:
            if skip_waze:
                results.append(('Waze', True))
                loaded_layers.extend(self._get_layers_by_name('Waze'))
            else:
                advance("Chargement Waze...")
                waze_success, waze_layers = self.load_xyz_tile_layer(
                    'https://www.waze.com/row-tiles/editor/roads/{z}/{x}/{y}/tile.png',
                    'Waze', zmin=0, zmax=19
                )
                results.append(('Waze', waze_success))
                loaded_layers.extend(waze_layers)

        if osmfr_checked:
            if skip_osmfr:
                results.append(('OSM France', True))
                loaded_layers.extend(self._get_layers_by_name('OSM France'))
            else:
                advance("Chargement OSM France...")
                osmfr_success, osmfr_layers = self.load_xyz_tile_layer(
                    'https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
                    'OSM France', zmin=0, zmax=20
                )
                results.append(('OSM France', osmfr_success))
                loaded_layers.extend(osmfr_layers)

        if cosia_checked:
            if skip_cosia:
                results.append(('CoSIA', True))
                loaded_layers.extend(self._get_group_layers('CoSIA (Couverture du Sol par IA)'))
            else:
                advance("Chargement CoSIA (Couverture du Sol par IA)...")
                cosia_success, cosia_layers = self.load_cosia_wms()
                results.append(('CoSIA', cosia_success))
                loaded_layers.extend(cosia_layers)

        if bd_ortho_checked:
            if skip_bdortho:
                results.append(('BD ORTHO\u00ae 20 cm', True))
                loaded_layers.extend(self._get_layers_by_name('BD ORTHO\u00ae 20 cm'))
            else:
                advance("Chargement BD ORTHO\u00ae 20 cm...")
                bdortho_success, bdortho_layers = self._load_wms_layer('HR.ORTHOIMAGERY.ORTHOPHOTOS', 'BD ORTHO\u00ae 20 cm', 'EPSG:2154')
                results.append(('BD ORTHO\u00ae 20 cm', bdortho_success))
                loaded_layers.extend(bdortho_layers)

        if mnt_lidar_checked:
            if skip_mntlidar:
                results.append(('MNT LiDAR HD', True))
                loaded_layers.extend(self._get_layers_by_name('MNT LiDAR HD'))
            else:
                advance("Chargement MNT LiDAR HD...")
                mntlidar_success, mntlidar_layers = self._load_wms_layer('IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.SHADOW', 'MNT LiDAR HD', 'EPSG:4326')
                results.append(('MNT LiDAR HD', mntlidar_success))
                loaded_layers.extend(mntlidar_layers)

        if plan_ign_checked:
            if skip_planign:
                results.append(('PLAN IGN J+1', True))
                loaded_layers.extend(self._get_layers_by_name('PLAN IGN J+1'))
            else:
                advance("Chargement PLAN IGN J+1...")
                planign_success, planign_layers = self._load_wms_layer('GEOGRAPHICALGRIDSYSTEMS.MAPS.BDUNI.J1', 'PLAN IGN J+1', 'EPSG:3857')
                results.append(('PLAN IGN J+1', planign_success))
                loaded_layers.extend(planign_layers)

        if geofoncier_checked:
            if skip_geofoncier:
                results.append(('G\u00e9ofoncier public', True))
                loaded_layers.extend(self._get_group_layers('G\u00e9ofoncier public'))
            else:
                advance("Chargement G\u00e9ofoncier public...")
                geofoncier_success, geofoncier_layers = self.load_geofoncier_wms()
                results.append(('G\u00e9ofoncier public', geofoncier_success))
                loaded_layers.extend(geofoncier_layers)

        for typename, display_name in photo_aeriennes_sources:
            if self._layer_exists_by_name(display_name):
                results.append((display_name, True))
                loaded_layers.extend(self._get_layers_by_name(display_name))
            else:
                advance(f"Chargement {display_name}...")
                ph_success, ph_layers = self.load_scan_historique_wms(typename, display_name)
                results.append((display_name, ph_success))
                loaded_layers.extend(ph_layers)

        # Fermer la boîte de progression
        progress.setValue(steps)
        progress.close()

        # Afficher les avertissements différés (après fermeture de la progression)
        for title, msg in deferred_warnings:
            QMessageBox.warning(self.iface.mainWindow(), title, msg)

        # Récupérer le nom de la commune pour nommer le groupe
        commune_name = self._get_commune_name(code_insee, commune_layer)

        # Regrouper d'abord les couches spécifiques dans leur groupe commune
        self._group_commune_layers(code_insee, commune_name)

        # Puis réordonner les items à la racine (groupe commune + fonds de plan)
        if SettingsDialog.get('auto_reorder', True, bool):
            self._reorder_layers(code_insee)

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

        # Message récapitulatif de fin de chargement
        if len(results) >= 1:
            if success_count == len(results):
                if len(results) == 1:
                    source_name = results[0][0]
                    QMessageBox.information(
                        self.iface.mainWindow(),
                        "Chargement terminé",
                        f"{source_name} chargé avec succès pour le code INSEE {code_insee}."
                    )
                else:
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
            self.dlg = VoirieCommunaleDialog()
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

