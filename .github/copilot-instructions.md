# Instructions Copilot pour le plugin QGIS Voirie Communale

## Architecture du plugin

Ce plugin QGIS suit l'architecture standard des plugins PyQGIS :
- **Point d'entrée** : `__init__.py` avec la fonction `classFactory(iface)` qui retourne l'instance du plugin
- **Classe principale** : `CheminsRuraux` dans `chemins_ruraux.py` gère le cycle de vie du plugin (initGui, unload, run)
- **Interface utilisateur** : Séparation entre la logique (`chemins_ruraux_dialog.py`) et l'UI Qt Designer (`.ui`)
- **Ressources** : Fichiers compilés via `pyrcc5` (resources.qrc → resources.py)

## API QGIS spécifique

### Interface principale (iface)
```python
self.iface.mainWindow()          # Fenêtre principale pour les boîtes de dialogue
self.iface.addToolBarIcon()      # Ajouter une icône dans la barre d'outils
self.iface.addPluginToVectorMenu()  # Ajouter au menu Vector
self.iface.mapCanvas()           # Accès au canevas de la carte
```

### Manipulation de couches
```python
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature
layers = QgsProject.instance().mapLayers()  # Toutes les couches
layer = self.iface.activeLayer()            # Couche active
```

### Widgets QGIS personnalisés
- `QgsMapLayerComboBox` : Sélecteur de couches avec filtres (VectorLayer, RasterLayer, etc.)
- Importez depuis `qgis.gui` et déclarez dans la section `<customwidgets>` du fichier .ui

## Workflow de développement critique

### 1. Modification de l'interface utilisateur
```powershell
# Éditer avec Qt Designer (optionnel, peut éditer le XML directement)
# Compiler les changements AVANT de tester
pyuic5 chemins_ruraux_dialog_base.ui -o chemins_ruraux_dialog_base.py
```

### 2. Modification des ressources (icônes)
```powershell
# Après avoir modifié resources.qrc
pyrcc5 resources.qrc -o resources.py
```

### 3. Test dans QGIS
- **Rechargement rapide** : Installer "Plugin Reloader" depuis le gestionnaire d'extensions
- **Débogage** : Console Python QGIS (Ctrl+Alt+P) ou attachez un débogueur externe
- **Logs** : Utilisez `QgsMessageLog.logMessage("message", "CheminsRuraux", Qgis.Info)`

### 4. Installation du plugin
```powershell
# Créer un lien symbolique vers le répertoire de plugins QGIS
$pluginDir = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux"
New-Item -ItemType SymbolicLink -Path $pluginDir -Target "d:\chemins_ruraux"
```

### 5. Synchronisation unidirectionnelle (développement → QGIS)
```powershell
# Après chaque changement de version ou release
$pluginDir = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux"
if (Test-Path $pluginDir) { Remove-Item -Recurse -Force $pluginDir }
Copy-Item -Recurse -Force D:\chemins_ruraux $pluginDir
```
- Cette commande supprime le plugin existant dans QGIS puis copie le dossier de développement.
- Toute suppression ou modification par QGIS n’affectera jamais le dossier de développement.
- À intégrer systématiquement dans le workflow de changement de version.

## Conventions du projet

### Structure des fichiers
- **Nommage** : Convention snake_case pour les fichiers Python et classes CamelCase
- **UI compilé** : Ne pas modifier `chemins_ruraux_dialog_base.py` manuellement, toujours régénérer depuis le .ui
- **Ressources** : Référencer via `:/plugins/chemins_ruraux/` dans le code après compilation

### Gestion des traductions
- Utiliser `self.tr("Texte")` pour toutes les chaînes visibles
- Fichiers de traduction dans `i18n/` (format Qt .qm)

### Métadonnées (metadata.txt)
- **Version** : Incrémenter pour chaque release (synchroniser avec version.py)
- **qgisMinimumVersion** : Vérifier la compatibilité API
- **experimental=True** : Pour les versions en développement

### Gestion des versions
- **version.py** : Fichier central contenant `__version__` et l'historique
- **CHANGELOG.md** : Documentation détaillée des changements (format Keep a Changelog)
- **metadata.txt** : Version et changelog pour le gestionnaire d'extensions QGIS
- Synchroniser les 3 fichiers lors des mises à jour de version

## Intégrations et dépendances

### Dépendances Python
- PyQt5 (fourni par QGIS)
- qgis.core, qgis.gui (API QGIS)
- Ajoutez des dépendances externes dans metadata.txt : `plugin_dependencies=autre_plugin`

### Données géospatiales
- **Format préféré** : GeoPackage (.gpkg) pour la performance
- **CRS** : Toujours vérifier et transformer si nécessaire avec `QgsCoordinateTransform`
- **Édition** : Utiliser `layer.startEditing()` / `layer.commitChanges()` pour modifier les données

### Flux WMS du Cadastre
Le plugin intègre le flux WMS du cadastre français :
- **URL du service** : `https://inspire.cadastre.gouv.fr/scpc/[codeINSEE].wms`
- **Gestionnaire** : DGFiP (Direction Générale des Finances Publiques)
- **CRS par défaut** : `EPSG:2154` (Lambert 93)
- **Note** : Le service nécessite le code INSEE de la commune (5 chiffres)
- **Couches disponibles** :
  - `CADASTRALPARCELS.PARCELLAIRE_EXPRESS` : Parcelles cadastrales
  - `BUILDINGS.BUILDINGS` : Bâtiments
  - `CADASTRALPARCELS.PARCELS` : Sections cadastrales
- **Chargement** : Utilisez `QgsRasterLayer` avec le provider `'wms'`

Exemple de chargement WMS :
```python
code_insee = "75056"  # Paris
wms_url = f"https://inspire.cadastre.gouv.fr/scpc/{code_insee}.wms"
uri = f"crs=EPSG:2154&format=image/png&layers=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&url={wms_url}"
layer = QgsRasterLayer(uri, "Cadastre - Parcelles", 'wms')
if layer.isValid():
    QgsProject.instance().addMapLayer(layer)
```

## Patterns spécifiques au projet

### Initialisation du dialogue (lazy loading)
```python
def run(self):
    if self.first_start == True:
        self.first_start = False
        self.dlg = CheminsRurauxDialog()
    # Le dialogue n'est créé qu'au premier clic
```

### Accès aux widgets du dialogue
```python
# Après setupUi(), accès direct aux widgets définis dans le .ui
selected_layer = self.dlg.mMapLayerComboBox.currentLayer()

# Connecter les signaux Qt dans la méthode run() lors de la première initialisation
if self.first_start == True:
    self.first_start = False
    self.dlg = CheminsRurauxDialog()
    self.dlg.btnLoadCadastre.clicked.connect(self.load_cadastre_wms)
```

### Menu et toolbar
- Plugin ajouté au menu Extensions via `addPluginToMenu()`
- Icône référencée depuis les ressources compilées : `:/plugins/chemins_ruraux/icon.png`

## Commandes de build essentielles

```powershell
# Compilation complète
.\compile.bat

# Test rapide des imports Python
python -c "from chemins_ruraux import CheminsRuraux; print('OK')"

# Vérifier la version de QGIS
qgis --version
```

## Points d'attention

1. **Ne jamais** importer PyQt5 et PyQt6 en même temps - QGIS 3.x utilise PyQt5
2. **Toujours** compiler les .ui et .qrc après modification
3. **Vérifier** la compatibilité API QGIS selon la version cible (3.0+)
4. **Tester** avec des données réelles de chemins ruraux (vecteurs linéaires)
5. **Documenter** les champs obligatoires pour les couches de chemins dans README.md
