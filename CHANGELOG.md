# [0.9.59] - 2026-03-01
### Modifié
- "Tout sélectionner / Désélectionner" déplacé au-dessus du label "Données à charger".
# [0.9.58] - 2026-03-01
### Modifié
- Case **Cadastre** déplacée de la section "Données à charger" vers la section "Plans à charger".
# [0.9.57] - 2026-03-01
### Ajouté
- Section **Plans à charger** dans la boîte de dialogue (en dessous de "Données à charger").
# [0.9.56] - 2026-03-01
### Modifié
- `TODO.md` n'est plus stocké dans le dossier du plugin (qui est écrasé à chaque mise à jour). Il est désormais sauvegardd dans le profil utilisateur QGIS : `<profil>/chemins_ruraux/TODO.md` (via `QgsApplication.qgisSettingsDirPath()`). Le fichier est créé automatiquement à la première ouverture.
# [0.9.55] - 2026-03-01
### Ajouté
- Suppression automatique des doublons : si une couche du même nom (même commune) existe déjà dans le projet QGIS, elle est retirée avant le rechargement. Concerne toutes les sources (cadastre, commune, BAN, voirie, OSM, BD TOPO, MAJIC).
# [0.9.54] - 2026-03-01
### Modifié
- Zoom après chargement : utilise désormais l'emprise de la couche commune plutôt que l'emprise combinée de toutes les couches chargées.
# [0.9.53] - 2026-03-01
### Modifié
- ToDo : remplacement de l'ouverture dans l'éditeur système par une fenêtre QGIS intégrée (`QDialog`) avec éditeur de texte et bouton **Enregistrer**.
# [0.9.52] - 2026-03-01
### Ajouté
- Entrée de menu **Extensions → Voirie Communale → ToDo** : ouvre `TODO.md` dans l'éditeur système par défaut.
# [0.9.51] - 2026-03-01
### Modifié
- Menu du plugin déplacé de **Vecteur** vers **Extensions** (`addPluginToMenu`).
# [0.9.50] - 2026-03-01
### Supprimé
- Catégorie "Autre" inutile dans le renderer OSM (les tronçons sont filtrés à la source — seuls C/R passent dans la couche).
# [0.9.49] - 2026-03-01
### Correction
- `AttributeError: 'QgsRectangle' object has no attribute '__ior__'` dans `validate_and_load` — le calcul de l'emprise combinatoire utilisait l'opérateur `|=` non supporté par `QgsRectangle`. Remplacé par `combineExtentWith()`.
# [0.9.48] - 2026-03-01
### Correction
- OSM Routes : libellés de catégorisation incorrects — C = Voie communale, R = Chemin rural, CE = Chemin d'exploitation.
# [0.9.47] - 2026-03-01
### Correction
- OSM Routes : la catégorisation (CE / C / R) était incorrecte pour les tronçons sans `ref` direct mais appartenant à une relation référencée. Le champ `ref` stocke désormais la meilleure référence disponible (`ref` direct, sinon `rel_ref`).
# [0.9.46] - 2026-03-01
### Ajouté
- Barre de progression (`QProgressDialog`) affichée après 1,5 seconde d'attente, avec le nom de la source en cours de chargement. Se ferme automatiquement à la fin.
# [0.9.45] - 2026-03-01
### Modifié
- SNA RPG : le flux WFS n'est pas encore disponible sur la Géoplateforme IGN. La case à cocher est conservée mais affiche un message d'information en attendant la mise à disposition.
# [0.9.44] - 2026-03-01
### Ajouté
- Nouvelle source de données : **Surfaces non agricoles RPG** (`RPG.LATEST:SNA`, WFS IGN Géoplateforme), filtrée sur l'emprise communale, rendu orange semi-transparent. Case à cocher dédiée, intégrée dans Tout sélectionner/Désélectionner.
# [0.9.43] - 2026-03-01
### Correction
- Case "Routes numérotées ou nommées (BD TOPO)" absente du groupe Tout sélectionner/Désélectionner.
# [0.9.42] - 2026-02-28
### Technique
- Mise à jour technique : incrémentation automatique de version, workflow automatisé (test).
# [0.9.41] - 2026-02-25
### Ajouté
- Affichage d'un avertissement à l'utilisateur (QMessageBox.warning) en cas d'échec du chargement MAJIC (personnes morales).
# [0.9.40] - 2026-02-25
### Correction
- Mapping MAJIC/WFS IGN amélioré : correspondance multi-variantes pour géoréférencement maximal des parcelles.
# [0.9.39] - 2026-02-25
### Suppression
- Retrait complet de la couche BD TOPO Tronçons de route (case à cocher, logique, code, changelog, metadata).
# [0.9.38] - 2026-02-25
### Correction
- Symbologie BD TOPO limitée à 6 valeurs principales de type_de_route (les autres supprimées).
# [0.9.37] - 2026-02-25
### Correction
- Symbologie catégorisée mise à jour pour n'utiliser que les valeurs officielles de type_de_route BD TOPO.
# [0.9.36] - 2026-02-25
### Ajout
- Affichage catégorisé de la couche Routes numérotées ou nommées selon le champ type_de_route.
# Changelog - Voirie Communale

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/lang/fr/).



