# -*- coding: utf-8 -*-
"""
Voirie Communale - Point d'entrée du plugin QGIS
Copyright (C) 2026 Yann Schwarz <yann.schwarz@ign.fr>
Licence : GNU GPL v2+
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VoirieCommunale class from file VoirieCommunale.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .voirie_communale import VoirieCommunale
    return VoirieCommunale(iface)
