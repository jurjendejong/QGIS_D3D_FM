# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Delft3D_FlexibleMesh
                                 A QGIS plugin
 This plugin will provide basic tools for Flexible Mesh
                              -------------------
        begin                : 2017-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Jurjen de Jong, Deltares
        email                : Jurjen.deJong@deltares.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Delft3D_FlexibleMesh_dialog import Delft3D_FlexibleMeshDialog
import os
import shutil
from qgis.core import QGis, QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPoint, QgsMapLayerRegistry, QgsPalLayerSettings, QgsLayerDefinition
from qgis.gui import QgsMessageBar
import tekal as tek
import glob

class Delft3D_FlexibleMesh:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Delft3D_FlexibleMesh_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Delft3D FlexibleMesh Toolbox')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Delft3D_FlexibleMesh')
        self.toolbar.setObjectName(u'Delft3D_FlexibleMesh')

        # default directory
        self.directory = '.'

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Delft3D_FlexibleMesh', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = Delft3D_FlexibleMeshDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Delft3D_FlexibleMesh/icon.png'
        self.add_action(
            icon_path,
            text='Save to .pli/.pol/.xyz',
            callback=self.run_save,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/Delft3D_FlexibleMesh/icon.png'
        self.add_action(
            icon_path,
            text='Open .pli/.pol/.xyz',
            callback=self.run_open_pli,
            parent=self.iface.mainWindow())
            
        icon_path = ':/plugins/Delft3D_FlexibleMesh/icon.png'
        self.add_action(
            icon_path,
            text='Open Baseline tree',
            callback=self.run_open,
            parent=self.iface.mainWindow())
            
        icon_path = ':/plugins/Delft3D_FlexibleMesh/icon.png'
        self.add_action(
            icon_path,
            text='Add Baseline6 tree',
            callback=self.run_open_Baseline6,
            parent=self.iface.mainWindow())
            
        icon_path = ':/plugins/Delft3D_FlexibleMesh/icon.png'
        self.add_action(
            icon_path,
            text='Add FM snapped features',
            callback=self.run_open_grid_snapped,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Delft3D FlexibleMesh Toolbox'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    
    
    def select_output_file(self):
        # Get path of layer in combobox
        selectedLayerIndex=self.dlg.comboBox.currentIndex()
        layers = self.iface.legendInterface().layers()
        selectedLayerPath = layers[selectedLayerIndex].source()
        selectedLayerFilename,ext=os.path.splitext(selectedLayerPath)
        
        # Open and process dialog
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ",selectedLayerFilename + '.ldb', '*.ldb,*.pol,*.pli,*.xyn')
        self.dlg.lineEdit.setText(filename)

    def run_open_pli(self):
        file = QFileDialog.getOpenFileName(self.dlg, "Select pli-file ",self.directory,'*') # .ldb,*.pol,*.pli,*.xyn,*.xyz')
        # file = r'd:\projecten\11200569_Maas_G6\20171114 Deltashell2\files\dflowfm\invoer\j17_5-v1_landboundaries.ldb'
        
        self.directory,filename = os.path.split(file)
        layername,extension = os.path.splitext(filename)
        
        print(layername)
        if extension == '.xyz' or extension == '.xyn':
                    
            vl = QgsVectorLayer("Point", layername, "memory")
            QgsMapLayerRegistry.instance().addMapLayer(vl)
            pr = vl.dataProvider()
            
            # add fields
            
            if extension == 'xyz':
                attribute = 'z'
            else:
                attribute = 'name'
            
            pr.addAttributes([QgsField(attribute, QVariant.String)])
            vl.updateFields() # tell the vector layer to fetch changes from the provider
            
            
            with open(file) as f:
                for line in f:
                    ls = line.strip().split('\t')
                    X = float(ls[0])
                    Y = float(ls[1])
                    Z = ls[2]
                    
                    fet = QgsFeature()
                    fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(X,Y)))
                    fet.setAttributes([Z])
                    pr.addFeatures([fet])
                    
                
            # update layer's extent when new features have been added
            # because change of extent in provider is not propagated to the layer
            vl.updateExtents()
        else:
            D = tek.tekal(file) # initialize
            D.info(file)        # get     file meta-data: all blocks        
            
            
            vl = QgsVectorLayer("LineString", layername, "memory")
            QgsMapLayerRegistry.instance().addMapLayer(vl)
            pr = vl.dataProvider()
            
            attribute = "name"
            
            # add fields
            pr.addAttributes([QgsField(attribute, QVariant.String)])
            vl.updateFields() # tell the vector layer to fetch changes from the provider
            
            for ii in range(len(D.blocks)):
                Name = D.blocks[ii].name
                M = D.read(ii)
                P = []
                for ix in range(len(M[0])):
                    P.append(QgsPoint(M[0][ix],M[1][ix]))
                
                # If line of just one points: duplicate
                if ix == 0:
                    P.append(QgsPoint(M[0][ix]+0.01,M[1][ix]+0.01))
                    
                # add a feature
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolyline(P))

                fet.setAttributes([Name])
                pr.addFeatures([fet])
            
            # update layer's extent when new features have been added
            # because change of extent in provider is not propagated to the layer
            vl.updateExtents()
        
        # Enable labels
        if attribute == 'name':
            label = QgsPalLayerSettings()
            label.readFromLayer(vl)
            label.enabled = True
            label.fieldName = attribute
            label.writeToLayer(vl)

        

        
    def run_save(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
            
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(layer_list)
        
        selectedLayer = layer_list.index(self.iface.activeLayer().name())
        self.dlg.comboBox.setCurrentIndex(selectedLayer)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if not result:
            return

        filename = self.dlg.lineEdit.text()
        # filename = r'D:\Temp\test1.pol'
        
        selectedLayerIndex = self.dlg.comboBox.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        fields = selectedLayer.pendingFields()
        fieldnames = [field.name() for field in fields]
        
        
        if selectedLayer.wkbType() == QGis.WKBPoint:
            print('Processing to xyz')
            output_file = open(filename,'w')
            for f in selectedLayer.getFeatures():
                geomPoint = f.geometry().asPoint()
                line = '{:.3f},{:.3f},'.format(geomPoint.x(),geomPoint.y()) + ','.join(unicode(f[x]) for x in fieldnames) + '\n'
                line = line.encode('utf-8')
                output_file.write(line)
            output_file.close()
        elif selectedLayer.wkbType() == QGis.WKBLineString or selectedLayer.wkbType() == QGis.WKBLineString25D:
            print('Processing to ldb (polyline)')
            output_file = open(filename,'w')
            for iFeature,f in enumerate(selectedLayer.getFeatures()):
                geomLine = f.geometry().asPolyline()
                if len(f.attributes())>0 and f.attributes()[0]:
                    featureName = str(f.attributes()[0]).replace(' ','_')
                else:
                    featureName = 'Feature_{}'.format(iFeature)
                output_file.write(featureName + '\n')
                output_file.write('{} {}\n'.format(len(geomLine),2))  # Space as seperater in Deltashell
                for g in geomLine:
                    output_file.write('{:.3f} {:.3f}\n'.format(g.x(),g.y()))  # Space as seperater in Deltashell
            output_file.close()
        elif selectedLayer.wkbType() == QGis.WKBPolygon:
            print('Processing to ldb (polygon)')
            output_file = open(filename,'w')
            fId=0
            for feature in selectedLayer.getFeatures():
                fpol=feature.geometry().asPolygon()
                for geomLine in fpol:
                    output_file.write('Feature{}\n'.format(fId))
                    output_file.write('{},{}\n'.format(len(geomLine),2))
                    for g in geomLine:
                        output_file.write('{:.3f},{:.3f}\n'.format(g.x(),g.y()))
                    fId+=1
            output_file.close()
        elif selectedLayer.wkbType() == QGis.WKBMultiLineString:
            print('Processing to ldb (multi polyline)')
            output_file = open(filename,'w')
            print('Not tested yet')
            # fId=0
            # for feature in selectedLayer.getFeatures():
                # fpol=feature.geometry().asPolygon()
                # for geomLine in fpol:
                    # output_file.write('Feature{}\n'.format(fId))
                    # output_file.write('{},{}\n'.format(len(geomLine),2))
                    # for g in geomLine:
                        # output_file.write('{:.3f},{:.3f}\n'.format(g.x(),g.y()))
                    # fId+=1
            # output_file.close()
        elif selectedLayer.wkbType() == QGis.WKBMultiPolygon:
            print('Processing to ldb (multi polygon)')
            output_file = open(filename,'w')
            fId=0
            for feature in selectedLayer.getFeatures():
                fpols=feature.geometry().asMultiPolygon()
                for fpol in fpols:
                    for geomLine in fpol:
                        output_file.write('Feature{}\n'.format(fId))
                        output_file.write('{},{}\n'.format(len(geomLine),2))
                        for g in geomLine:
                            output_file.write('{:.3f},{:.3f}\n'.format(g.x(),g.y()))
                        fId+=1
            output_file.close()
        else:
            self.iface.messageBar().pushMessage("Error", 'Type of layer not recognised. wkbType: ' + str(selectedLayer.wkbType()),level=QgsMessageBar.CRITICAL)
        DialogMessageBox('Saving finished')

    def run_open(self):
        # Open Baseline-project with template
        # Supports both: d:\modellen\baseline\Rijn\j15_5-v1\ and d:\modellen\baseline\Rijn\j15_5-v1\baseline.gdb\
        baselinegdb = QFileDialog.getExistingDirectory(self.dlg, "Select baseline gdb-file ",'*.gdb')
        
        if len(baselinegdb)==0:
            return
        
        if not ("baseline.gdb" in baselinegdb):
            baselinegdb=os.path.join(baselinegdb,'baseline.gdb')
        
        if not os.path.isdir(baselinegdb):
            self.iface.messageBar().pushMessage("Error", "Cannot find baseline.gdb in given folder", level=QgsMessageBar.CRITICAL)
            return        
        
        # Copy QGIS-template to folder
        templatefile=r'c:\Users\jong_jn\.qgis2\python\plugins\Delft3D_FlexibleMesh\incl\baseline_template.qgs'
        
        head,tail=os.path.split(baselinegdb)
        qgsfile=os.path.join(head,'baseline.qgs')
        
        shutil.copy(templatefile,qgsfile)
        
        # Open new project
        project = QgsProject.instance()
        project.read(QFileInfo(qgsfile))

        # Zoom to extent
        canvas = self.iface.mapCanvas()
        canvas.zoomToFullExtent()

    def run_open_Baseline6(self):
        # Open Baseline-project with template
        # Supports both: d:\modellen\baseline\Rijn\j15_5-v1\ and d:\modellen\baseline\Rijn\j15_5-v1\baseline.gdb\
        baselinegdb = QFileDialog.getExistingDirectory(self.dlg, "Select baseline gdb-file ", '*.gdb')

        if len(baselinegdb) == 0:
            return

        if not ("baseline.gdb" in baselinegdb):
            baselinegdb = os.path.join(baselinegdb, 'baseline.gdb')

        if not os.path.isdir(baselinegdb):
            self.iface.messageBar().pushMessage("Error", "Cannot find baseline.gdb in given folder", level=QgsMessageBar.CRITICAL)
            return

        templatefile = r'c:\Users\jong_jn\.qgis2\python\plugins\Delft3D_FlexibleMesh\incl\baseline6_layer_template.qlr'

        head, tail = os.path.split(baselinegdb)
        _, baselinedirname = os.path.split(head)
        qlrfile = os.path.join(head, 'baseline6.qlr')

        # shutil.copy(templatefile, qlrfile)
        with open(templatefile, 'r') as fin:
            templatecontent = fin.read()

        # Do adjustments to the templatecontent
        # templatecontent = templetecontent.replace()

        with open(qlrfile, 'w') as fout:
            fout.write(templatecontent)

        root = QgsProject.instance().layerTreeRoot()
        group = root.insertGroup(0,"Baseline6_{}".format(baselinedirname))
        QgsLayerDefinition().loadLayerDefinition(qlrfile, group)

    def run_open_grid_snapped(self):
        snappeddirectory = QFileDialog.getExistingDirectory(self.dlg, "Select snapped directory ")

        allshapefiles = glob.glob(os.path.join(snappeddirectory, '*.shp'))

        print(allshapefiles)
        templatefile = r'c:\Users\jong_jn\.qgis2\python\plugins\Delft3D_FlexibleMesh\incl\snapped.qlr'

        _, dirname = os.path.split(snappeddirectory)
        qlrfile = os.path.join(snappeddirectory, 'snapped.qlr')

        # shutil.copy(templatefile, qlrfile)
        with open(templatefile, 'r') as fin:
            templatecontent = fin.read()

        # Do adjustments to the templatecontent
        # templatecontent = templetecontent.replace()

        with open(qlrfile, 'w') as fout:
            fout.write(templatecontent)

        root = QgsProject.instance().layerTreeRoot()
        group = root.insertGroup(0, "Snapped_{}".format(dirname))
        QgsLayerDefinition().loadLayerDefinition(qlrfile, group)





def DialogMessageBox(message):
    msgBox = QMessageBox()
    msgBox.setText(message)
    ret = msgBox.exec_()