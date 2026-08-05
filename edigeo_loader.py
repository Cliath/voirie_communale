# -*- coding: utf-8 -*-
"""
Voirie Communale - Chargement des voies EDIGEO (plan cadastral vecteur)
Copyright (C) 2026 Yann Schwarz <yann.schwarz@gmail.com>
Licence : GNU GPL v2+

Ce module charge les voies (ZONCOMMUNI_id) du plan cadastral informatisé au
format EDIGEO, distribué par section cadastrale sur cadastre.data.gouv.fr.
Toutes les sections de la commune sont téléchargées, décompressées en
mémoire (/vsimem) puis fusionnées en une couche communale unique. Le nom de
voie, fragmenté sur plusieurs champs (TEX, TEX2...TEX10), est reconstitué en
un seul attribut avant l'ajout au projet.

Note : la couche VOIEP_id du même format mélange en réalité des toponymes
divers (lieux-dits, bâtiments remarquables, points cotés d'altitude, repères
géodésiques) sans champ permettant de les distinguer des noms de voie —
elle n'est donc pas exploitée ici.
"""
import io
import os
import tarfile
import urllib.error
import urllib.request
import zipfile

from qgis.core import (QgsFeature, QgsGeometry, QgsMessageLog, Qgis,
                       QgsProject, QgsVectorLayer)


# Champs texte à concaténer, dans l'ordre, pour reconstituer le nom complet
# fragmenté par le format EDIGEO (limite historique de longueur de chaîne)
EDIGEO_NAME_FIELDS = ['TEX', 'TEX2', 'TEX3', 'TEX4', 'TEX5', 'TEX6', 'TEX7', 'TEX8', 'TEX9', 'TEX10']

# Le plan cadastral vecteur est diffusé en projection Lambert-93 (paramètres
# proj4 identiques à EPSG:2154) mais sans code d'autorité EPSG dans les
# fichiers EDIGEO eux-mêmes ; on force donc explicitement ce CRS connu.
EDIGEO_CRS = 'EPSG:2154'


