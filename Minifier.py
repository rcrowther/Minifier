#!/usr/bin/env python3


'''
'''

## TODO:
# YUI don't like empty JS files



import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
from time import sleep
from gi.repository import Gio, GLib

import glob
from datetime import datetime, date, time
import os.path
import shutil




'''
Minify CSS and JS resources.

Needs YUI compressor.
Needs GSettings schema installing.

Requires: YUI jar, GNU Tools (cat, rm)
'''
# sudo cp /.../minifier.gschema.xml /usr/share/glib-2.0/schemas/
# sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

## TODO
# Spinner jambed
# Store if to start with js or css, settings bind...
# Not saving basename target prefs?
# support slimmer





#################
### User Data ###
#################

GSCHEMA = "uk.co.archaicgroves.minifier"
#CSS_KEY = 'current-css'
#JS_KEY = 'current-js'
DATA_KEY = 'data'
# Used if files are concatenated - if only one name, 
# the name is changed to <basename>-min.css
DEFAULT_CSS_BASENAME = 'site-min.css'
# Used if files are concatenated - if only one name, 
# the name is changed to <basename>-min.js
DEFAULT_JS_BASENAME = 'site-min.js'

# a(cssPath, jsPath, convPath, tmpFilePath)
DATA_SIGNATURE = "a(ssss)"


TMP_FILE_BASENAME = '.minifier.tmp'



############
# Internal #
############

       
       
def baseNameList(
    route,
    excludeSuffix,
    extension
    ):
        
    if(not os.path.isdir(route)):
        return None;
    else:
        gPath = os.path.join(route, '*.' + extension)
        pList = glob.glob(gPath)
        l = []
        for p in pList:
            if (not p.endswith(excludeSuffix) and not os.path.isdir(p)):
                l.append(os.path.basename(p))
        l.sort()
        return l
        
def cssBaseNameList(route):
    return baseNameList(route, 'min.css', 'css')
        
def jsBaseNameList(route):
    return baseNameList(route, 'min.js', 'js')
        
        

def _concatFiles(sourcePaths, tmpPath):
    success = False
    try:
        with open(tmpPath, "w") as outfile:
            for src in sourcePaths:
                shutil.copyfileobj(open(src), outfile)
        success = True
    except IOError as e:
        print(e)
    return success
    
def _yuiMinify(execPath, srcPath, dstPath, isCSS):
    tpe = "css" if (isCSS) else "js"
    success = False
    cmd = ['java', '-jar', execPath, "--type", tpe, "-o", dstPath, srcPath]
    #print(cmd)
    try:
        subprocess.call(cmd)
        success = True
    except Exception as e:
        print(e)
    return success
           
           
           
            
                    
