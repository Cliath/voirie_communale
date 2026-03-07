# Voirie Communale - Plugin QGIS

Plugin QGIS pour le recensement de la voirie communale (voies communales et chemins ruraux).  
Version actuelle : **0.11.6**

## Installation

### Depuis un ZIP

1. Récupérez le ZIP depuis le dépôt ou via `build.bat` (dossier `releases/`)
2. QGIS → **Extensions** → **Installer/Gérer les extensions** → onglet **Installer depuis un ZIP**
3. Sélectionnez le fichier `chemins_ruraux-X.X.X.zip` et cliquez sur **Installer l'extension**
4. Activez le plugin dans l'onglet **Installées**

### En mode développement

```powershell
# Déployer manuellement dans le répertoire des plugins QGIS
$pluginDir = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux"
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
- **Paramètres** : zoom automatique et réordonnancement automatique des couches configurables
- **Ordre canonique** des couches dans le panneau (haut → bas) : BD TOPO → Voirie comm. → Voirie dép. → OSM Routes → BAN → MAJIC → Commune → PLAN IGN → Waze → OSM France → Cadastre → BD ORTHO® → Photos aériennes → SCAN 50® → Cassini → État-Major

### Données vectorielles (filtrées par code INSEE ou BBOX communale)

| Couche | Source | Filtre |
|--------|--------|--------|
| **Emprise communale** | IGN Géoplateforme WFS — Admin Express | code INSEE |
| **Adresses BAN** | IGN Géoplateforme WFS | code INSEE |
| **Voirie communale DGCL 2025** | IGN Géoplateforme WFS | BBOX commune |
| **Voirie départementale DGCL 2025** | IGN Géoplateforme WFS | BBOX commune |
| **Routes OSM** (CE / C / R) | Overpass API | BBOX commune |
| **BD TOPO routes nommées** | IGN Géoplateforme WFS | BBOX commune |
| **Parcelles MAJIC** (personnes morales) | API Koumoul (DGFiP) + IGN WFS | code INSEE |

#### Routes OSM — catégorisation par `ref`

- 🟢 **CE** – Chemin d'exploitation (`ref` commence par `CE`)
- 🟠 **C** – Voie communale (`ref` commence par `C`, hors `CE`)
- 🔴 **R** – Chemin rural (`ref` commence par `R`)

### Plans de fond

| Plan | Source |
|------|--------|
| **Cadastre** (10 couches) | DGFiP — WMS INSPIRE |
| **Plan IGN J+1** | IGN Géoplateforme WMS |
| **Waze** | Tuiles XYZ Waze |
| **OSM France** | Tuiles XYZ openstreetmap.fr |
| **BD ORTHO® 20 cm** | IGN Géoplateforme WMS |
| **Photos aériennes historiques** (8 périodes 1950–2023) | IGN Géoplateforme WMS |
| **SCAN 50® 1950** | IGN Géoplateforme WMS |
| **Carte de Cassini** | IGN Géoplateforme WMS |
| **Carte de l'État-Major** | IGN Géoplateforme WMS |
| **MNT LiDAR HD** | IGN Géoplateforme WMS |

## Utilisation

1. Cliquez sur l'icône **Voirie Communale** dans la barre d'outils
2. Cliquez sur **Charger des données**
3. Saisissez le **code INSEE** de la commune (5 chiffres, ex : `57150`)
4. Cochez les couches souhaitées
5. Cliquez sur **Charger les données**

Les couches nécessitant un filtre géographique (Voirie DGCL, OSM Routes, BD TOPO) chargent automatiquement l'emprise communale en premier pour délimiter la zone de requête.

## Structure du projet

```
chemins_ruraux/
├── __init__.py                      # Point d'entrée du plugin
├── chemins_ruraux.py                # Classe principale (logique métier)
├── chemins_ruraux_dialog.py         # Dialogues (LauncherDialog, CheminsRurauxDialog, etc.)
├── chemins_ruraux_dialog_base.ui    # Interface Qt Designer
├── chemins_ruraux_dialog_base.py    # [généré] Compilé depuis le .ui
├── resources.qrc                    # Ressources Qt (icônes)
├── resources.py                     # [généré] Compilé depuis resources.qrc
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
| API Koumoul (MAJIC) | `https://koumoul.com/data-fair/api/v1/datasets/parcelles-des-personnes-morales` |

## Licence

GNU General Public License v2.0 ou ultérieure.

## Contact

Yann Schwarz — yann.schwarz@gmail.com