class EdigeoLoaderMixin:
    """Chargement des voies du plan cadastral EDIGEO
    (cadastre.data.gouv.fr/bundler/pci-vecteur), en complément des sources
    WFS/OSM/BD TOPO existantes.
    """

    EDIGEO_BASE_URL = "https://cadastre.data.gouv.fr/bundler/pci-vecteur/communes/{code_insee}/edigeo"

    @staticmethod
    def _edigeo_reconstruct_name(ogr_feature, field_names):
        """Concatène les champs TEX, TEX2..TEX10 non vides pour reconstituer le nom complet."""
        parts = []
        for field in EDIGEO_NAME_FIELDS:
            if field in field_names:
                value = ogr_feature.GetField(field)
                if value:
                    parts.append(str(value).strip())
        return ' '.join(parts)

    def load_edigeo_voies(self, code_insee, regex_chemin=None, regex_voie=None):
        """Télécharge et fusionne la couche EDIGEO ZONCOMMUNI_id (voies, lignes)
        pour toutes les sections cadastrales d'une commune.

        Args:
            code_insee: Code INSEE de la commune (5 caractères)
            regex_chemin: Expression régulière QGIS pour détecter les chemins ruraux
                (transmise à apply_edigeo_voies_style ; défaut de la méthode si None)
            regex_voie: Expression régulière QGIS pour détecter les voies communales
                (transmise à apply_edigeo_voies_style ; défaut de la méthode si None)

        Returns:
            tuple: (bool succès, QgsVectorLayer voies ou None, bool aucune_donnee)
        """
        from osgeo import gdal, ogr

        url = self.EDIGEO_BASE_URL.format(code_insee=code_insee)
        QgsMessageLog.logMessage(
            f"EDIGEO : téléchargement du plan cadastral vecteur pour {code_insee}",
            "VoirieCommunale", Qgis.Info
        )

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'QGIS-VoirieCommunale/1.0'})
            with urllib.request.urlopen(req, timeout=180) as response:
                zip_bytes = response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                QgsMessageLog.logMessage(
                    f"EDIGEO : aucune donnée disponible pour {code_insee} (404)",
                    "VoirieCommunale", Qgis.Warning
                )
                return False, None, True
            QgsMessageLog.logMessage(f"EDIGEO : erreur HTTP {e.code} : {e}", "VoirieCommunale", Qgis.Critical)
            return False, None, False
        except (urllib.error.URLError, OSError) as e:
            QgsMessageLog.logMessage(f"EDIGEO : erreur de téléchargement : {e}", "VoirieCommunale", Qgis.Critical)
            return False, None, False

        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
        except zipfile.BadZipFile as e:
            QgsMessageLog.logMessage(f"EDIGEO : archive ZIP invalide : {e}", "VoirieCommunale", Qgis.Critical)
            return False, None, False

        section_members = [n for n in zf.namelist() if n.lower().endswith('.tar.bz2')]
        if not section_members:
            QgsMessageLog.logMessage(
                f"EDIGEO : aucune section cadastrale trouvée pour {code_insee}",
                "VoirieCommunale", Qgis.Warning
            )
            return False, None, True

        voies_features = []   # (QgsGeometry, nom)
        vsimem_dir = f"/vsimem/edigeo_{code_insee}"

        for member_name in section_members:
            try:
                tar_bytes = zf.read(member_name)
                tf = tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:bz2')
            except (tarfile.TarError, OSError) as e:
                QgsMessageLog.logMessage(
                    f"EDIGEO : section illisible ({member_name}) : {e}",
                    "VoirieCommunale", Qgis.Warning
                )
                continue

            section_id = os.path.splitext(os.path.splitext(os.path.basename(member_name))[0])[0]
            section_dir = f"{vsimem_dir}/{section_id}"
            written_paths = []
            thf_path = None

            try:
                for ti in tf.getmembers():
                    if not ti.isfile():
                        continue
                    extracted = tf.extractfile(ti)
                    if extracted is None:
                        continue
                    data = extracted.read()
                    path = f"{section_dir}/{os.path.basename(ti.name)}"
                    gdal.FileFromMemBuffer(path, data)
                    written_paths.append(path)
                    if ti.name.upper().endswith('.THF'):
                        thf_path = path

                if not thf_path:
                    continue

                ds = ogr.Open(thf_path)
                if ds is None:
                    continue

                zoncommuni = ds.GetLayerByName('ZONCOMMUNI_id')
                if zoncommuni is not None:
                    field_names = [
                        zoncommuni.GetLayerDefn().GetFieldDefn(i).GetName()
                        for i in range(zoncommuni.GetLayerDefn().GetFieldCount())
                    ]
                    zoncommuni.ResetReading()
                    for feat in zoncommuni:
                        geom_ref = feat.GetGeometryRef()
                        if geom_ref is None:
                            continue
                        geom = QgsGeometry.fromWkt(geom_ref.ExportToWkt())
                        if geom.isNull() or geom.isEmpty():
                            continue
                        geom.convertToMultiType()
                        nom = self._edigeo_reconstruct_name(feat, field_names)
                        voies_features.append((geom, nom))

                ds = None
            finally:
                for p in written_paths:
                    gdal.Unlink(p)

        if not voies_features:
            QgsMessageLog.logMessage(
                f"EDIGEO : aucune voie trouvée pour {code_insee}",
                "VoirieCommunale", Qgis.Warning
            )
            return False, None, True

        voies_layer = self._edigeo_build_layer(
            voies_features, f"MultiLineString?crs={EDIGEO_CRS}&field=nom:string",
            f"Voies EDIGEO (cadastre) {code_insee}"
        )
        if voies_layer:
            style_kwargs = {}
            if regex_chemin is not None:
                style_kwargs['regex_chemin'] = regex_chemin
            if regex_voie is not None:
                style_kwargs['regex_voie'] = regex_voie
            self.apply_edigeo_voies_style(voies_layer, **style_kwargs)
            self._remove_layers_by_name(f"Voies EDIGEO (cadastre) {code_insee}")
            QgsProject.instance().addMapLayer(voies_layer, False)
            QgsProject.instance().layerTreeRoot().addLayer(voies_layer)

        QgsMessageLog.logMessage(
            f"EDIGEO : {len(voies_features)} voie(s) chargée(s) pour {code_insee}",
            "VoirieCommunale", Qgis.Success
        )
        return True, voies_layer, False

    @staticmethod
    def _edigeo_build_layer(features_in, uri, layer_name):
        """Construit une couche mémoire à partir d'une liste de (QgsGeometry, nom)."""
        if not features_in:
            return None
        layer = QgsVectorLayer(uri, layer_name, "memory")
        provider = layer.dataProvider()
        feats = []
        for geom, nom in features_in:
            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([nom])
            feats.append(feat)
        provider.addFeatures(feats)
        layer.updateExtents()
        return layer
