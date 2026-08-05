# -*- coding: utf-8 -*-
"""
Voirie Communale - Symbologie (styles, couleurs, regles de rendu)
Copyright (C) 2026 Yann Schwarz <yann.schwarz@gmail.com>
Licence : GNU GPL v2+

Ce module regroupe la logique de symbologie du plugin : dictionnaires de
couleurs (MAJIC), et methodes appliquant des QgsRuleBasedRenderer / renderers
categorises sur les couches chargees (BD TOPO, BAN, OSM, MagOSM).
"""
from qgis.PyQt.QtGui import QColor
from qgis.core import (Qgis, QgsMessageLog,
                       QgsMarkerSymbol,
                       QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
                       QgsTextBufferSettings)

from .voirie_communale_dialog import SettingsDialog


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


class StylesMixin:
    """Regroupe les methodes de symbologie (styles, couleurs, regles) du plugin."""

    def apply_majic_style(self, layer):
        """Applique le rendu catégorisé MAJIC (par 'groupe_personne') à `layer`.

        Construit les catégories à partir des valeurs de `groupe_personne`
        réellement présentes dans les attributs de la couche (et non depuis
        les données Koumoul brutes), afin de pouvoir être réutilisée aussi
        bien juste après téléchargement que lors d'un chargement depuis le
        cache local (où seule la couche polygone existe, sans accès aux
        données API d'origine).
        """
        from qgis.core import QgsFillSymbol, QgsCategorizedSymbolRenderer, QgsRendererCategory

        if layer.fields().indexOf('groupe_personne') < 0:
            return

        unique_groupes = sorted({
            int(v) for v in layer.uniqueValues(layer.fields().indexOf('groupe_personne'))
            if v is not None
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

    def _apply_bdtopo_troncons_style(self, layer,
                                      regex_chemin=r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b',
                                      regex_voie=r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b'):
        """Style à règles : regex de filtrage (chemin rural / voie communale) en priorité
        sur le champ 'nom_1_gauche', puis catégorisation par 'nature'.
        """
        from qgis.core import (
            QgsRuleBasedRenderer, QgsSymbol,
            QgsLineSymbol
        )

        def make_line(color, width, dash=False):
            props = {'color': color, 'width': str(width)}
            if dash:
                props['line_style'] = 'dash'
            sym = QgsLineSymbol.createSimple(props)
            return sym

        root_rule = QgsRuleBasedRenderer.Rule(None)  # règle racine (conteneur)

        # ---- 1. Regex CR / VC sur nom_collaboratif_gauche (prioritaires) ----
        nom_field = 'nom_collaboratif_gauche'

        rule_cr = QgsRuleBasedRenderer.Rule(make_line('#8C7274', 0.7))
        rule_cr.setLabel('Chemin rural (nom)')
        rule_cr.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_chemin)}') > 0"
            f" OR \"cpx_classement_administratif\" = 'Chemin rural'"
        )
        root_rule.appendChild(rule_cr)

        rule_vc = QgsRuleBasedRenderer.Rule(make_line('#FCF6B5', 0.7))
        rule_vc.setLabel('Voie communale (nom)')
        rule_vc.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_voie)}') > 0"
        )
        root_rule.appendChild(rule_vc)

        # ---- 2. Catégories fusionnées (cpx OR importance OR nature) ----
        # Une seule règle par catégorie sémantique
        cpx_null = "(\"cpx_classement_administratif\" IS NULL OR \"cpx_classement_administratif\" = '')"
        imp_fallback = f"({cpx_null} AND (\"importance\" IS NULL OR \"importance\" >= 5))"

        categories = [
            ('Autoroute',
             "\"cpx_classement_administratif\" = 'Autoroute' OR ({cpx_null} AND \"importance\" = 1)".format(cpx_null=cpx_null),
             '#f26119', 1.4),
            ('Nationale',
             "\"cpx_classement_administratif\" = 'Nationale' OR ({cpx_null} AND \"importance\" = 2)".format(cpx_null=cpx_null),
             '#f2a824', 1.2),
            ('Départementale',
             "\"cpx_classement_administratif\" = 'Départementale' OR ({cpx_null} AND \"importance\" = 3)".format(cpx_null=cpx_null),
             '#F2D7A2', 0.9),
            ('Route intercommunale',
             "\"cpx_classement_administratif\" = 'Route intercommunale'",
             '#2db9fc', 0.8),
            ('Liaison locale',
             "({cpx_null} AND \"importance\" = 4)".format(cpx_null=cpx_null),
             '#FCF0A8', 0.8),
            ('Desserte',
             "({imp_fallback} AND (\"nature\" = 'Route à 1 chaussée' OR \"nature\" = 'Route à 2 chaussées' OR \"nature\" = 'Rond-point'))".format(imp_fallback=imp_fallback),
             '#ededed', 0.7),
            ('Route empierrée',
             "({imp_fallback} AND \"nature\" = 'Route empierrée')".format(imp_fallback=imp_fallback),
             '#7C7C7C', 0.6),
            ('Chemin',
             "({imp_fallback} AND \"nature\" = 'Chemin')".format(imp_fallback=imp_fallback),
             '#8C7274', 0.5),
            ('Sentier',
             "({imp_fallback} AND \"nature\" = 'Sentier')".format(imp_fallback=imp_fallback),
             '#8C7274', 0.4, True),
            ('Bac / Maritime',
             "({imp_fallback} AND \"nature\" = 'Bac ou liaison maritime')".format(imp_fallback=imp_fallback),
             '#5792C2', 0.5),
        ]
        for item in categories:
            label, expr, color, width = item[0], item[1], item[2], item[3]
            dash = item[4] if len(item) > 4 else False
            rule = QgsRuleBasedRenderer.Rule(make_line(color, width, dash))
            rule.setLabel(label)
            rule.setFilterExpression(expr)
            root_rule.appendChild(rule)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        # ---- Étiquettes : champ brut, aucune regex ----
        # Le renderer gère déjà la catégorisation. Le labeling affiche simplement
        # nom_collaboratif_gauche ; QGIS n'affiche rien si le champ est null/vide.
        lbl = QgsPalLayerSettings()
        lbl.isExpression = False
        lbl.fieldName = nom_field
        lbl.enabled = True
        lbl.placement = QgsPalLayerSettings.Line
        fmt = QgsTextFormat()
        fmt.setSize(8)
        fmt.setColor(QColor(0, 0, 0))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.5)
        buf.setColor(QColor(255, 255, 255))
        fmt.setBuffer(buf)
        lbl.setFormat(fmt)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(lbl))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()


    def _apply_bdtopo_routesnom_style(self, layer):
        """Applique une symbologie catégorisée sur 'type_de_route' aux routes BD TOPO nommées."""
        from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol
        color_map = {
            'Autoroute':            '#F2A824',
            'Nationale':            '#F2D7A2',
            'Départementale':       '#FCF5AF',
            'Route intercommunale': '#FCF0A8',
            'Voie communale':       '#FCF6B5',
            'Chemin rural':         '#8C7274',
        }
        categories = []
        for route_type, color in color_map.items():
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(QColor(color))
            categories.append(QgsRendererCategory(route_type, symbol, route_type))
        layer.setRenderer(QgsCategorizedSymbolRenderer('type_de_route', categories))
        layer.triggerRepaint()


    @staticmethod
    def _get_regex_setting(key, default):
        """Lit une regex depuis settings.json, valide, et restaure le défaut si corrompue.

        Args:
            key:     Clé (sans préfixe).
            default: Valeur par défaut (raw string recommandé).

        Returns:
            str: Expression régulière valide.
        """
        import re as _re
        val = SettingsDialog.get(key, default)
        try:
            _re.compile(val)
            return val
        except _re.error:
            QgsMessageLog.logMessage(
                f"Regex corrompue pour '{key}' ({val!r}), restauration du défaut.",
                "VoirieCommunale", Qgis.Warning
            )
            SettingsDialog.set(key, default)   # Réparer settings.json
            return default


    @staticmethod
    def _qgis_expr_regex(regex):
        """Prépare une regex pour intégration dans un littéral de chaîne d'expression QGIS.

        Le parseur d'expressions QGIS interprète les séquences d'échappement standard
        (``\\n``, ``\\t``, ``\\b`` = retour arrière, etc.) dans les chaînes entre guillemets
        simples.  Pour que ``\\b`` ou ``\\.`` soient transmis tels quels au moteur regex Qt,
        il faut les doubler : ``\\\\b`` dans la chaîne Python → ``\\b`` dans l'expression
        QGIS → ``\\b`` reçu par le moteur regex.

        Args:
            regex: Expression régulière Python (ex. ``r'\\bC\\.?R\\.?\\b'``).

        Returns:
            str: Regex avec backslashes doublés, prête à être insérée dans ``'...'``.
        """
        return regex.replace('\\', '\\\\')

    # ------------------------------------------------------------------
    # Méthodes fetch-to-vsimem (background-safe, sans objets QGIS)
    # Utilisées par WfsLoadTask pour le chargement WFS parallèle
    # ------------------------------------------------------------------


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
                "VoirieCommunale",
                Qgis.Warning
            )
            return
        
        # Renderer à règles : chaque règle porte une regex de filtre + un symbole ponctuel.
        # QgsRuleBasedRenderer est préférable à QgsCategorizedSymbolRenderer avec une
        # expression CASE WHEN, car QGIS n'affiche pas l'expression dans la légende.
        from qgis.core import QgsRuleBasedRenderer

        def make_marker(color, outline_color, size='3'):
            return QgsMarkerSymbol.createSimple({
                'name': 'circle', 'color': color, 'size': size,
                'outline_color': outline_color, 'outline_width': '0.5'
            })

        root_rule = QgsRuleBasedRenderer.Rule(None)

        # Chemin rural
        rule_cr = QgsRuleBasedRenderer.Rule(make_marker('#8C7274', '#6B5557'))
        rule_cr.setLabel('Chemin rural')
        rule_cr.setFilterExpression(
            f"regexp_match(\"{field_name}\", '{self._qgis_expr_regex(regex_chemin)}') > 0"
        )
        root_rule.appendChild(rule_cr)

        # Voie communale
        rule_vc = QgsRuleBasedRenderer.Rule(make_marker('#B4B4B4', '#909090'))
        rule_vc.setLabel('Voie communale')
        rule_vc.setFilterExpression(
            f"regexp_match(\"{field_name}\", '{self._qgis_expr_regex(regex_voie)}') > 0"
        )
        root_rule.appendChild(rule_vc)

        # Autre – gris, désactivé par défaut
        rule_autre = QgsRuleBasedRenderer.Rule(make_marker('#808080', '#505050', '2.5'))
        rule_autre.setLabel('Autre')
        rule_autre.setActive(False)
        rule_autre.setIsElse(True)   # s'applique à tout ce qui n'est pas matché
        root_rule.appendChild(rule_autre)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        # ---- Étiquettes : champ brut, aucune regex ----
        # Le renderer gère déjà la catégorisation. Le labeling affiche simplement
        # nom_voie ; QGIS n'affiche rien si le champ est null/vide.
        lbl = QgsPalLayerSettings()
        lbl.isExpression = True
        lbl.fieldName = '"numero" || \' \' || "nom_voie"'
        lbl.enabled = True
        lbl.placement = QgsPalLayerSettings.AroundPoint
        fmt = QgsTextFormat()
        fmt.setSize(8)
        fmt.setColor(QColor(0, 0, 0))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.5)
        buf.setColor(QColor(255, 255, 255))
        fmt.setBuffer(buf)
        lbl.setFormat(fmt)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(lbl))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()
        
        QgsMessageLog.logMessage(
            "Style différencié et étiquettes appliqués à la couche BAN (Chemins ruraux / Voies communales)",
            "VoirieCommunale",
            Qgis.Success
        )
    

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
            ('"ref" LIKE \'CE%\'',                           make_sym('#8C7274', '0.6'), 'CE – Chemin d\'exploitation'),
            ('"ref" LIKE \'C%\' AND "ref" NOT LIKE \'CE%\'', make_sym('#FCF6B5', '0.6'), 'C – Voie communale'),
            ('"ref" LIKE \'R%\'',                            make_sym('#8C7274', '0.6'), 'R – Chemin rural'),
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

    def _apply_magosm_style(self, layer,
                             regex_chemin=r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b',
                             regex_voie=r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b'):
        """Style à règles pour la couche MagOSM highways_line.

        Même structure que BD TOPO tronçons :
        1. Règles regex CR/VC sur le champ 'name' (prioritaires)
        2. Catégorisation par valeur du champ 'highway' (à la place de 'nature')
        """
        from qgis.core import QgsRuleBasedRenderer, QgsLineSymbol

        def make_line(color, width, dash=False):
            props = {
                'color': color, 'width': str(width),
                'capstyle': 'round', 'joinstyle': 'round',
            }
            if dash:
                props['line_style'] = 'dash'
            return QgsLineSymbol.createSimple(props)

        nom_field = 'name'
        root_rule = QgsRuleBasedRenderer.Rule(None)

        # ---- 1. Regex CR / VC (prioritaires) ----
        rule_cr = QgsRuleBasedRenderer.Rule(make_line('#8C7274', 0.7))
        rule_cr.setLabel('Chemin rural (nom)')
        rule_cr.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_chemin)}') > 0"
        )
        root_rule.appendChild(rule_cr)

        rule_vc = QgsRuleBasedRenderer.Rule(make_line('#FCF6B5', 0.7))
        rule_vc.setLabel('Voie communale (nom)')
        rule_vc.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_voie)}') > 0"
        )
        root_rule.appendChild(rule_vc)

        # ---- 2. Catégorisation par champ 'highway' ----
        highway_map = [
            ('Autoroute',            ['motorway', 'motorway_link'],                                    '#f26119', 1.2, False),
            ('Nationale',            ['trunk', 'trunk_link', 'primary', 'primary_link'],               '#f2a824', 1.0, False),
            ('Départementale',       ['secondary', 'secondary_link'],                                 '#F2D7A2', 0.8, False),
            ('Route intercommunale', ['tertiary', 'tertiary_link'],                                    '#2db9fc', 0.7, False),
            ('Desserte',             ['residential', 'service', 'living_street'],                       '#ededed', 0.6, False),
            ('Chemin',               ['track', 'path', 'bridleway'],                                   '#8C7274', 0.5, False),
            ('Sentier',              ['footway', 'steps'],                                             '#8C7274', 0.4, True),
            ('Piste cyclable',       ['cycleway'],                                                     '#9B5CCC', 0.4, False),
        ]
        for label, vals, color, width, dash in highway_map:
            expr = ' OR '.join(f"\"highway\" = '{v}'" for v in vals)
            rule = QgsRuleBasedRenderer.Rule(make_line(color, width, dash))
            rule.setLabel(label)
            rule.setFilterExpression(expr)
            root_rule.appendChild(rule)

        # Règle par défaut
        rule_default = QgsRuleBasedRenderer.Rule(make_line('#969696', 0.4))
        rule_default.setLabel('(autre)')
        rule_default.setIsElse(True)
        root_rule.appendChild(rule_default)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        # ---- Étiquettes : champ 'name' ----
        lbl = QgsPalLayerSettings()
        lbl.isExpression = False
        lbl.fieldName = nom_field
        lbl.enabled = True
        lbl.placement = QgsPalLayerSettings.Line
        fmt = QgsTextFormat()
        fmt.setSize(8)
        fmt.setColor(QColor(0, 0, 0))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.5)
        buf.setColor(QColor(255, 255, 255))
        fmt.setBuffer(buf)
        lbl.setFormat(fmt)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(lbl))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()

        QgsMessageLog.logMessage(
            "Style différencié appliqué à la couche MagOSM (highway)",
            "VoirieCommunale", Qgis.Success
        )

    def apply_edigeo_voies_style(self, layer,
                                  regex_chemin=r'(?i)(che(?:min)?|sen(?:tier)?) rural|\bC\.?R\.?\b',
                                  regex_voie=r'(?i)(voi(?:e)?) (com(?:munale)?)|\bV\.?C\.?\b'):
        """Style à règles pour la couche des voies EDIGEO (ZONCOMMUNI_id) : mêmes
        regex de catégorisation (Chemin rural / Voie communale) que BAN, BD TOPO
        tronçons et MagOSM, appliquées sur le nom complet reconstitué (champ 'nom').

        Args:
            layer: La couche QgsVectorLayer des voies EDIGEO à styliser
            regex_chemin: Expression régulière QGIS pour détecter les chemins ruraux
            regex_voie: Expression régulière QGIS pour détecter les voies communales
        """
        from qgis.core import QgsRuleBasedRenderer, QgsLineSymbol

        def make_line(color, width, dash=False):
            props = {'color': color, 'width': str(width)}
            if dash:
                props['line_style'] = 'dash'
            return QgsLineSymbol.createSimple(props)

        nom_field = 'nom'
        root_rule = QgsRuleBasedRenderer.Rule(None)

        rule_cr = QgsRuleBasedRenderer.Rule(make_line('#8C7274', 0.7, dash=True))
        rule_cr.setLabel('Chemin rural (nom)')
        rule_cr.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_chemin)}') > 0"
        )
        root_rule.appendChild(rule_cr)

        rule_vc = QgsRuleBasedRenderer.Rule(make_line('#FCF6B5', 0.7, dash=True))
        rule_vc.setLabel('Voie communale (nom)')
        rule_vc.setFilterExpression(
            f"regexp_match(\"{nom_field}\", '{self._qgis_expr_regex(regex_voie)}') > 0"
        )
        root_rule.appendChild(rule_vc)

        rule_autre = QgsRuleBasedRenderer.Rule(make_line('#8C7274', 0.4, dash=True))
        rule_autre.setLabel('(autre)')
        rule_autre.setIsElse(True)
        root_rule.appendChild(rule_autre)

        layer.setRenderer(QgsRuleBasedRenderer(root_rule))

        lbl = QgsPalLayerSettings()
        lbl.isExpression = False
        lbl.fieldName = 'nom'
        lbl.enabled = True
        lbl.placement = QgsPalLayerSettings.Line
        fmt = QgsTextFormat()
        fmt.setSize(8)
        fmt.setColor(QColor(0, 0, 0))
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.5)
        buf.setColor(QColor(255, 255, 255))
        fmt.setBuffer(buf)
        lbl.setFormat(fmt)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(lbl))
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()

        QgsMessageLog.logMessage(
            "Style différencié appliqué à la couche Voies EDIGEO (cadastre) (Chemin rural / Voie communale)",
            "VoirieCommunale", Qgis.Success
        )


