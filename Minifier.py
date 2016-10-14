#!/usr/bin/env python3


'''
'''

## TODO:
# YUI don't like empty files



import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
from time import sleep
from gi.repository import Gio, GLib

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
# More protextion
# Store if to start with js or css
# Replace shell 'file list' with simple Python methods?



#################
### User Data ###
#################

# Route to YUI
YUI_BASENAME="yuicompressor-2.4.8.jar"
# For storage of temporary files
YUI_DIR="/home/rob/Deployed/"
CSS_DIR='/home/rob/websites/archaic_groves/css/'
JS_DIR='/home/rob/websites/archaic_groves/js/'
GSCHEMA = "uk.co.archaicgroves.minifier"
CSS_KEY = 'current-css'
JS_KEY = 'current-js'
# Used if files are concatenated - if only one name, 
# the name is changed to <basename>-min.css
DEFAULT_CSS_BASENAME = 'site-min.css'
# Used if files are concatenated - if only one name, 
# the name is changed to <basename>-min.js
DEFAULT_JS_BASENAME = 'site-min.js'

    
    
############
# Internal #
############         
TMP_PATH =  os.path.join(YUI_DIR + "yuicompressor.tmp")  
YUI_PATH=os.path.join(YUI_DIR + YUI_BASENAME)


        
       
class MyWindow(Gtk.Window):

    isCSSPopulated = True


        
    def saveSettings(self, srcList):
        key = CSS_KEY if (self.isCSSPopulated) else JS_KEY
        gsettings.set_string(key, ':'.join(srcList))

    def baseNameList(self,
        settingsKey,
        route,
        defaultBasename,
        excludeExtension,
        extension
        ):
        savedNames = gsettings.get_string(settingsKey).split(':')
                
        if(not os.path.isdir(route)):
            self.message("Source path not exists {0}".format(route))
            return [];
        else:
            # ls -xA <routes>
            # -1 = by line, -A= don't add implied '.' or '..',
            # -B = ignore backups
            cmd = ['ls', '-1AB', route]
    
            try:
                ret = subprocess.check_output(cmd)
            except:
                ret = b''
            
            currentNames = ret.decode('UTF-8')
            currentList = currentNames.split('\n')
            # Filter empty elements
            currentList =  [e for e in currentList if (e and not e.endswith(excludeExtension) and e.endswith(extension))]
            # Make pairs. If saved names exist, toggle True, else false.
            l = map(lambda e: [e in savedNames, e], currentList)
            return l
        
    def cssBaseNameList(self):
        return self.baseNameList(CSS_KEY, CSS_DIR, DEFAULT_CSS_BASENAME, 'min.css', '.css')

    def jsBaseNameList(self):
        return self.baseNameList(JS_KEY, JS_DIR, DEFAULT_JS_BASENAME, 'min.js', '.js')
        
        
    def cssPopulate(self):
        self.store.clear()
        for e in self.cssBaseNameList():
            self.store.append(e)
        self.isCSSPopulated = True

            
    def jsPopulate(self):
        self.store.clear()
        for e in self.jsBaseNameList():
            self.store.append(e)
        self.isCSSPopulated = False

    def message(self, message):
        self.statusbar.pop(self.statusbarContext)
        self.statusbar.push(self.statusbarContext, message)

    def clearStatus(self):
        self.statusbar.remove_all(self.statusbarContext)

        
    def _on_list_toggle(self, renderer, path):
        it = self.store.get_iter(path) 
        currentVal = self.store.get_value(it, 0)
        self.store.set_value(it, 0, not currentVal)
            
    def __init__(self):
        Gtk.Window.__init__(self, title="Minifier")
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.set_homogeneous(False)
        self.add(self.box)
        
        # Model
        self.store = Gtk.ListStore(bool, str)



        # View
        self.listView = Gtk.TreeView(self.store)
        r = Gtk.CellRendererToggle()
        # select = tree.get_selection()
        r.connect("toggled", self._on_list_toggle)
        self.toggleColumn = Gtk.TreeViewColumn("Minify?", r, active=0)
        self.listView.append_column(self.toggleColumn)


        self.nameColumn = Gtk.TreeViewColumn("BaseName", Gtk.CellRendererText(), text=1)
        self.listView.append_column(self.nameColumn)
        self.nameColumn.set_sort_column_id(1)
        self.box.pack_start(self.listView, True, True, 0)

        self.spinner = Gtk.Spinner()
        self.box.pack_start(self.spinner, True, True, 0)
        
        buttonbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonbox.set_homogeneous(False)
        self.box.pack_start(buttonbox, True, True, 0)
        
        self.button1 = Gtk.Button(label="Minify")
        self.button1.connect("clicked", self._minify)
        buttonbox.pack_start(self.button1, True, True, 0)
        
        self.button2 = Gtk.Button(label="CSS/JS")
        self.button2.connect("clicked", self._onclick_cssjs)
        buttonbox.pack_start(self.button2, True, True, 0)

        self.statusbar = Gtk.Statusbar()
        self.statusbarContext = self.statusbar.get_context_id("minifier")
        self.box.pack_start(self.statusbar, False, True, 0)

        # Now built, test YUI, then populate
        if(not os.path.exists(YUI_PATH)):
            self.message("YUI not acessible? {0}".format(YUI_PATH))
        
        #self.jsPopulate()
        self.cssPopulate()
        
        


    def _minify(self, widget):
        self.clearStatus()
        sourceList = self.getSelected()
        if (len(sourceList) > 0):
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

            route = CSS_DIR if (self.isCSSPopulated) else JS_DIR
            
            #print("sourceList: "+  ','.join(sourceList))
            #print("tmpPath: "+  TMP_PATH)

            self.spinner.start()

            # Concatenate the files
            sourcePathList = [os.path.join(route, bn) for bn in sourceList]
            #print("srcs: "+  ' '.join(sourcePathList))
            success = False
            try:
                with open(TMP_PATH, "w") as outfile:
                    for src in sourcePathList:
                        shutil.copyfileobj(open(src), outfile)
                success = True
            except IOError as e:
                self.message("Unable to concatenate source files?", e)

            if (not success):
                self.spinner.stop()
                return False
            else:
            
                ##java -jar yuicompressor-2.4.8.jar -o "./site-min.css" "/site.css"
                ##java -jar /home/rob/Deployed/yuicompressor-2.4.8.jar -o /home/rob/websites/archaic_groves/resources/css/site-min.css /home/rob/Desktop/site.css
                ## todo: os.path
                tpe = "css" if (self.isCSSPopulated) else "js"
                cmd = ['java', '-jar', YUI_PATH, "--type", tpe, "-o", os.path.join(route, dstBaseName), TMP_PATH]
                #print(cmd)
                try:
                    subprocess.call(cmd)
                except:
                    self.message("Unable to minify concatenated file?")
                
                #_cleanTmp
                os.remove(TMP_PATH) 
                self.spinner.stop()
            
                #return False if (ret != 0) else True
                self.saveSettings(sourceList)
                self.message("minified to {0}".format(dstBaseName))

    
    def getSelected(self):
        return [row[1] for row in self.store if (row[0])]


               
    def _onclick_cssjs(self, widget):
        self.clearStatus()
        self.jsPopulate() if (self.isCSSPopulated) else self.cssPopulate()
             




        
# settings for last used files
gsettings = Gio.Settings.new(GSCHEMA)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
