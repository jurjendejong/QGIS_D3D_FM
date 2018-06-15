# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Delft3D_FlexibleMesh
                                 A QGIS plugin
 This plugin will provide basic tools for Flexible Mesh
                             -------------------
        begin                : 2017-04-10
        copyright            : (C) 2017 by Jurjen de Jong, Deltares
        email                : Jurjen.deJong@deltares.nl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Delft3D_FlexibleMesh class from file Delft3D_FlexibleMesh.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Delft3D_FlexibleMesh import Delft3D_FlexibleMesh
    return Delft3D_FlexibleMesh(iface)
