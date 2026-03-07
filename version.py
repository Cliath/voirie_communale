# -*- coding: utf-8 -*-
"""
Version management for Voirie Communale plugin
"""


__version__ = "0.13.2"
__version_info__ = (0, 13, 2)

VERSION_HISTORY = {
    "0.12.3": {
        "date": "2026-03-07",
        "changes": [
            "Corrigé : validation des regex chemin/voie dans les Paramètres avant sauvegarde — message d'erreur explicite si invalide.",
        ]
    },
    "0.12.1": {
        "date": "2026-03-07",
        "changes": [
            "Corrigé : clip par emprise communale — couche mémoire invalide car geometryDisplayString() retourne 'Line' au lieu de 'LineString'. Corrigé avec QgsWkbTypes.displayString(layer.wkbType()).",
        ]
    },
    "0.12.0": {
        "date": "2026-03-07",
        "changes": [
            "Ajouté : option 'Découper les couches sur l'emprise communale' dans les Paramètres, avec buffer configurable (0–10 000 m, défaut 25 m).",
            "Ajouté : méthode _clip_layer_to_commune() — filtre les entités BBOX par intersection avec le buffer communal (calcul métrique en EPSG:2154).",
        ]
    },
    "0.9.74": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : suppression des mentions de licence dans les libellés des cases à cocher du dialogue."
        ]
    },
    "0.9.73": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : 'Photographies aériennes historiques' converti en case à cocher intégrée dans Tout sélectionner ; le dialogue de sélection des périodes s'ouvre lors du clic sur Charger les données."
        ]
    },
    "0.9.72": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : 5 nouvelles périodes de photographies aériennes (2000-2005, 2006-2010, 2011-2015, 2016-2020, 2021-2023) dans le dialogue Photos aériennes historiques."
        ]
    },
    "0.9.71": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : bouton 'Photographies aériennes historiques...' dans Plans à charger, ouvre un dialogue de sélection (1950-1965, 1965-1980, 1980-1995) depuis la Géoplateforme IGN."
        ]
    },
    "0.9.70": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : couche OSM renommée 'OSM Routes {code_insee}' (suppression du suffixe '(C/R)')."
        ]
    },
    "0.9.69": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : Waze placée au-dessus de Cadastre dans l'ordre canonique des couches."
        ]
    },
    "0.9.68": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : ordre canonique des couches — Parcelles MAJIC placées entre Adresses BAN et Commune."
        ]
    },
    "0.9.67": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : réordonnancement automatique des couches après chargement selon un ordre canonique (vecteurs détaillés → emprise → cadastre → rasters historiques → tuiles), quelle que soit l'ordre de sélection des cases."
        ]
    },
    "0.9.66": {
        "date": "2026-03-01",
        "changes": [
            "Corrigé : recherche de la couche Commune dans le projet utilise désormais une égalité exacte (==) au lieu de startswith, évitant les faux positifs en cas de plusieurs couches similaires."
        ]
    },
    "0.9.65": {
        "date": "2026-03-01",
        "changes": [
            "Corrigé : zoom post-chargement ne fonctionnait pas quand seule une couche tuile (Waze/WMS global) était cochée sans commune — on cherche désormais une couche Commune existante dans le projet avant de recourir à zoomToFullExtent."
        ]
    },
    "0.9.64": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : case 'Tuiles Waze Editor' renommée en 'Waze'."
        ]
    },
    "0.9.63": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : case Tuiles Waze Editor (XYZ) dans Plans à charger. Nouvelle méthode générique load_xyz_tile_layer()."
        ]
    },
    "0.9.62": {
        "date": "2026-03-01",
        "changes": [
            "Supprimé : case Surfaces non agricoles RPG (SNA) — source non disponible, surchargement inutile."
        ]
    },
    "0.9.61": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : SCAN 50\u00ae 1950 (GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN50.1950) dans Plans à charger."
        ]
    },
    "0.9.60": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : deux cases \"Plans à charger\" \u2014 Carte d'\u00c9tat-Major IGN (1820-1866) et Carte de Cassini (XVIIIe siècle) via WMS Géoplateforme IGN."
        ]
    },
    "0.9.59": {
        "date": "2026-03-01",
        "changes": [
            "Déplacé : 'Tout sélectionner / Désélectionner' placé au-dessus du label 'Données à charger'."
        ]
    },
    "0.9.58": {
        "date": "2026-03-01",
        "changes": [
            "Déplacé : la case Cadastre est maintenant dans la section 'Plans à charger' plutôt que 'Données à charger'."
        ]
    },
    "0.9.57": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : section 'Plans à charger' dans la boîte de dialogue."
        ]
    },
    "0.9.56": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : TODO.md n'est plus stocké dans le dossier du plugin (qui est écrasé à chaque mise à jour) mais dans le profil utilisateur QGIS (QgsApplication.qgisSettingsDirPath()/chemins_ruraux/TODO.md)."
        ]
    },
    "0.9.55": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : suppression automatique des doublons de couches — si une couche du même nom (même commune) existe déjà dans le projet, elle est retirée avant le rechargement."
        ]
    },
    "0.9.54": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : le zoom après chargement se fait désormais sur l'emprise de la commune plutôt que sur l'emprise combinée de toutes les couches."
        ]
    },
    "0.9.53": {
        "date": "2026-03-01",
        "changes": [
            "Modifié : ToDo ouvre désormais une fenêtre QGIS intégrée (QDialog) avec éditeur et bouton Enregistrer plutôt que l'éditeur système."
        ]
    },
    "0.9.52": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : entrée de menu 'ToDo' (Extensions → Voirie Communale → ToDo) ouvrant TODO.md dans l'éditeur système."
        ]
    },
    "0.9.51": {
        "date": "2026-03-01",
        "changes": [
            "Déplacé : menu du plugin de Vecteur vers Extensions (addPluginToMenu)."
        ]
    },
    "0.9.50": {
        "date": "2026-03-01",
        "changes": [
            "Supprimé : catégorie 'Autre' inutile dans le renderer OSM (les tronçons sont déjà filtrés à la source sur C/R)."
        ]
    },
    "0.9.49": {
        "date": "2026-03-01",
        "changes": [
            "Corrigé : AttributeError 'QgsRectangle' has no attribute '__ior__' — remplacé par combineExtentWith()."
        ]
    },
    "0.9.48": {
        "date": "2026-03-01",
        "changes": [
            "Corrigé : libellés de catégorisation OSM — C = Voie communale, R = Chemin rural, CE = Chemin d'exploitation."
        ]
    },
    "0.9.47": {
        "date": "2026-03-01",
        "changes": [
            "Corrigé : catégorisation OSM (CE/C/R) échouait pour les tronçons sans ref direct mais appartenant à une relation référencée — le champ ref utilise maintenant chosen_ref (ref direct sinon ref de la relation)."
        ]
    },
    "0.9.46": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : barre de progression (QProgressDialog) affichée après 1,5 s de téléchargement, avec label mis à jour pour chaque source."
        ]
    },
    "0.9.45": {
        "date": "2026-03-01",
        "changes": [
            "SNA RPG : flux WFS non disponible sur la G\u00e9oplateforme IGN — la case reste pr\u00e9sente mais affiche un message d'information."
        ]
    },
    "0.9.44": {
        "date": "2026-03-01",
        "changes": [
            "Ajouté : Nouvelle source de données Surfaces non agricoles RPG (RPG.LATEST:SNA, WFS IGN Géoplateforme), filtrée sur l'emprise communale, rendu orange semi-transparent."
        ]
    },
    "0.9.43": {
        "date": "2026-03-01",
        "changes": [
            "Correction : case 'Routes numérotées ou nommées (BD TOPO)' manquante dans le groupe Tout sélectionner/Désélectionner."
        ]
    },
    "0.9.42": {
        "date": "2026-02-28",
        "changes": [
            "Mise à jour technique : incrémentation automatique de version, workflow automatisé (test)."
        ]
    },
    "0.9.41": {
        "date": "2026-02-25",
        "changes": [
            "Ajouté : Affichage d'un avertissement à l'utilisateur (QMessageBox.warning) en cas d'échec du chargement MAJIC (personnes morales)."
        ]
    },
    "0.9.35": {
        "date": "2026-02-23",
        "changes": [
            "Ajouté: Affichage explicite des licences de chaque source de données dans le menu et la boîte de dialogue À propos (Licence Ouverte 2.0, ODbL, etc.)."
        ]
    },
    "0.9.34": {
        "date": "2026-02-23",
        "changes": [
            "Corrigé: libellés des codes AU* dans le dictionnaire MAJIC_FORMES_JURIDIQUES (AUDA=Autre administration, AUDP=Autre de droit privé, AUEP=Autre entité publique, AUPE=Autre personne étrangère, AURS=Autre à régime spécial, AUTA=Autre titre administratif, AUTC=Autre titre collectif)"
        ]
    },
    "0.9.33": {
        "date": "2026-02-23",
        "changes": [
            "Modifié: couche MAJIC — catégorisation basée sur groupe_personne (10 groupes) "
            "avec les couleurs exactes de l'application Koumoul (référence officielle DGFiP)"
        ]
    },
    "0.9.32": {
        "date": "2026-02-23",
        "changes": [
            "Modifié: couche MAJIC — rendu catégorisé avec palette de couleurs fixe et stables par forme juridique. "
            "Libellés complets dans la légende (ex: 'Société anonyme' au lieu de 'SA'). "
            "Couleurs sémantiques groupées par type (public, associations, agricole, commercial...)"
        ]
    },
    "0.9.31": {
        "date": "2026-02-23",
        "changes": [
            "Ajouté: rendu catégorisé QGIS sur l'attribut forme_juridique pour la couche MAJIC "
            "(couleurs HSV distinctes par forme juridique abrégée)"
        ]
    },
    "0.9.30": {
        "date": "2026-02-22",
        "changes": [
            "Modifié: couche MAJIC passe de points (centroïdes) à polygones "
            "— les géométries sont désormais issues du WFS IGN Géoplateforme "
            "(CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle), jointes par idu=code_parcelle"
        ]
    },
    "0.9.29": {
        "date": "2026-02-22",
        "changes": [
            "Corrigé: MAJIC HTTP 400 — (1) filtre corrigé en qs=code_commune:INSEE (syntaxe Elasticsearch Data Fair), (2) pagination skip remplacée par curseur after"
        ]
    },
    "0.9.28": {
        "date": "2026-02-22",
        "changes": [
            "Corrigé: MAJIC HTTP 400 — remplacement de '_parcelle_coords.coord' (point interdit) par '_geopoint', et pagination 'skip' remplacée par curseur 'after'"
        ]
    },
    "0.9.27": {
        "date": "2026-02-22",
        "changes": [
            "Ajouté: couche Parcelles personnes morales (MAJIC) via API REST Koumoul (DGFiP)"
        ]
    },
    "0.9.26": {
        "date": "2026-02-22",
        "changes": [
            "Simplifié: chkToutSelectionner sans tristate — comportement binaire simple coché/décoché"
        ]
    },
    "0.9.25": {
        "date": "2026-02-22",
        "changes": [
            "Corrigé: état partiel de chkToutSelectionner non fonctionnel — signal 'clicked' utilisé à la place de 'stateChanged' pour éviter le cycle tristate 0→1→2"
        ]
    },
    "0.9.24": {
        "date": "2026-02-22",
        "changes": [
            "Ajouté: case à cocher 'Tout sélectionner / Désélectionner' pour basculer toutes les couches en une action"
        ]
    },
    "0.9.23": {
        "date": "2026-02-22",
        "changes": [
            "Corrigé: champ géométrie BD TOPO troncon_de_route ('geometrie' et non 'geom')",
            "Ajouté: paramètre geom_field dans load_wfs_layer pour gérer les champs géométrie variés"
        ]
    },
    "0.9.22": {
        "date": "2026-02-22",
        "changes": [
            "Ajout\u00e9: couche BD TOPO tron\u00e7ons_de_route (WFS G\u00e9oplateforme IGN, filtr\u00e9 par BBOX commune)"
        ]
    },
    "0.9.21": {
        "date": "2026-02-22",
        "changes": [
            "Ajout\u00e9: bo\u00eete de dialogue '\u00c0 propos' dans le menu du plugin (version, auteur, lien GitHub)"
        ]
    },
    "0.9.20": {
        "date": "2026-02-22",
        "changes": [
            "Corrigé: renommage exhaustif du plugin en 'Voirie Communale' (releases/README.md, compile_plugin.py, compile_simple.py, QUICKSTART.md, chemins_ruraux.py message de log)"
        ]
    },
    "0.9.19": {
        "date": "2026-02-22",
        "changes": [
            "Modifié: le plugin est renommé 'Voirie Communale' — recensement des voies communales et chemins ruraux"
        ]
    },
    "0.9.18": {
        "date": "2026-02-22",
        "changes": [
            "Optimisation: suppression imports inutilisés (QgsDataSourceUri, QgsSymbol, tempfile)",
            "Optimisation: suppression self.temp_files inutilisé",
            "Optimisation: suppression paramètres show_wait_message de load_wfs_layer",
            "Optimisation: logs verbeux de la boucle zoom supprimés",
            "Corrigé: bug label_settings.fieldName assigné 3 fois dans apply_ban_style",
            "Nettoyage: en-têtes boilerplate remplacés, first_start == True simplifié"
        ]
    },
    "0.9.17": {
        "date": "2026-02-22",
        "changes": [
            "Modifié: renommage des couches voirie - 'DGCL Voirie communale retenue DSR 2025 INSEE' et 'DGCL Voirie départementale retenue DGF 2025 INSEE'"
        ]
    },
    "0.9.16": {
        "date": "2026-02-22",
        "changes": [
            "Modifié: renommage des couches voirie - 'Voirie communale pour calcul DSR INSEE' et 'Voirie départementale pour calcul DGF INSEE'"
        ]
    },
    "0.9.15": {
        "date": "2026-02-18",
        "changes": [
            "Corrigé: champs définis dans l'URI de la couche mémoire (field=ref:string&...) au lieu de addAttributes - setAttribute fonctionne désormais"
        ]
    },
    "0.9.14": {
        "date": "2026-02-18",
        "changes": [
            "Corrigé: KeyError 'ref' - utilisation de feat[index] au lieu de feat.setAttribute(nom)"
        ]
    },
    "0.9.13": {
        "date": "2026-02-18",
        "changes": [
            "Corrigé: setAttribute par nom au lieu de setAttributes en liste positionnelle (champ ref vide)"
        ]
    },
    "0.9.12": {
        "date": "2026-02-18",
        "changes": [
            "Ajouté: style catégorisé CE (vert) / C (orange) / R (rouge) pour la couche OSM",
            "Ajouté: étiquettes avec le champ 'ref' sur les routes OSM"
        ]
    },
    "0.9.11": {
        "date": "2026-02-18",
        "changes": [
            "Corrigé: Overpass 'out body;>;out body geom;' remplace par 'out geom;' pour avoir la géométrie inline dans les ways"
        ]
    },
    "0.9.10": {
        "date": "2026-02-18",
        "changes": [
            "Corrigé: DeprecationWarning QgsField - suppression de QVariant.String"
        ]
    },
    "0.9.9": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Indentation invalide dans le chargement OSM"
        ]
    },
    "0.9.8": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Correction du filtre OSM ref C/R (erreur matched_count)"
        ]
    },
    "0.9.7": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Filtre OSM ref C/R via JSON Overpass et couche mémoire"
        ]
    },
    "0.9.6": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Filtre OSM ref avec propagation des refs de relations"
        ]
    },
    "0.9.5": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Filtre OSM ref appliqué localement après téléchargement"
        ]
    },
    "0.9.4": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Filtre OSM ref via relations route + voies associées"
        ]
    },
    "0.9.3": {
        "date": "2026-02-17",
        "changes": [
            "Corrigé: Filtre OSM ref via relations route=road + voies associées"
        ]
    },
    "0.9.2": {
        "date": "2026-02-17",
        "changes": [
            "Ajusté: Filtre OSM routes avec ref commençant par C ou R"
        ]
    },
    "0.9.1": {
        "date": "2026-02-17",
        "changes": [
            "Ajusté: Téléchargement des routes OSM sans filtres highway/surface"
        ]
    },
    "0.9.0": {
        "date": "2026-02-17",
        "changes": [
            "Ajout: Téléchargement des routes OSM via Overpass avec filtres highway/surface"
        ]
    },
    "0.8.12": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Utilisation de CQL_FILTER BBOX(geom,...) au lieu du paramètre bbox pour filtrage spatial"
        ]
    },
    "0.8.11": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Utilisation du format URL standard WFS au lieu du format provider pour le BBOX"
        ]
    },
    "0.8.10": {
        "date": "2026-02-14",
        "changes": [
            "Test: Format BBOX sans préfixe CRS: (bbox=xmin,ymin,xmax,ymax,EPSG:4326)"
        ]
    },
    "0.8.9": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Préfixe CRS: requis dans le format BBOX (bbox=xmin,ymin,xmax,ymax,CRS:EPSG:4326)"
        ]
    },
    "0.8.8": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Format BBOX dans l'URI WFS doit inclure le CRS (bbox=xmin,ymin,xmax,ymax,CRS:EPSG:4326)"
        ]
    },
    "0.8.7": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Recherche d'une couche commune existante dans le projet avant d'en charger une nouvelle pour le BBOX des voiries"
        ]
    },
    "0.8.6": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Deux formats d'URI WFS selon le type de filtre (CQL_FILTER vs BBOX)"
        ]
    },
    "0.8.5": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Format URI WFS pour que le filtre BBOX soit respecté par QGIS",
            "Corrigé: Utilisation de restrictToRequestBBOX=1 pour forcer le filtrage spatial"
        ]
    },
    "0.8.4": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Évite le chargement en double de la commune pour le BBOX voirie"
        ]
    },
    "0.8.3": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Chargement voirie avec filtre BBOX au lieu de code_insee",
            "Amélioré: load_wfs_layer() supporte maintenant filtres CQL et BBOX",
            "Corrigé: Chargement automatique de la commune si nécessaire pour BBOX voirie"
        ]
    },
    "0.8.2": {
        "date": "2026-02-14",
        "changes": [
            "Supprimé: Message d'attente lors du chargement de la BAN"
        ]
    },
    "0.8.1": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Tooltips voirie avec la source correcte (calcul IGN pour la DGCL)"
        ]
    },
    "0.8.0": {
        "date": "2026-02-14",
        "changes": [
            "Ajout: Nouvelle source de données WFS - Voirie départementale (DGCL.2025:voirie_departementale)",
            "Amélioré: Checkbox pour sélectionner la voirie départementale"
        ]
    },
    "0.7.0": {
        "date": "2026-02-14",
        "changes": [
            "Ajout: Nouvelle source de données WFS - Voirie communale (DGCL.2025:voirie_communale)",
            "Amélioré: Interface avec checkbox pour sélectionner la voirie communale"
        ]
    },
    "0.6.16": {
        "date": "2026-02-14",
        "changes": [
            "Optimisation: URL WFS IGN mutualisée (constante WFS_IGN_URL)",
            "Nettoyage: Suppression de l'URL redondante /wfs/ows"
        ]
    },
    "0.6.15": {
        "date": "2026-02-14",
        "changes": [
            "Refactorisation: Méthode générique load_wfs_layer() pour réduire la duplication de code",
            "Amélioré: Code plus maintenable pour l'ajout de nouvelles sources WFS"
        ]
    },
    "0.6.14": {
        "date": "2026-02-14",
        "changes": [
            "Amélioré: Catégorie 'Autre' désactivée par défaut dans la légende BAN"
        ]
    },
    "0.6.13": {
        "date": "2026-02-14",
        "changes": [
            "Amélioré: Étiquettes BAN affichées uniquement sur chemins ruraux et voies communales"
        ]
    },
    "0.6.12": {
        "date": "2026-02-14",
        "changes": [
            "Corrigé: Placement des étiquettes BAN (AroundPoint au lieu de OverPoint)"
        ]
    },
    "0.6.11": {
        "date": "2026-02-14",
        "changes": [
            "Amélioré: Nouveau logo du plugin"
        ]
    },
    "0.3.1": {
        "date": "2026-01-27",
        "changes": [
            "Correction: Utilisation de ADMINEXPRESS.LATEST au lieu de ADMINEXPRESS-COG-CARTO.LATEST",
            "Amélioration: Couche commune correcte pour le WFS IGN"
        ]
    },
    "0.3.0": {
        "date": "2026-01-27",
        "changes": [
            "Ajout: Chargement automatique de l'emprise communale via WFS Admin Express IGN",
            "Ajout: Zoom automatique sur l'emprise de la commune",
            "Amélioration: Intégration des données Géoplateforme IGN"
        ]
    },
    "0.2.9": {
        "date": "2026-01-27",
        "changes": [
            "Correction: Le dialogue principal revient au premier plan après les messages de succès/erreur",
            "Amélioration: Meilleure gestion du focus après QMessageBox"
        ]
    },
    "0.2.8": {
        "date": "2026-01-27",
        "changes": [
            "Correction: Le dialogue existant est ramené au premier plan au lieu de créer une nouvelle fenêtre",
            "Ajout: raise_() et activateWindow() pour gérer le focus correctement"
        ]
    },
    "0.2.7": {
        "date": "2026-01-25",
        "changes": [
            "Amélioration: Dialogue non-modal (reste ouvert après chargement du cadastre)",
            "Suppression de exec_() pour permettre des chargements multiples"
        ]
    },
    "0.2.6": {
        "date": "2026-01-25",
        "changes": [
            "Correction: IndentationError à la ligne 354",
            "Correction: Suppression des lignes orphelines du code"
        ]
    },
    "0.2.5": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Suppression du code utilisant mMapLayerComboBox (erreur AttributeError)",
            "Correction: Le bouton OK ferme maintenant correctement le dialogue"
        ]
    },
    "0.2.4": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Suppression du widget 'Couche de chemins' inutilisé",
            "Nettoyage: Simplification de l'interface"
        ]
    },
    "0.2.3": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Validation réelle des codes INSEE français (métropole, Corse, DOM-TOM)",
            "Correction: Support des codes Corse (2A, 2B)",
            "Correction: Support des codes DOM-TOM (971-976, 984-988)",
            "Correction: Remplacement de la regex inutile de 0.2.2 par une vraie validation"
        ]
    },
    "0.2.2": {
        "date": "2026-01-25",
        "changes": [
            "Amélioration: Validation du code INSEE avec regex (^\\d{5}$)",
            "Amélioration: Validation plus robuste et explicite"
        ]
    },
    "0.2.1": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Suppression des cases à cocher de l'interface utilisateur",
            "Correction: Simplification de l'interface (un seul bouton)"
        ]
    },
    "0.2.0": {
        "date": "2026-01-25",
        "changes": [
            "Amélioration: Chargement automatique de toutes les couches cadastrales disponibles",
            "Amélioration: Organisation des couches dans un groupe nommé 'Cadastre - {INSEE}'",
            "Ajout: 7 nouvelles couches (lieux-dits, amorces, clôtures, détails topo, hydro, voies, bornes)",
            "Suppression: Cases à cocher de sélection des couches (chargement complet automatique)"
        ]
    },
    "0.1.2": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Noms de couches WMS conformes au service INSPIRE",
            "Correction: CP.CadastralParcel au lieu de CADASTRALPARCELS.PARCELLAIRE_EXPRESS",
            "Correction: BU.Building au lieu de BUILDINGS.BUILDINGS",
            "Correction: SUBFISCAL au lieu de CADASTRALPARCELS.PARCELS"
        ]
    },
    "0.1.1": {
        "date": "2026-01-25",
        "changes": [
            "Correction: Utilisation du fichier UI compilé au lieu du fichier source",
            "Amélioration: Gestion d'erreur détaillée pour le chargement WMS",
            "Amélioration: Logs détaillés dans le journal des messages",
            "Amélioration: Messages d'erreur explicites avec instructions de diagnostic"
        ]
    },
    "0.1.0": {
        "date": "2026-01-25",
        "changes": [
            "Intégration du flux WMS cadastre INSPIRE (DGFiP)",
            "Champ de saisie pour le code INSEE",
            "Sélection des couches cadastrales (parcelles, bâtiments, sections)",
            "Validation du code INSEE",
            "Documentation complète"
        ]
    },
    "0.0.1": {
        "date": "2026-01-25",
        "changes": [
            "Initialisation du projet",
            "Structure de base du plugin"
        ]
    }
}

def get_version():
    """Retourne la version actuelle du plugin"""
    return __version__

def get_version_info():
    """Retourne les informations de version sous forme de tuple"""
    return __version_info__

def get_changelog(version=None):
    """
    Retourne le changelog pour une version spécifique ou toutes les versions
    
    :param version: Version spécifique (ex: "0.1.0") ou None pour tout l'historique
    :return: Dict avec les informations de changement
    """
    if version:
        return VERSION_HISTORY.get(version, {})
    return VERSION_HISTORY