class MyWindow(Gtk.Window):

    isCSSPopulated = True

    ## GUI mods/accessors
    
    def message(self, message):
        self.statusbar.set_text(message)

    def request(self, message):
        msg = '[<span foreground="blue">request</span>] ' + message 
        self.statusbar.set_markup(msg)
        
    def warning(self, message):
        msg = '[<span foreground="orange">warning</span>] ' + message 
        self.statusbar.set_markup(msg)
        
    def error(self, message):
        msg = '[<span foreground="red">error</span>] <span foreground="red">' + message + '</span>'
        self.statusbar.set_markup(msg)

    def clearStatus(self):
        self.statusbar.set_text('')
    
    def spinnerStop(self):
        self.spinner.stop()
        #self.spinner.hide()
            
    def spinnerStart(self):
        self.spinner.start()
        #self.spinner.show()
        
    def tmpFilePath(self):
        '''@returna path to a file location suitable for storing a temporary file
        '''
        tmpFilePath = self.tmpPath.get_text()
        t = tmpFilePath if (tmpFilePath) else  os.path.dirname(self.converterPath.get_text())
        return os.path.join(t, TMP_FILE_BASENAME)
        
    def getSelected(self):
        return [row[1] for row in self.store if (row[0])]
        

    def minifyingPaths(self):
        ''' Rough test that all is ok with the executable and source paths.
        Used before minify, and on window init.
        '''
        srcDir = ''
        if (self.isCSSPopulated):
            srcDir = self.cssPath.get_text()
        else:
            srcDir = self.jsPath.get_text()
            
        if (not os.path.isdir(srcDir)):
            self.warning("source directory not readable?")
            return None
        else:
            execPath = self.converterPath.get_text()
            if (not os.path.isfile(execPath)):
                self.warning("executable not accessable?")
                return None
            else:
                return (execPath, srcDir)
                
          
        
    ## GSettings
    
    def saveSettings(self):
        cssPathStr = self.cssPath.get_text()
        jsPathStr = self.jsPath.get_text()
        converterPathStr =  self.converterPath.get_text()
        tmpPathStr = self.tmpPath.get_text()
        
        data = [(cssPathStr, jsPathStr, converterPathStr, tmpPathStr)]
        gsettingBackups = GLib.Variant(DATA_SIGNATURE, data)
        gsettings.set_value(DATA_KEY, gsettingBackups)
        
    def loadSettings(self):
        #savedNames = gsettings.get_string(settingsKey).split(':')
        gsettingData = gsettings.get_value(DATA_KEY)
        if (len(gsettingData) == 0):
            self.message('no settings found')
        else:
            # Currently preset to load the first backup project
            #for group in gsettingRet:
            datum = gsettingData[0]
            #print(': ' + datum[0])
            #print(': ' + datum[1])

            self.cssPath.set_text(datum[0])
            self.jsPath.set_text(datum[1])
            self.converterPath.set_text(datum[2])
            self.tmpPath.set_text(datum[3])


        
    def cssPopulate(self):
        self.store.clear()
        p = self.cssPath.get_text()
        if ( not os.path.isdir(p) ):
            self.warning("Can not read path: {0}".format(p))
        else:
            l = cssBaseNameList(p)
            if (len(l) == 0):
                self.message("no files found in CSS folder?")
            else:
                for e in l:
                    self.store.append((False, e))
                #self.message("CSS files found")
        self.isCSSPopulated = True

            
    def jsPopulate(self):
        self.store.clear()
        p = self.jsPath.get_text()
        if ( not os.path.isdir(p) ):
            self.warning("Can not read path: {0}".format(p))
        else:
            l = jsBaseNameList(p)
            if (len(l) == 0):
                self.message("no files found in JS folder?")
            else:
                for e in jsBaseNameList(p):
                    self.store.append(e)
                #self.message("JS files found")
        self.isCSSPopulated = False

 
    def _on_list_toggle(self, renderer, path):
        it = self.store.get_iter(path) 
        currentVal = self.store.get_value(it, 0)
        self.store.set_value(it, 0, not currentVal)
       
       
      
                
    ## Actions
               
    def _onclick_cssjs(self, widget):
        self.clearStatus()
        self.jsPopulate() if (self.isCSSPopulated) else self.cssPopulate()
             
             
    def _minify(self, widget):
        self.clearStatus()
        sourceList = self.getSelected()
        
        if (len(sourceList) < 1):
            self.warning("no files to minify?")
        else:
            paths = self.minifyingPaths()
            if (paths is None):
                return
            
            execPath, srcDir  = paths

            # Decide a basename (generic for concatenated files, 
            # modified for a single file)
            dstBaseName = 'Unnamed'
            if (len(sourceList) == 1):
                bn = sourceList[0]
                if (self.isCSSPopulated):
                    dstBaseName = bn[0: len(bn) - 4] + '-min.css'
                else:
                    dstBaseName = bn[0: len(bn) - 3] + '-min.js' 
            else:
                dstBaseName = DEFAULT_CSS_BASENAME if (self.isCSSPopulated) else DEFAULT_JS_BASENAME

            # Concatenate the files
            self.spinnerStart()

            # rejoin source basenames to the full path
            sourcePathList = [os.path.join(srcDir, bn) for bn in sourceList]
            #print("srcs: "+  ' '.join(sourcePathList))
            tmpFilePath = self.tmpFilePath()
            success = _concatFiles(sourcePathList, tmpFilePath)

            if (not success):
                self.error("Unable to concatenate source files?")
                os.remove(tmpFilePath)
                self.spinnerStop()
                return False
            else:
                # Minify
                dstPath = os.path.join(srcDir, dstBaseName)
                success = _yuiMinify(execPath, tmpFilePath, dstPath, self.isCSSPopulated)

                #_cleanTmp
                os.remove(tmpFilePath) 
                self.spinnerStop()
            
                if (not success):
                    self.error("Unable to minify files?")
                else:
                    self.message("minified to {0}".format(dstBaseName))



    ## Widgets

    def actionPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
        
        # Model
        self.store = Gtk.ListStore(bool, str)

        # View
        self.listView = Gtk.TreeView(self.store)
        box.pack_start(self.listView, True, True, 0)
        
        r = Gtk.CellRendererToggle()
        # select = tree.get_selection()
        r.connect("toggled", self._on_list_toggle)
        self.toggleColumn = Gtk.TreeViewColumn("Minify?", r, active=0)
        self.listView.append_column(self.toggleColumn)


        self.nameColumn = Gtk.TreeViewColumn("BaseName", Gtk.CellRendererText(), text=1)
        self.listView.append_column(self.nameColumn)
        self.nameColumn.set_sort_column_id(1)
        
        buttonbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        buttonbox.set_homogeneous(False)
        box.pack_start(buttonbox, False, True, 0)
        
        self.button1 = Gtk.Button(label="Minify")
        self.button1.connect("clicked", self._minify)
        buttonbox.pack_start(self.button1, True, True, 0)
        
        self.button2 = Gtk.Button(label="CSS/JS")
        self.button2.connect("clicked", self._onclick_cssjs)
        buttonbox.pack_start(self.button2, True, True, 0)
        
        return box
        
        

    def _selectCSSFolder(self, widget):
            dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 "Select", Gtk.ResponseType.OK))
            dialog.set_default_size(800, 400)
    
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                self.cssPath.set_text(path)
                self.cssPopulate()
            elif response == Gtk.ResponseType.CANCEL:
                self.message('Selection cancelled')
    
            dialog.destroy()
            
            
    def _selectJSFolder(self, widget):
            dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 "Select", Gtk.ResponseType.OK))
            dialog.set_default_size(800, 400)
    
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                self.jsPath.set_text(path)
                self.jsPopulate()
            elif response == Gtk.ResponseType.CANCEL:
                self.message('Selection cancelled')
    
            dialog.destroy()
            
    def _selectConverterFile(self, widget):
            dialog = Gtk.FileChooserDialog("Please choose an executable", self,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 "Select", Gtk.ResponseType.OK))
            dialog.set_default_size(800, 400)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                self.converterPath.set_text(path)
                # TODO: test
                self.message('New converter')
            elif response == Gtk.ResponseType.CANCEL:
                self.message('Selection cancelled')
    
            dialog.destroy()
       
    def _selectTmpFolder(self, widget):
            dialog = Gtk.FileChooserDialog("Please choose a folder", self,
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 "Select", Gtk.ResponseType.OK))
            dialog.set_default_size(800, 400)
    
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                path = dialog.get_filename()
                self.tmpPath.set_text(path)
                #TODO: test
                self.message('New temporary file folder')
            elif response == Gtk.ResponseType.CANCEL:
                self.message('Selection cancelled')
    
            dialog.destroy()
            
    def settingsPage(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_homogeneous(False)
        
        cssLabel = Gtk.Label()
        cssLabel.set_markup ("<b>CSS directory</b>")
        cssLabel.set_halign(Gtk.Align.START)  
        box.pack_start(cssLabel, False, True, 0)
        
        selectCSSButton = Gtk.Button(label="Select CSS directory")
        selectCSSButton.connect("clicked", self._selectCSSFolder)
        box.pack_start(selectCSSButton, False, True, 0)
        
        self.cssPath = Gtk.Entry()
        self.cssPath.set_margin_bottom(8)
        box.pack_start(self.cssPath, False, True, 0)
        
        
        
        jsLabel = Gtk.Label()
        jsLabel.set_markup ("<b>JS directory</b>")
        jsLabel.set_halign(Gtk.Align.START)  
        box.pack_start(jsLabel, False, True, 0)
        
        selectJSButton = Gtk.Button(label="Select JS directory")
        selectJSButton.connect("clicked", self._selectJSFolder)
        box.pack_start(selectJSButton, False, True, 0)
        
        self.jsPath = Gtk.Entry()
        self.jsPath.set_margin_bottom(8)
        box.pack_start(self.jsPath, False, True, 0)
        
        
        convLabel = Gtk.Label()
        convLabel.set_markup ("<b>Converter path</b>")
        convLabel.set_halign(Gtk.Align.START)
        box.pack_start(convLabel, False, True, 0)

        selectConvButton = Gtk.Button(label="Select converter executable")
        selectConvButton.connect("clicked", self._selectConverterFile)
        box.pack_start(selectConvButton, False, True, 0)
        
        self.converterPath = Gtk.Entry()
        self.converterPath.set_margin_bottom(8)
        box.pack_start(self.converterPath, False, True, 0)
        
        
        tmpLabel = Gtk.Label()
        tmpLabel.set_markup("<b>Temporary directory</b>\n<i>if empty, uses the folder containing the converter</i>")
        tmpLabel.set_halign(Gtk.Align.START)
        box.pack_start(tmpLabel, False, True, 0)
        
        selectTmpButton = Gtk.Button(label="Select temporary file directory")
        selectTmpButton.connect("clicked", self._selectTmpFolder)
        box.pack_start(selectTmpButton, False, True, 0)
        
        self.tmpPath = Gtk.Entry()
        #self.tmpPath.set_editable(False)
        self.tmpPath.set_margin_bottom(8)
        box.pack_start(self.tmpPath, False, True, 0)        
        
        return box
        
        
        
    def __init__(self):
        Gtk.Window.__init__(self, title="Minifier")
        self.set_border_width(10)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_homogeneous(False)
        self.add(box)

        
        self.notebook = Gtk.Notebook()
        box.pack_start(self.notebook, True, True, 0)

        page1 =  self.actionPage()
        page1.set_border_width(10)
        self.notebook.append_page(page1, Gtk.Label('Action'))
        
        page2 =  self.settingsPage()
        page2.set_border_width(10)
        self.notebook.append_page(page2, Gtk.Label('Settings'))
        
        separator = Gtk.Separator()
        box.pack_start(separator, False, True, 4)
        
        statusbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        statusbox.set_homogeneous(False)

        self.spinner = Gtk.Spinner()
        statusbox.pack_start(self.spinner, False, True, 0)
        
        self.statusbar = Gtk.Label()
        statusbox.pack_start(self.statusbar, False, True, 0)
        
        box.pack_start(statusbox, True, True, 0)
    


    






def end(widget, event):
    widget.saveSettings()
    Gtk.main_quit()
        
# settings for last used files
gsettings = Gio.Settings.new(GSCHEMA)

win = MyWindow()
win.connect("delete-event", end)
win.show_all()

# reset gui
win.spinnerStop()
win.loadSettings()

# populate
#self.jsPopulate()
win.cssPopulate()

# Test main path settings
win.minifyingPaths()

Gtk.main()
