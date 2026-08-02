# -*- coding: utf-8 -*-
"""
Voirie Communale - Cache local GeoPackage
Copyright (C) 2026 Yann Schwarz <yann.schwarz@gmail.com>
Licence : GNU GPL v2+
"""
import os
import time

from qgis.core import (QgsVectorLayer, QgsVectorFileWriter, QgsProject,
                        QgsMessageLog, Qgis, QgsApplication, QgsDataProvider)


class CacheManagerMixin:
    """Cache local des couches vecteur par commune, sous forme de GeoPackage.

    Un fichier `voirie_{code_insee}.gpkg` est créé dans un dossier dédié du
    profil QGIS actif, avec une couche interne par type de donnée (ex. 'ban',
    'majic', 'filaires_bal'...). Le cache est transparent : consulté avant
    tout téléchargement réseau, et alimenté après chaque chargement réussi.

    Il n'y a pas d'expiration automatique — seulement un avertissement
    affiché si le cache dépasse un âge configurable (paramètre
    'cache_warning_days'), l'utilisateur restant libre de forcer un
    rechargement complet via le bouton dédié.
    """

    CACHE_SUBDIR = "voirie_communale_cache"

    def _cache_dir(self):
        """Retourne (et crée si besoin) le dossier de cache dans le profil QGIS."""
        base = QgsApplication.qgisSettingsDirPath()
        cache_dir = os.path.join(base, self.CACHE_SUBDIR)
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except OSError as exc:
            QgsMessageLog.logMessage(
                f"Cache : impossible de créer le dossier {cache_dir} : {exc}",
                "VoirieCommunale", Qgis.Warning
            )
        return cache_dir

    def _cache_gpkg_path(self, code_insee):
        """Chemin du fichier GeoPackage de cache pour une commune donnée."""
        return os.path.join(self._cache_dir(), f"voirie_{code_insee}.gpkg")

    def _cache_age_days(self, code_insee):
        """Âge du fichier de cache en jours, ou None si le cache est absent."""
        path = self._cache_gpkg_path(code_insee)
        if not os.path.isfile(path):
            return None
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return None
        return (time.time() - mtime) / 86400.0

    def _load_layer_from_cache(self, code_insee, layer_key, display_name):
        """Tente de charger `layer_key` depuis le GeoPackage de cache de `code_insee`.

        Args:
            code_insee: code INSEE de la commune
            layer_key: nom interne de la couche dans le GeoPackage (ex. 'ban')
            display_name: nom d'affichage à donner à la couche QGIS chargée

        Returns:
            QgsVectorLayer valide (nommée display_name) ou None si absente/invalide.
        """
        path = self._cache_gpkg_path(code_insee)
        if not os.path.isfile(path):
            return None
        uri = f"{path}|layername={layer_key}"
        layer = QgsVectorLayer(uri, display_name, "ogr")
        if not layer.isValid() or layer.featureCount() == 0:
            return None
        QgsMessageLog.logMessage(
            f"Cache : {display_name} chargée depuis {os.path.basename(path)} "
            f"({layer.featureCount()} entité(s))",
            "VoirieCommunale", Qgis.Info
        )
        return layer

    def _save_layer_to_cache(self, code_insee, layer_key, layer):
        """Écrit (ou remplace) la couche `layer_key` dans le GeoPackage de `code_insee`.

        Opération best-effort : toute erreur est loguée sans jamais interrompre
        le chargement en cours — le cache n'est qu'une optimisation, jamais
        une dépendance bloquante.

        Returns:
            bool: True si l'écriture a réussi.
        """
        if layer is None or not layer.isValid():
            return False

        path = self._cache_gpkg_path(code_insee)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = layer_key
        options.fileEncoding = "UTF-8"
        if os.path.isfile(path):
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer

        transform_context = QgsProject.instance().transformContext()
        try:
            if hasattr(QgsVectorFileWriter, 'writeAsVectorFormatV3'):
                error = QgsVectorFileWriter.writeAsVectorFormatV3(layer, path, transform_context, options)
            else:
                error = QgsVectorFileWriter.writeAsVectorFormatV2(layer, path, transform_context, options)
            error_code = error[0] if isinstance(error, tuple) else error
        except Exception as exc:  # défensif : une erreur de cache ne doit jamais faire échouer un chargement
            QgsMessageLog.logMessage(
                f"Cache : échec d'écriture de {layer_key} dans {path} : {exc}",
                "VoirieCommunale", Qgis.Warning
            )
            return False

        if error_code != QgsVectorFileWriter.NoError:
            QgsMessageLog.logMessage(
                f"Cache : échec d'écriture de {layer_key} dans {path} (code {error_code})",
                "VoirieCommunale", Qgis.Warning
            )
            return False

        QgsMessageLog.logMessage(
            f"Cache : {layer_key} enregistrée dans {os.path.basename(path)}",
            "VoirieCommunale", Qgis.Info
        )
        return True

    def _reload_layer_from_cache_preserving_style(self, code_insee, layer_key, layer, display_name):
        """Bascule la source de données de `layer` (initialement en provider
        'memory') vers sa version fraîchement écrite dans le GeoPackage de
        cache (provider 'ogr'), afin qu'elle ne soit plus signalée par QGIS
        comme « couche temporaire ».

        Utilise `QgsVectorLayer.setDataSource()` plutôt que de recréer une
        nouvelle couche : il s'agit du même objet QgsVectorLayer (même id,
        même renderer, mêmes labels, jointures, etc.), donc tout le style est
        conservé automatiquement, sans recopie manuelle.

        Best-effort : si le cache est absent/invalide ou si la bascule
        échoue, `layer` est retournée inchangée (le cache reste une
        optimisation, jamais une dépendance bloquante).
        """
        # Vérifie d'abord que le cache est exploitable avant de basculer la
        # source de la couche réelle, pour ne jamais la rendre invalide.
        check = self._load_layer_from_cache(code_insee, layer_key, display_name)
        if check is None:
            return layer

        path = self._cache_gpkg_path(code_insee)
        uri = f"{path}|layername={layer_key}"
        try:
            layer.setDataSource(uri, display_name, "ogr", QgsDataProvider.ProviderOptions())
        except Exception as exc:
            QgsMessageLog.logMessage(
                f"Cache : impossible de basculer la source de {display_name} vers le cache : {exc}",
                "VoirieCommunale", Qgis.Warning
            )
            return layer

        if not layer.isValid():
            QgsMessageLog.logMessage(
                f"Cache : bascule de source invalide pour {display_name}, couche laissée en mémoire",
                "VoirieCommunale", Qgis.Warning
            )
            return layer

        return layer
