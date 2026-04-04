# Voirie Communale - Plugin QGIS

Plugin QGIS pour le recensement de la voirie communale (voies communales et chemins ruraux).  
Version actuelle : **0.15.13** — voir [CHANGELOG](CHANGELOG.md)

## Installation

### Depuis un ZIP

1. Récupérez le ZIP depuis le dépôt ou via `build.bat` (dossier `releases/`)
2. QGIS → **Extensions** → **Installer/Gérer les extensions** → onglet **Installer depuis un ZIP**
3. Sélectionnez le fichier `voirie_communale-X.X.X.zip` et cliquez sur **Installer l'extension**
4. Activez le plugin dans l'onglet **Installées**

### En mode développement

```powershell
# Déployer manuellement dans le répertoire des plugins QGIS
$pluginDir = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\voirie_communale"
if (Test-Path $pluginDir) { Remove-Item -Recurse -Force $pluginDir }
Copy-Item -Recurse -Force <dossier_du_dépôt> $pluginDir
```

Ou via `build.bat` qui compile, package, push git et déploie en une commande :

```powershell
.\build.bat patch   # patch version (0.0.X)
.\build.bat minor   # minor version (0.X.0)
.\build.bat major   # major version (X.0.0)
```

## Fonctionnalités

### Interface

- **Barre de lancement** : le bouton du plugin ouvre 5 actions : *Charger des données*, *Numériser des données* (à venir), *Liste des tâches*, *Paramètres*, *À propos*
- **Mémorisation** : dernier code INSEE et sélection des couches restaurés automatiquement à l'ouverture
- **Paramètres** : zoom automatique, réordonnancement automatique, regex de filtrage des voies, et ordre des couches configurable par glisser-déposer
- **Ordre canonique** configurable via `layer_order.json` (haut → bas) : BD TOPO Tronçons → BD TOPO Routes → Voirie comm. → Voirie dép. → OSM Routes → MagOSM Routes → BAN → MAJIC → Commune → Cadastre → Géofoncier → PLAN IGN → Waze → OSM France → CoSIA → BD ORTHO® → Photos aériennes → SCAN 50® → Cassini → État-Major

### Données vectorielles (filtrées par code INSEE ou BBOX communale)

| Couche | Source | Filtre |
|--------|--------|--------|
| **Emprise communale** | IGN Géoplateforme WFS — Admin Express | code INSEE |
| **Adresses BAN** (paginée, toutes adresses) | IGN Géoplateforme WFS | code INSEE |
| **Voirie communale DGCL 2025** | IGN Géoplateforme WFS | BBOX commune |
| **Voirie départementale DGCL 2025** | IGN Géoplateforme WFS | BBOX commune |
| **Routes OSM** (CE / C / R) | Overpass API | BBOX commune |
| **Réseau routier OSM MagOSM** (paginé) | MagOSM WFS — Magellium | BBOX commune |
| **BD TOPO routes nommées** | IGN Géoplateforme WFS | BBOX commune |
| **BD TOPO tronçons de route** (paginé) | IGN Géoplateforme WFS | BBOX commune |
| **Parcelles MAJIC** (personnes morales) | API Koumoul (DGFiP) + IGN WFS | code INSEE |

#### BD TOPO tronçons de route — style par règles

Le style utilise un `QgsRuleBasedRenderer` avec la chaîne de priorité suivante :

1. **Regex sur `nom_collaboratif_gauche`** (paramétrable dans les Paramètres)
   - *Chemin rural (nom)* → `#8C7274` — déclenche aussi si `cpx_classement_administratif = 'Chemin rural'`
   - *Voie communale (nom)* → `#FCF6B5`
2. **Catégories sémantiques** (cpx / importance / nature, par ordre de priorité)

| Catégorie | Condition | Couleur |
|-----------|-----------|---------|
| Autoroute | cpx=Autoroute ou importance=1 | `#f26119` |
| Nationale | cpx=Nationale ou importance=2 | `#f2a824` |
| Départementale | cpx=Départementale ou importance=3 | `#F2D7A2` |
| Route intercommunale | cpx=Route intercommunale | `#2db9fc` |
| Liaison locale | importance=4 (sans cpx) | `#FCF0A8` |
| Desserte | importance≥5 (sans cpx) + nature Route 1/2 chaussées ou Rond-point | `#ededed` |
| Route empierrée | importance≥5 (sans cpx) + nature=Route empierrée | `#7C7C7C` |
| Chemin | importance≥5 (sans cpx) + nature=Chemin | `#8C7274` |
| Sentier | importance≥5 (sans cpx) + nature=Sentier | `#8C7274` (pointillés) |
| Bac / Maritime | importance≥5 (sans cpx) + nature=Bac ou liaison maritime | `#5792C2` |

#### Routes OSM — catégorisation par `ref`

- 🟢 **CE** – Chemin d'exploitation (`ref` commence par `CE`)
- 🟠 **C** – Voie communale (`ref` commence par `C`, hors `CE`)
- 🔴 **R** – Chemin rural (`ref` commence par `R`)

#### Adresses BAN — style par règles

Le style utilise un `QgsRuleBasedRenderer` sur le champ `nom_voie` :