## [0.9.35] - 2026-02-23

### Ajouté
- Affichage explicite des licences de chaque source de données dans le menu et la boîte de dialogue À propos (Licence Ouverte 2.0, ODbL, etc.).
- Nouvelle donnée : **Routes numérotées ou nommées (BD TOPO® IGN)** (BDTOPO_V3:route_numerotee_ou_nommee) — case à cocher dédiée, chargement filtré sur la commune, licence ouverte IGN.

## [Non publié]

## [0.9.34] - 2026-02-23

### Corrigé
- Dictionnaire `MAJIC_FORMES_JURIDIQUES` : libellés des codes `AU*` corrigés d'après analyse des dénominations observées dans les données (`AUDA` = Autre administration, `AUDP` = Autre de droit privé, `AUEP` = Autre entité publique, `AUPE` = Autre personne étrangère, `AURS` = Autre à régime spécial, `AUTA` = Autre titre administratif, `AUTC` = Autre titre collectif).

## [0.9.33] - 2026-02-23

### Modifié
- Couche **MAJIC** : catégorisation basée sur `groupe_personne` (10 groupes officiels DGFiP) avec les couleurs exactes de l'application Koumoul. Légende : 🔴 Personnes morales non remarquables · 🟠 État · 🟢 Région · 🟡 Département · 💙 Commune · 💜 Office HLM · 🟡 SEM · Copropriétaires · Associés · 🔵 Établissements publics.

## [0.9.32] - 2026-02-23

### Modifié
- Couche **MAJIC** : rendu catégorisé avec palette fixe (couleurs stables quelle que soit la commune). Chaque code de forme juridique est associé à un libellé complet (ex : `SARL` → _Société à responsabilité limitée_) et une couleur sémantique groupée : bleus pour les collectivités, teals pour l'intercommunalité, verts pour les associations, oranges pour l'agriculture, rouges pour les sociétés commerciales, violets pour les sociétés civiles. 100 formes juridiques répertoriées, fallback gris pour les codes inconnus.

## [0.9.31] - 2026-02-23

### Ajouté
- Couche **MAJIC** : rendu catégorisé QGIS appliqué automatiquement sur le champ `forme_juridique`. Chaque forme juridique abrégée (SA, SARL, COMMUNE, ASSOC…) obtient une couleur HSV distincte. Les parcelles sans forme juridique renseignée apparaissent en gris.

## [0.9.30] - 2026-02-22

### Modifié
- Couche **MAJIC** : géométrie passée de points (centroïdes `_geopoint`) à **polygones**. Les contours de parcelles sont désormais chargés depuis le WFS IGN Géoplateforme (`CADASTRALPARCELS.PARCELLAIRE_EXPRESS:parcelle`), filtrés par commune (`code_dep` + `code_com`). Jointure par `idu` (IGN) = `code_parcelle` (Koumoul). Seules les parcelles appartenant à des personnes morales sont retenues. Gestion des départements DOM (code_dep sur 3 chars).

## [0.9.29] - 2026-02-22

### Corrigé
- MAJIC HTTP 400 Bad Request (tentative 2) : deux causes identifiées par test direct de l'API :
  1. **Filtre inopérant** : `code_commune=88141` ne filtrait pas (renvoyait 16M résultats). Corrigé en `qs=code_commune:88141` (syntaxe Elasticsearch de Data Fair, test confirmé : 152 résultats pour commune 88141)
  2. **Pagination par `skip`** : avec 16M résultats sans filtre, `skip` dépassait la limite de l'API. Remplacé par curseur `after` (extrait du champ `next` de la réponse API)

## [0.9.28] - 2026-02-22

### Corrigé
- MAJIC HTTP 400 Bad Request : le champ `_parcelle_coords.coord` (point dans le nom) n'était pas accepté dans le paramètre `select` de l'API Data Fair. Remplacé par `_geopoint` (champ calculé centroïde `"lat,lon"`). Pagination corrigée de `skip` vers curseur `after`.

