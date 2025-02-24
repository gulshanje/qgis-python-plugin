# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HelloCGI
                                 A QGIS plugin
 First plugin for demo assignment
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-06-02
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Gul
        email                : gul.rajput.official@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog  
from qgis.core import QgsProject, QgsVectorFileWriter
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .hello_cgi_dialog import HelloCGIDialog
import os.path
import csv

class HelloCGI:
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

        self.hello_cgi_dialogue = HelloCGIDialog()
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HelloCGI_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.allLayers= []
        self.layersName = []
        self.fields_array = []
        self.layer_name = []
        self.checked_field = []
        self.fieldName = []
        self.export_filename = ""
        self.layer_source = ""
        self.layer_CRS_id = ""
        self.layer_CRS_description = ""
        self.menu = self.tr(u'&HelloCgi')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('HelloCGI', message)


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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/hello_cgi/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Say Hello to CGI'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        # ---

        # will be set False in run()
        self.first_start = True


    @staticmethod
    def __hello_cgi():
        print("Hello CGI Interviewer")

    def _load_fields(self, index=0):
        provider = self.allLayers[index].dataProvider()
        fieldName = [field.name() for field in provider.fields()]
        self.fieldName_array = str(fieldName)

        self.hello_cgi_dialogue.mComboBox.addItems(fieldName)
        
        crs_authId = provider.crs().authid()
        crs_description = provider.crs().description()
        self.hello_cgi_dialogue.idLabel.setText(crs_authId)
        self.hello_cgi_dialogue.descriptionLabel.setText(crs_description)
        self.checked_field = self.hello_cgi_dialogue.mComboBox.currentText()
        current_data = self.hello_cgi_dialogue.mComboBox.currentData()
        
    def _layer_change(self):
        self.hello_cgi_dialogue.mComboBox.clear()
        index = self.hello_cgi_dialogue.comboBox.currentIndex()
        self._load_fields(index)

    def updateFields(self):
        
        self.layer_name = self.hello_cgi_dialogue.mComboBox.currentText()
        self.layer_name = self.layer_name.split(", ")
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&HelloCgi'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):  
        filename, _filter = QFileDialog.getSaveFileName(  
            self.hello_cgi_dialogue, "Select output filename and destination","", '*.csv')  
        self.hello_cgi_dialogue.lineEdit.setText(filename) 
        self.export_filename = filename

    def _export_file_csv(self):
        outFolder = r'C:/Practice/'
        filename = 'as.csv'
        outPath = f"{outFolder}{filename}"
        index = self.hello_cgi_dialogue.comboBox.currentIndex()
        header = [field.name() for field in self.allLayers[index].fields()]
        current_data = self.hello_cgi_dialogue.mComboBox.currentData()
        columns= self.layer_name #['id','name']
        attrib = []
        for f in self.allLayers[index].getFeatures():
            attrs = [f[column] for column in columns]
            attrib.append(attrs)
        
        export_file_folder = outPath
        if self.export_filename:
            export_file_folder = self.export_filename
        else:
            export_file_folder = outPath
            
        with open(export_file_folder, 'w', encoding='UTF8', newline='') as f:

            writer = csv.writer(f)

            writer.writerow(header)
            for field in attrib:
                writer.writerow(field)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            #self.dlg = HelloCGIDialog()
            self.hello_cgi_dialogue.pushButton.clicked.connect(self.select_output_file) 
            self.hello_cgi_dialogue.exportButton.clicked.connect(self._export_file_csv)

        for layer in QgsProject.instance().mapLayers().values():
            self.layersName.append(layer.name())
            self.allLayers.append(layer)
        self.hello_cgi_dialogue.comboBox.addItems(self.layersName)
        self._load_fields()
        self._export_file_csv()

        self.hello_cgi_dialogue.comboBox.currentIndexChanged.connect(self._layer_change)

        self.hello_cgi_dialogue.mComboBox.currentTextChanged.connect(self.updateFields) 
        self.hello_cgi_dialogue.show()
        # Run the dialog event loop
        result = self.hello_cgi_dialogue.exec_()

        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            