| Catégorie | Condition | Couleur marqueur |
|-----------|-----------|------------------|
| Chemin rural | regex chemin rural sur `nom_voie` | `#8C7274` |
| Voie communale | regex voie communale sur `nom_voie` | `#B4B4B4` |
| Autre | (tout le reste, désactivé par défaut) | `#808080` |

L'étiquette affiche `numero + nom_voie`.

#### Réseau routier OSM MagOSM — style par règles

Le style utilise un `QgsRuleBasedRenderer` sur la couche `magosm:highways_line` :

1. **Regex sur `name`** (paramétrable) – *Chemin rural (nom)* `#8C7274` et *Voie communale (nom)* `#FCF6B5`
2. **Catégorisation par `highway`** :

| Catégorie | Valeurs `highway` | Couleur |
|-----------|-------------------|---------|
| Autoroute | motorway, motorway_link | `#f26119` |
| Nationale | trunk, primary (+ _link) | `#f2a824` |
| Départementale | secondary, secondary_link | `#F2D7A2` |
| Route intercommunale | tertiary, tertiary_link | `#2db9fc` |
| Desserte | residential, service, living_street | `#ededed` |
| Chemin | track, path, bridleway | `#8C7274` |
| Sentier | footway, steps | `#8C7274` (pointillés) |
| Piste cyclable | cycleway | `#9B5CCC` |
| (autre) | unclassified, … | `#969696` |

Service parfois lent — timeout 180 s par page, pagination 500 entités/page.

### Plans de fond

| Plan | Source |
|------|--------|
| **Cadastre** (10 couches) | DGFiP — WMS INSPIRE |
| **Plan IGN J+1** | IGN Géoplateforme WMS |
| **Waze** | Tuiles XYZ Waze |
| **OSM France** | Tuiles XYZ openstreetmap.fr |
| **CoSIA** (3 millésimes : 2017–2020, 2021–2023, 2024–2026) | IGN Géoplateforme WMS |
| **BD ORTHO® 20 cm** | IGN Géoplateforme WMS |
| **Photos aériennes historiques** (8 périodes 1950–2023) | IGN Géoplateforme WMS |
| **SCAN 50® 1950** | IGN Géoplateforme WMS |
| **Carte de Cassini** | IGN Géoplateforme WMS |
| **Carte de l'État-Major** | IGN Géoplateforme WMS |
| **MNT LiDAR HD** | IGN Géoplateforme WMS |
| **Géofoncier public** (RFU + Plans d'alignement, 5 couches) | Géofoncier — WMS public |

## Utilisation

1. Cliquez sur l'icône **Voirie Communale** dans la barre d'outils
2. Cliquez sur **Charger des données**
3. Saisissez le **code INSEE** de la commune (5 chiffres, ex : `57150`)
4. Cochez les couches souhaitées
5. Cliquez sur **Charger les données**

Les couches nécessitant un filtre géographique (Voirie DGCL, OSM Routes, BD TOPO) chargent automatiquement l'emprise communale en premier pour délimiter la zone de requête. La BAN et les tronçons BD TOPO utilisent une pagination automatique (1 000 entités par page) pour contourner la limite serveur de la Géoplateforme IGN.

## Structure du projet

```
voirie_communale/
├── __init__.py                      # Point d'entrée du plugin
├── voirie_communale.py                # Classe principale (logique métier)
├── voirie_communale_dialog.py         # Dialogues (LauncherDialog, VoirieCommunaleDialog, SettingsDialog…)
├── voirie_communale_dialog_base.ui    # Interface Qt Designer
├── voirie_communale_dialog_base.py    # [généré] Compilé depuis le .ui
├── resources.qrc                    # Ressources Qt (icônes)
├── resources.py                     # [généré] Compilé depuis resources.qrc
├── layer_order.json                 # Ordre canonique des couches (modifiable sans recompiler)
├── version.py                       # Version courante
├── metadata.txt                     # Métadonnées QGIS
├── CHANGELOG.md                     # Historique détaillé
├── build.bat                        # Build complet (compile + ZIP + git + déploiement)
├── bump_version.py                  # Incrémentation automatique de version
├── compile_plugin.py                # Compilation UI et ressources
├── get_commit_message.py            # Extraction du message de commit depuis CHANGELOG
├── package.py                       # Création du ZIP
└── releases/                        # Packages ZIP (ignorés par git)
```

## Développement

### Prérequis

- QGIS 3.0+
- Python 3.6+, PyQt5, `pyuic5`, `pyrcc5`
- Git (GitHub Desktop ou autre)

### Sources de données

| Service | URL |
|---------|-----|
| IGN Géoplateforme WFS | `https://data.geopf.fr/wfs` |
| IGN Géoplateforme WMS | `https://data.geopf.fr/wms/r` |
| Cadastre INSPIRE DGFiP | `https://inspire.cadastre.gouv.fr/scpc/{codeINSEE}.wms` |
| Overpass API (OSM) | `https://overpass-api.de/api/interpreter` |
| MagOSM WFS (Magellium) | `https://magosm.magellium.com/geoserver/ows` |
| API Koumoul (MAJIC) | `https://koumoul.com/data-fair/api/v1/datasets/parcelles-des-personnes-morales` |
| Géofoncier WMS public | `https://api2.geofoncier.fr/api/referentielsoge/wxs` |

## Licence

GNU General Public License v2.0 ou ultérieure.

## Contact

Yann Schwarz — yann.schwarz@gmail.com