## [0.9.27] - 2026-02-22

### Ajouté
- Couche **Parcelles personnes morales (MAJIC)** : charge les parcelles cadastrales détenues par des personnes morales (entreprises, associations, collectivités) pour la commune sélectionnée. Source : API REST [Koumoul](https://koumoul.com/data-fair/app/carte-des-parcelles-des-personnes-morales-majic) (données DGFiP, Licence Ouverte). Couche de points avec attributs : dénomination, SIREN, forme juridique, groupe, contenance, nature culture, adresse.

## [0.9.26] - 2026-02-22

### Corrigé
- Case "Tout sélectionner" : suppression du tristate, comportement binaire simple

## [0.9.25] - 2026-02-22

### Corrigé
- Case maître "Tout sélectionner" : état partiel non fonctionnel au premier clic. Cause : signal `stateChanged` déclenchait le cycle tristate 0→1→2, passant par l'état partiel avant d'atteindre "coché". Correction : signal `clicked` utilisé à la place, avec forçage direct à l'état coché si la checkbox atterrit sur l'état partiel.

## [0.9.24] - 2026-02-22

### Ajouté
- Case à cocher **Tout sélectionner / Désélectionner** dans le panneau de sélection des couches : coche ou décoche toutes les couches en une action. Supporte l'état intermédiaire (partiellement coché) quand seules certaines couches sont sélectionnées.

## [0.9.23] - 2026-02-22

### Corrigé
- Champ géométrie BD TOPO `troncon_de_route` : `geometrie` au lieu de `geom` (Bad Request 400)
- Paramètre `geom_field` ajouté dans `load_wfs_layer` pour gérer les noms de champ variables selon la source

## [0.9.22] - 2026-02-22

### Ajouté

## [0.9.21] - 2026-02-22

### Ajouté
- Boîte de dialogue **À propos** dans le menu du plugin : version, auteur, licence, lien GitHub

## [0.9.20] - 2026-02-22

### Corrigé
- Renommage exhaustif du plugin en **Voirie Communale** dans tous les fichiers restants : message de log au chargement (`chemins_ruraux.py`), scripts de compilation (`compile_plugin.py`, `compile_simple.py`), script de packaging (`package.py`), guide de démarrage rapide (`QUICKSTART.md`) et `releases/README.md`

## [0.9.19] - 2026-02-22

### Modifié
- Renommage du plugin en **Voirie Communale** : la description, les menus, titres et en-têtes reflètent désormais le périmètre élargi (voies communales et chemins ruraux)

## [0.9.18] - 2026-02-22

### Optimisations
- Suppression des imports inutilisés : `QgsDataSourceUri`, `QgsCoordinateReferenceSystem`, `QgsSymbol`, `tempfile`
- Suppression de `self.temp_files` (plus de fichiers temporaires OSM)
- Suppression des paramètres `show_wait_message` de `load_wfs_layer` (jamais utilisés)
- Logs verbeux de la boucle de zoom supprimés

### Corrigé
- Bug `apply_ban_style` : `label_settings.fieldName` était assigné 3 fois consécutivement

### Nettoyage
- En-têtes boilerplate auto-générés remplacés par des en-têtes propres
- `first_start == True` simplifié en `first_start`

## [0.9.17] - 2026-02-22

### Modifié
- Renommage des couches voirie : `DGCL Voirie communale retenue DSR 2025 {insee}` et `DGCL Voirie départementale retenue DGF 2025 {insee}`

## [0.9.16] - 2026-02-22

### Modifié
- Renommage des couches voirie : `Voirie communale pour calcul DSR {insee}` et `Voirie départementale pour calcul DGF {insee}`

## [0.9.15] - 2026-02-18

### Corrigé
- OSM : champs définis dans l'URI de la couche mémoire (`field=ref:string&field=name:string&...`) au lieu de `addAttributes` — `setAttribute("ref", ...)` fonctionne désormais correctement

## [0.9.14] - 2026-02-18

### Corrigé
- OSM : `KeyError: 'ref'` corrigé — attributs écrits par index (`feat[0]`, `feat[1]`...) au lieu de `setAttribute(nom)`

## [0.9.13] - 2026-02-18

### Corrigé
- OSM : attributs écrits via `setAttribute(nom, valeur)` au lieu de `setAttributes([liste])` — le champ `ref` était vide, rendant le style catégorisé inopérant

## [0.9.12] - 2026-02-18

### Ajouté
- Style catégorisé pour la couche OSM : CE (vert), C (orange), R (rouge)
- Étiquettes avec le champ `ref` sur les routes OSM

## [0.9.11] - 2026-02-18

### Corrigé
- OSM : requête Overpass corrigée (`out geom;` au lieu de `out body;>;out body geom;`) — les ways n'avaient aucune géométrie inline, 0 feature chargée
- OSM : ajout du traitement des membres de relations (ways avec géométrie inline via `out geom;`)
- Testé sur commune 88141 : 74/74 routes C/R correctement chargées

## [0.9.10] - 2026-02-18

### Corrigé
- `QgsField` : suppression du constructeur déprécié avec `QVariant.String`, import `QVariant` retiré

## [0.9.9] - 2026-02-17

### Corrigé
- Indentation invalide dans le chargement OSM

## [0.9.8] - 2026-02-17

### Corrigé
- Correction du filtre OSM `ref` C/R (erreur `matched_count`)

## [0.9.7] - 2026-02-17

### Corrigé
- Filtre OSM `ref` C/R via JSON Overpass et couche mémoire

## [0.9.6] - 2026-02-17

### Corrigé
- Filtre OSM `ref` avec propagation des refs de relations

## [0.9.5] - 2026-02-17

### Corrigé
- Filtre OSM `ref` appliqué localement après téléchargement

## [0.9.4] - 2026-02-17

### Corrigé
- Filtre OSM `ref` via relations `route` et voies associées

## [0.9.3] - 2026-02-17

### Corrigé
- Filtre OSM `ref` via relations `route=road` et voies associées

## [0.9.2] - 2026-02-17

### Ajusté
- Filtre OSM routes avec `ref` commençant par C ou R

## [0.9.1] - 2026-02-17

### Ajusté
- Téléchargement des routes OSM sans filtres `highway`/`surface`

## [0.9.0] - 2026-02-17

### Ajouté
- Téléchargement des routes OSM via Overpass avec filtres `highway` et `surface`

## [0.8.6] - 2026-02-14

### Corrigé
- Utilisation de deux formats d'URI WFS selon le type de filtre :
  - Format classique `https://...?service=WFS&CQL_FILTER=...` pour filtres par code_insee (commune, BAN)
  - Format provider QGIS `url=...&bbox=...&restrictToRequestBBOX=1` pour filtres spatiaux (voiries)

## [0.8.5] - 2026-02-14

### Corrigé
- Format de l'URI WFS pour que QGIS respecte le filtre BBOX
- Changement de format : `url=...&typename=...&bbox=...&restrictToRequestBBOX=1` au lieu de `https://...?service=WFS&BBOX=...`
- Le filtre spatial BBOX fonctionne maintenant correctement pour les voiries

## [0.8.4] - 2026-02-14

### Corrigé
- Évite le chargement en double de la commune lorsque l'emprise communale est déjà sélectionnée
- Réutilisation de la couche commune déjà chargée pour obtenir le BBOX des voiries

## [0.8.3] - 2026-02-14

### Corrigé
- Chargement des voiries (communale et départementale) avec filtre BBOX spatial au lieu de code_insee
- Les tables DGCL.2025 n'ayant pas de champ code_insee, utilisation de l'emprise communale pour filtrage
- Chargement automatique de la couche commune si non sélectionnée mais nécessaire pour le BBOX

### Amélioré
- Méthode `load_wfs_layer()` générique supporte maintenant :
  - Filtre CQL avec code_insee (optionnel)
  - Filtre BBOX avec emprise (optionnel)
  - Combinaison des deux filtres possible

## [0.8.2] - 2026-02-14

### Supprimé
- Message d'attente (QMessageBox) lors du chargement des adresses BAN
- Chargement plus fluide sans interruption de l'interface

## [0.8.1] - 2026-02-14

### Corrigé
- Tooltips des checkboxes voirie : correction pour indiquer la source correcte (calcul IGN pour la DGCL)
- Formulation précise : "Charge le réseau de voirie communale/départementale (calcul IGN pour la DGCL)"

## [0.8.0] - 2026-02-14

### Ajouté
- Nouvelle source de données WFS : Voirie départementale (DGCL.2025:voirie_departementale)
- Checkbox dans l'interface pour sélectionner le chargement de la voirie départementale
- Méthode `load_voirie_dep_wfs()` utilisant l'architecture générique WFS

### Amélioré
- Ajout de la validation de la checkbox voirie départementale dans `validate_and_load()`
- Messages informatifs spécifiques pour la voirie départementale

## [0.7.0] - 2026-02-14

### Ajouté
- Nouvelle source de données WFS : Voirie communale (DGCL.2025:voirie_communale)
- Checkbox dans l'interface pour sélectionner le chargement de la voirie communale
- Méthode `load_voirie_wfs()` utilisant l'architecture générique WFS

### Amélioré
- Ajout de la validation de la checkbox voirie dans `validate_and_load()`
- Messages informatifs spécifiques pour la voirie communale

## [0.6.16] - 2026-02-14

### Optimisé
- URL WFS IGN mutualisée en constante de classe `WFS_IGN_URL = "https://data.geopf.fr/wfs"`
- Suppression de l'URL redondante `/wfs/ows` (tous les services utilisent maintenant `/wfs`)
- Signature de `load_wfs_layer()` simplifiée (paramètre `wfs_url` supprimé)

## [0.6.15] - 2026-02-14

### Refactorisé
- Création d'une méthode générique `load_wfs_layer()` pour centraliser le chargement WFS
- Les méthodes `load_commune_wfs()` et `load_ban_wfs()` utilisent maintenant la méthode générique
- Code plus maintenable et facilite l'ajout de nouvelles sources WFS
- Réduction de la duplication de code (~100 lignes économisées)

## [0.6.14] - 2026-02-14

### Amélioré
- Catégorie "Autre" désactivée par défaut dans la légende de la couche BAN
- Seuls les chemins ruraux et voies communales sont visibles au chargement

## [0.6.13] - 2026-02-14

### Amélioré
- Étiquettes BAN affichées uniquement sur les chemins ruraux et voies communales (filtre via expression CASE)

## [0.6.12] - 2026-02-14

### Corrigé
- Placement des étiquettes BAN : AroundPoint au lieu de OverPoint (TypeError résolu)

## [0.6.11] - 2026-02-14

### Amélioré
- Nouveau logo du plugin

## [0.6.10] - 2026-02-14

### Amélioré
- Étiquettes automatiques sur la couche BAN affichant le nom de la voie
- Buffer blanc autour des étiquettes pour meilleure lisibilité
- Placement des étiquettes au-dessus des points

## [0.6.9] - 2026-02-14

### Amélioré
- Regex optimisées avec groupes non capturants (?:...)
- che(?:min)? et sen(?:tier)? plus concis et performants
- voi(?:e)? et com(?:munale)? également optimisés

## [0.6.8] - 2026-02-14

### Corrigé
- regexp_match retourne position, ajout test > 0 pour fonctionnement correct
- Double échappement des backslash pour regex dans Python string

## [0.6.7] - 2026-02-14

### Corrigé
- Regex compatible avec moteur QGIS (sans groupes non capturants)
- Syntaxe simplifiée mais fonctionnalité identique

## [0.6.6] - 2026-02-14

### Corrigé
- Regex voie communale : COM au lieu de CO (VOI COM, VOIE COMMUNALE, etc.)

## [0.6.5] - 2026-02-14

### Amélioré
- Regex optimisée pour voies communales : VC, V.C., VOI COMMUNALE, VOIE CAL, etc.
- Suppression des filtres génériques rue/avenue/boulevard (trop larges)
- Cohérence avec le pattern chemins ruraux

## [0.6.4] - 2026-02-14

### Amélioré
- Remplacement des filtres LIKE par des regex optimisées
- Performance améliorée avec groupes non capturants (?:...)
- Expression plus concise et maintenable

## [0.6.3] - 2026-02-14

### Amélioré
- Filtres chemins ruraux beaucoup plus précis et exhaustifs :
  - "Chemin Rural" (toutes variations de casse)
  - "CR" (avec espaces avant/après)
  - "C.R." (avec points)
  - "CHE RURAL" (abréviation courante)
  - "Sentier Rural"
  - "SEN RURAL" (abréviation courante)
- Utilisation de upper() pour insensibilité à la casse
- Suppression du filtre générique "Chemin" trop large

## [0.6.2] - 2026-02-14

### Ajouté
- Style différencié automatique pour la couche BAN :
  - **Chemins ruraux** : Points marron/chocolat (détection via "Chemin", "CR")
  - **Voies communales** : Points bleus (détection via "Rue", "Avenue", "Boulevard", "VC")
  - **Autres voies** : Points gris
- Fonction apply_ban_style() avec expression CASE WHEN sur le champ nom_voie
- Symbologie basée sur QgsCategorizedSymbolRenderer
- Log de confirmation du style appliqué

## [0.6.1] - 2026-02-14

### Corrigé
- URL WFS BAN avec paramètres en minuscules (service, version, request)
- Ajout d'un message d'avertissement avant le chargement BAN pour informer l'utilisateur
- Message indique que le service peut être lent et demande de patienter

## [0.6.0] - 2026-02-14

### Ajouté
- Nouvelle source de données : Base Adresse Nationale (BAN)
- Case à cocher "Adresses (Base Adresse Nationale - BAN)" dans l'interface
- Fonction load_ban_wfs() pour charger les adresses via WFS
- Filtre par code_insee sur les 26+ millions d'adresses de France
- Support EPSG:4326 pour la BAN
- Logs de progression et avertissement sur le temps de chargement
- Gestion intelligente des messages selon les données chargées (cadastre/commune/BAN)

## [0.5.13] - 2026-01-27

### Modifié
- Remplacement de ADMINEXPRESS-COG.LATEST:commune par LIMITES_ADMINISTRATIVES_EXPRESS.LATEST:commune
- Couche WFS plus récente pour les limites communales
- Conserve EPSG:4326 et le filtre code_insee

## [0.5.12] - 2026-01-27

### Corrigé
- Transformation automatique de l'emprise dans le CRS du projet avant d'appliquer le zoom
- Détection du CRS source depuis les couches chargées
- Logs de la transformation : CRS source, CRS cible, emprise avant/après
- Résolution du problème : emprise WFS en EPSG:4326 vs projet en EPSG:2154

## [0.5.11] - 2026-01-27

### Corrigé
- Ajout de updateExtents() pour forcer le calcul de l'emprise des couches WFS
- Logs détaillés pour chaque couche : nom, extent, isEmpty
- Logs du résultat final du zoom pour faciliter le diagnostic
- Meilleure visibilité du processus de zoom dans le journal des messages

## [0.5.10] - 2026-01-27

### Amélioré
- Zoom robuste avec priorité sur les couches vectorielles (commune WFS)
- Fallback sur les couches raster WMS (cadastre) si nécessaire
- Ajout d'une marge de 5% autour de l'emprise pour meilleure visibilité
- Vérification que les emprises ne sont pas vides avant utilisation
- Gestion du cas où les couches WMS n'ont pas encore d'emprise valide

## [0.5.9] - 2026-01-27

### Amélioré
- Le zoom se fait désormais uniquement sur les couches nouvellement chargées
- Calcul de l'emprise combinée de toutes les couches chargées (cadastre + commune)
- Les fonctions load_cadastre_wms() et load_commune_wfs() retournent maintenant les couches créées
- Meilleure expérience utilisateur : pas de zoom sur toute la carte

## [0.5.8] - 2026-01-27

### Modifié
- Simplification : utilisation de EPSG:4326 (WGS84) pour tous les territoires français
- Suppression de la détection DOM-TOM devenue inutile
- Un seul CRS universel élimine les problèmes de compatibilité

## [0.5.7] - 2026-01-27

### Corrigé
- Détection automatique des DOM-TOM (codes INSEE 97xxx et 98xxx)
- Utilisation de EPSG:4326 (WGS84) pour les DOM-TOM au lieu de EPSG:2154
- Évite le plantage de QGIS lors du chargement d'emprises communales DOM-TOM
- EPSG:2154 (Lambert 93) conservé pour la métropole et la Corse

## [0.5.6] - 2026-01-27

### Corrigé
- Centralisation du zoom et du retour au premier plan dans la méthode validate_and_load()
- Le dialogue revient TOUJOURS au premier plan après chaque opération
- Zoom automatique après chaque chargement réussi (cadastre et/ou commune)
- Suppression du code redondant dans load_cadastre_wms() et load_commune_wfs()

## [0.5.5] - 2026-01-27

### Corrigé
- Restauration du zoom automatique sur l'emprise communale à chaque chargement
- Restauration du retour au premier plan du dialogue après chargement (toujours actif)
- Ajout du retour au premier plan après les messages récapitulatifs

## [0.5.4] - 2026-01-27

### Modifié
- Construction directe de l'URI WFS au lieu d'utiliser QgsDataSourceUri
- Utilisation de `CQL_FILTER=code_insee='54215'` dans l'URI complète
- Ajout de log pour afficher l'URI générée et faciliter le débogage

## [0.5.3] - 2026-01-27

### Modifié
- Suppression de tous les guillemets autour de la valeur dans le filtre CQL

## [0.5.2] - 2026-01-27

### Corrigé
- Filtre CQL WFS : suppression de tous les guillemets autour de la valeur
- Génère maintenant `code_insee=54215` (sans guillemets)

## [0.5.2] - 2026-01-27

### Corrigé
- Filtre CQL WFS : utilisation de guillemets doubles au lieu de simples pour éviter les antislashs d'échappement
- Le filtre génère maintenant `code_insee="54215"` au lieu de `code_insee=\'54215\'`

## [0.5.1] - 2026-01-27

### Corrigé
- Filtre WFS pour l'emprise communale : utilisation du champ correct `code_insee` au lieu de `insee_com`
- L'emprise communale se charge maintenant correctement avec le filtre sur le code INSEE

## [0.5.0] - 2026-01-27

### Modifié
- Remplacement des boutons radio par des cases à cocher pour permettre le chargement simultané de plusieurs types de données
- Cadastre ET emprise communale peuvent maintenant être chargés en même temps

### Ajouté
- Message récapitulatif lors du chargement de plusieurs types de données
- Gestion intelligente de l'affichage : pas de message individuel si chargement multiple

## [0.4.0] - 2026-01-27

### Ajouté
- Boutons radio pour choisir entre le chargement du cadastre (10 couches) ou de l'emprise communale
- Interface plus claire avec sélection explicite du type de données

### Modifié
- Titre du groupe changé de "Cadastre" à "Données géographiques"
- Texte du bouton changé de "Charger toutes les couches du Cadastre" à "Charger les données"
- Messages d'information adaptés selon le type de données chargées

## [0.3.2] - 2026-01-27

### Corrigé
- Nom correct de la couche WFS: `ADMINEXPRESS-COG.LATEST:commune` (avec "-COG")
- Le service WFS n'expose pas `ADMINEXPRESS.LATEST` mais `ADMINEXPRESS-COG.LATEST`

## [0.3.1] - 2026-01-27

### Corrigé
- Utilisation de la couche correcte `ADMINEXPRESS.LATEST:commune` au lieu de `ADMINEXPRESS-COG-CARTO.LATEST:commune`
- Couche Admin Express standard sans COG-CARTO

## [0.3.0] - 2026-01-27

### Ajouté
- **Chargement automatique de l'emprise communale** via WFS Admin Express de l'IGN Géoplateforme
- Service WFS : `https://data.geopf.fr/wfs` (couche `ADMINEXPRESS-COG-CARTO.LATEST:commune`)
- Filtre automatique par code INSEE
- Zoom automatique sur l'emprise de la commune après chargement
- Affichage du statut de chargement de l'emprise dans le message de confirmation

### Amélioré
- Intégration complète : cadastre (DGFiP) + emprise administrative (IGN)
- Logs détaillés pour le débogage WFS

## [0.2.9] - 2026-01-27

### Corrigé
- Le dialogue principal revient automatiquement au premier plan après les messages de succès ou d'erreur
- Ajout de `raise_()` et `activateWindow()` après les QMessageBox de confirmation
- Expérience utilisateur améliorée : flux de travail continu sans perdre le dialogue

## [0.2.8] - 2026-01-27

### Corrigé
- Le dialogue existant est maintenant ramené au premier plan au lieu de créer une nouvelle fenêtre
- Ajout de `raise_()` et `activateWindow()` pour gérer correctement le focus
- Un seul dialogue reste ouvert même avec plusieurs clics sur l'icône du plugin

## [0.2.7] - 2026-01-25

### Amélioré
- Dialogue non-modal : reste ouvert après le chargement du cadastre
- Permet de charger plusieurs communes successivement sans fermer/rouvrir le dialogue
- Suppression de `exec_()` remplacé par `show()` simple

## [0.2.6] - 2026-01-25

### Corrigé
- **CORRECTION CRITIQUE** : `IndentationError: unexpected indent` à la ligne 354
- Nettoyage des lignes orphelines restées après suppression du code mMapLayerComboBox

## [0.2.5] - 2026-01-25

### Corrigé
- **CORRECTION CRITIQUE** : Erreur `AttributeError: 'CheminsRurauxDialog' object has no attribute 'mMapLayerComboBox'`
- Suppression du code qui référençait le widget supprimé en 0.2.4
- Le bouton OK ferme maintenant correctement le dialogue sans erreur

## [0.2.4] - 2026-01-25

### Supprimé
- Widget "Couche de chemins" inutilisé (sera réimplémenté avec une vraie fonctionnalité ultérieurement)
- Section "Options" vide de l'interface
- Déclaration du customwidget QgsMapLayerComboBox devenu inutile

### Amélioré
- Interface plus épure et focusée sur le cadastre

## [0.2.3] - 2026-01-25

### Corrigé
- **Correction de la validation des codes INSEE** (la regex de 0.2.2 était inutile)
- Validation complète et réelle des codes INSEE français :
  - Métropole : Départements 01-19, 21-95 (format : 2 chiffres + 3 chiffres)
  - Corse : 2A et 2B (format : 2A/2B + 3 chiffres)
  - DOM : 971-976 (format : 3 chiffres + 2 chiffres)
  - TOM : 984-988 (format : 3 chiffres + 2 chiffres)
- Messages d'erreur détaillés avec exemples par territoire
- Conversion automatique en majuscules pour les codes Corse
- Interface : Placeholder et tooltip mis à jour

## [0.2.2] - 2026-01-25

### Amélioré
- Validation du code INSEE avec expression régulière (`^\\d{5}$`)
- Validation plus robuste et explicite avec le module `re`

## [0.2.1] - 2026-01-25

### Corrigé
- Suppression des cases à cocher (Parcelles, Bâtiments, Sections) de l'interface utilisateur
- Simplification de l'interface : un seul bouton "Charger toutes les couches du Cadastre"
- Cohérence entre le code (chargement automatique) et l'interface utilisateur

## [0.2.0] - 2026-01-25

### Ajouté
- Chargement automatique de 10 couches cadastrales au lieu de 3
- Nouvelles couches : Lieux-dits, Amorces cadastrales, Clôtures, Détails topographiques, Hydrographie, Voies de communication, Bornes et repères
- Organisation automatique des couches dans un groupe nommé "Cadastre - {code INSEE}"

### Amélioré
- Les couches sont maintenant organisées dans un groupe dédié pour faciliter la gestion
- Chargement complet du cadastre en un seul clic

### Supprimé
- Cases à cocher de sélection des couches (chargement automatique de toutes les couches)

## [0.1.2] - 2026-01-25

### Corrigé
- **CORRECTION CRITIQUE** : Utilisation des noms de couches corrects selon le service INSPIRE
  - Parcelles : `CP.CadastralParcel` (au lieu de CADASTRALPARCELS.PARCELLAIRE_EXPRESS)
  - Bâtiments : `BU.Building` (au lieu de BUILDINGS.BUILDINGS)
  - Sections : `SUBFISCAL` (au lieu de CADASTRALPARCELS.PARCELS)
- Vérifié via GetCapabilities du service https://inspire.cadastre.gouv.fr/scpc/

## [0.1.1] - 2026-01-25

### Corrigé
- Correction du chargement de l'interface : utilisation du fichier UI compilé (.py) au lieu du fichier source (.ui)
- Résolution de l'erreur FileNotFoundError lors du chargement du plugin

### Amélioré
- Gestion d'erreur détaillée pour le chargement des flux WMS
- Logs détaillés dans le journal des messages QGIS (onglet CheminsRuraux)
- Messages d'erreur explicites avec instructions de diagnostic
- Affichage des URI WMS testés pour faciliter le débogage

## [0.1.0] - 2026-01-25

### Ajouté
- Structure initiale du plugin QGIS
- Interface utilisateur avec Qt Designer
- Intégration du flux WMS cadastre INSPIRE (DGFiP)
- Champ de saisie pour le code INSEE de la commune
- Validation du code INSEE (5 chiffres obligatoires)
- Sélection des couches cadastrales :
  - Parcelles cadastrales (CADASTRALPARCELS.PARCELLAIRE_EXPRESS)
  - Bâtiments (BUILDINGS.BUILDINGS)
  - Sections cadastrales (CADASTRALPARCELS.PARCELS)
- Messages d'erreur explicites pour l'utilisateur
- Logs dans la console QGIS
- Documentation complète (README.md, QUICKSTART.md)
- Instructions Copilot pour les agents IA (.github/copilot-instructions.md)
- Scripts de compilation Python (compile.bat, compile.sh, compile_plugin.py)
- Gestion des ressources (icônes) via PyQt5

### Configuration
- Support QGIS 3.0+
- Compatibilité Python 3.6+
- CRS par défaut : EPSG:2154 (Lambert 93)
- Format WMS : image/png

### Documentation
- Guide d'installation en mode développement
- Workflow de développement (modification UI, compilation, test)
- Exemples de codes INSEE
- Lien vers le site INSEE pour recherche de codes

## [0.0.1] - 2026-01-25

### Ajouté
- Initialisation du projet
- Structure de base du plugin PyQGIS
- Fichiers de métadonnées (metadata.txt)

[Non publié]: https://github.com/votre-username/chemins_ruraux/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/votre-username/chemins_ruraux/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/votre-username/chemins_ruraux/releases/tag/v0.0.1
