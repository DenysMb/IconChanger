#!/usr/bin/env python3
"""
Author: Denys Madureira
Change icon of selected folder
DateTimeOriginal tag
"""

from os import listdir, path
from os.path import isfile, join
import gi
import glob
import sys
import subprocess
import os
import pathlib
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
from gi.repository.GdkPixbuf import Pixbuf

iconTheme = subprocess.getoutput('gsettings get org.gnome.desktop.interface icon-theme')
iconTheme = iconTheme.replace('\'', '')

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Icon Chooser")
        self.set_default_size(835, 400)

        self.last_search_time = 0
        self.search_timeout_id = None

        self.grid = Gtk.Grid(column_homogeneous=True)
        self.add(self.grid)

        self.scrolledwindow = Gtk.ScrolledWindow()

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('Search icon')
        self.entry.set_text("")
        self.entry.connect("changed", self.on_search_text_changed)

        self.liststore = Gtk.ListStore(Pixbuf, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.connect("activate-cursor-item", self.apply, None)
        self.iconview.connect("item-activated", self.apply)

        self.filteredIcons = []
        self.icons = self.getPlaceIcons()

        self.getIcons(self.icons)

        self.revertButton = Gtk.Button.new_with_label("Revert")
        self.revertButton.connect("clicked", self.revert)

        self.applyButton = Gtk.Button.new_with_label("Apply")
        self.applyButton.connect("clicked", self.apply, None)

        self.scrolledwindow.add(self.iconview)
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)

        self.grid.add(self.entry)
        self.grid.attach(self.scrolledwindow, 0, 1, 1, 1)
        self.grid.attach(self.applyButton, 0, 3, 1, 1)

    def on_search_text_changed(self, entry):
        if self.search_timeout_id:
            GLib.source_remove(self.search_timeout_id)

        self.search_timeout_id = GLib.timeout_add(300, self.search, None)

    def search(self, button):
        value = self.entry.get_text()

        self.search_timeout_id = None

        def filterIcons(icons):
            if value.lower() in icons["name"].lower():
                return True
            else:
                return False

        filteredIcons = list(filter(filterIcons, self.icons))

        self.liststore.clear()
        self.getIcons(filteredIcons)

        return False

    def revert(self, button):
        current = os.getenv("NAUTILUS_SCRIPT_CURRENT_URI", '').replace("file://", "").replace("%20", " ")
        root = os.path.realpath(current)
        click = os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','')
        folder = os.path.join(click)

        for path in os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','').splitlines():
            f = Gio.File.parse_name(os.path.abspath(path))
            f.set_attribute_string("metadata::custom-icon", '', Gio.FileQueryInfoFlags.NONE, None)
            # subprocess.Popen(['gvfs-set-attribute', folder, '-t', 'unset', 'metadata::custom-icon'])
            # os.system('gvfs-set-attribute ' + folder + ' -t unset metadata::custom-icon')

        self.destroy()

    def apply(self, button, param):
        current = os.getenv("NAUTILUS_SCRIPT_CURRENT_URI", '').replace("file://", "").replace("%20", " ")
        root = os.path.realpath(current)
        click = os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','')
        index = int(str(self.iconview.get_selected_items()[0]))
        icon = self.filteredIcons[index]
        folder = os.path.join(click)
        newList = [column for column in [row for row in self.liststore]]

        for path in os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','').splitlines():
            f = Gio.File.parse_name(os.path.abspath(path))
            f.set_attribute_string("metadata::custom-icon", "file://" + icon["path"], Gio.FileQueryInfoFlags.NONE, None)
            subprocess.Popen(['nautilus', root])

        self.destroy()

    def getIcons(self, icons):
        self.filteredIcons = []

        for icon in icons:
            self.filteredIcons.append(icon)
            try:
                pixbuf = Gtk.IconTheme.get_default().load_icon(icon["name"], 64, 0)
                self.liststore.append([pixbuf, icon["name"]])
            except Exception as inst:
                print(inst)

    def getPlaceIcons(self):
        systemPath = '/usr/share/icons/'
        userPath = os.path.expanduser('~/.local/share/icons/')
        currentPath = ''
        allFiles = []

        systemDirectories = [f for f in listdir(systemPath)]

        userDirectories = [f for f in listdir(userPath)]

        directories = systemDirectories + userDirectories

        iconThemePath = systemPath if iconTheme in systemDirectories else userPath

        for directory in directories:
            if directory == iconTheme:
                currentPath = iconThemePath + directory

                if path.exists(currentPath + '/48'):
                    currentPath = currentPath + '/48'

                elif path.exists(currentPath + '/48x48'):
                    currentPath = currentPath + '/48x48'

                elif path.exists(currentPath + '/scalable'):
                        currentPath = currentPath + '/scalable'

                        if path.exists(currentPath + '/places'):
                            currentPath = currentPath + '/places'

                        else:
                            pass

                if path.exists(currentPath + '/places'):
                    currentPath = currentPath + '/places'

                    if path.exists(currentPath + '/48'):
                        currentPath = currentPath + '/48'

                    elif path.exists(currentPath + '/scalable'):
                        currentPath = currentPath + '/scalable'

                    else:
                        pass

                else:
                    pass

                files = [f for f in listdir(currentPath) if isfile(join(currentPath, f))]

                for file in files:
                    if ".svg" in file:
                        allFiles.append({
                            "name": file.replace('.svg', ''),
                            "path": currentPath + '/' + file
                        })
                        # allFiles.append(file)
                    else:
                        continue

        return allFiles


window = MainWindow()
# window.set_resizable(False)
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
