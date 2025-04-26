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

current_icon_theme = subprocess.getoutput('gsettings get org.gnome.desktop.interface icon-theme')
current_icon_theme = current_icon_theme.replace('\'', '')

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Icon Chooser")
        self.set_default_size(835, 400)

        self.last_search_time = 0
        self.search_timeout_id = None
        self.selected_theme = current_icon_theme

        self.grid = Gtk.Grid(column_homogeneous=True)
        self.add(self.grid)

        self.scrolledwindow = Gtk.ScrolledWindow()

        # Search Entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text('Search icon')
        self.entry.set_text("")
        self.entry.connect("changed", self.on_search_text_changed)

        # Theme Selector ComboBox
        self.theme_store = Gtk.ListStore(str)
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.set_entry_text_column(0)
        self.populate_theme_combo()
        self.theme_combo.connect("changed", self.on_theme_changed)

        self.liststore = Gtk.ListStore(Pixbuf, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.connect("activate-cursor-item", self.apply, None)
        self.iconview.connect("item-activated", self.apply)

        self.filteredIcons = []
        self.icons = self.getAppIcons(self.selected_theme)

        self.getIcons(self.icons)

        self.revertButton = Gtk.Button.new_with_label("Revert")
        self.revertButton.connect("clicked", self.revert)

        self.applyButton = Gtk.Button.new_with_label("Apply")
        self.applyButton.connect("clicked", self.apply, None)

        self.scrolledwindow.add(self.iconview)
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)

        # Add search entry to grid
        self.grid.attach(self.entry, 0, 0, 1, 1)

        # Add theme selector below search input
        self.grid.attach(self.theme_combo, 0, 1, 1, 1)

        # Adjust positions of other elements
        self.grid.attach(self.scrolledwindow, 0, 2, 1, 1)
        self.grid.attach(self.applyButton, 0, 3, 1, 1)

    def populate_theme_combo(self):
        """Populate the theme combo box with available icon themes"""
        system_themes = self.get_available_themes('/usr/share/icons/')
        user_themes = self.get_available_themes(os.path.expanduser('~/.local/share/icons/'))

        # Combine and sort themes
        all_themes = sorted(list(set(system_themes + user_themes)))

        # Add themes to combo box
        for theme in all_themes:
            self.theme_combo.append_text(theme)

        # Set active theme to current system theme
        if current_icon_theme in all_themes:
            self.theme_combo.set_active(all_themes.index(current_icon_theme))

    def get_available_themes(self, directory_path):
        """Get list of available icon themes from a directory"""
        themes = []
        try:
            for item in os.listdir(directory_path):
                theme_dir = os.path.join(directory_path, item)
                if os.path.isdir(theme_dir):
                    # Check if it's actually an icon theme (has index.theme file or apps folder)
                    if (os.path.isfile(os.path.join(theme_dir, 'index.theme')) or
                        os.path.isdir(os.path.join(theme_dir, 'apps'))):
                        themes.append(item)
        except FileNotFoundError:
            pass
        return themes

    def on_theme_changed(self, combo):
        """Handler for theme change event"""
        self.selected_theme = combo.get_active_text()
        if self.selected_theme:
            # Refresh icons with the new theme
            self.liststore.clear()
            self.icons = self.getAppIcons(self.selected_theme)
            self.getIcons(self.icons)
            # Reapply search filter if there's text in the search box
            if self.entry.get_text():
                self.search(None)

    def on_search_text_changed(self, entry):
        # Cancel previous timeout if it exists
        if self.search_timeout_id:
            GLib.source_remove(self.search_timeout_id)

        # Add debounce to prevent searching on every keystroke
        self.search_timeout_id = GLib.timeout_add(300, self.search, None)

    def search(self, button):
        value = self.entry.get_text()

        # Clear timeout ID since we're executing the search now
        self.search_timeout_id = None

        def filterIcons(icons):
            if value.lower() in icons["name"].lower():
                return True
            else:
                return False

        filteredIcons = list(filter(filterIcons, self.icons))

        self.liststore.clear()
        self.getIcons(filteredIcons)

        # Return False to prevent the timeout from recurring
        return False

    def revert(self, button):
        current = os.getenv("NAUTILUS_SCRIPT_CURRENT_URI", '').replace("file://", "").replace("%20", " ")
        root = os.path.realpath(current)
        click = os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','')
        folder = os.path.join(click)

        for path in os.getenv('NAUTILUS_SCRIPT_SELECTED_FILE_PATHS','').splitlines():
            f = Gio.File.parse_name(os.path.abspath(path))
            f.set_attribute_string("metadata::custom-icon", '', Gio.FileQueryInfoFlags.NONE, None)

        self.destroy()

    def apply(self, button, param):
        if not self.iconview.get_selected_items():
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                message_format="Please select an icon first"
            )
            dialog.run()
            dialog.destroy()
            return

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
                # Try to load directly from file path if theme loading fails
                try:
                    pixbuf = Pixbuf.new_from_file_at_size(icon["path"], 64, 64)
                    self.liststore.append([pixbuf, icon["name"]])
                except Exception as e:
                    print(f"Failed to load icon {icon['name']}: {e}")

    def getAppIcons(self, theme_name):
        systemPath = '/usr/share/icons/'
        userPath = os.path.expanduser('~/.local/share/icons/')
        currentPath = ''
        allFiles = []

        # Check if theme exists in system or user directories
        theme_exists_in_system = os.path.isdir(os.path.join(systemPath, theme_name))
        theme_exists_in_user = os.path.isdir(os.path.join(userPath, theme_name))

        # Determine theme path
        iconThemePath = systemPath if theme_exists_in_system else userPath

        # If theme exists in either location, proceed
        if theme_exists_in_system or theme_exists_in_user:
            currentPath = os.path.join(iconThemePath, theme_name)

            # Search for apps icons in the theme structure
            # Try different common directory structures for icon themes
            if path.exists(os.path.join(currentPath, '48')):
                currentPath = os.path.join(currentPath, '48')
            elif path.exists(os.path.join(currentPath, '48x48')):
                currentPath = os.path.join(currentPath, '48x48')
            elif path.exists(os.path.join(currentPath, 'scalable')):
                currentPath = os.path.join(currentPath, 'scalable')

                if path.exists(os.path.join(currentPath, 'apps')):
                    currentPath = os.path.join(currentPath, 'apps')

            # Check if there's a dedicated apps directory
            if path.exists(os.path.join(currentPath, 'apps')):
                currentPath = os.path.join(currentPath, 'apps')

                # Check subdirectories within apps
                if path.exists(os.path.join(currentPath, '48')):
                    currentPath = os.path.join(currentPath, '48')
                elif path.exists(os.path.join(currentPath, 'scalable')):
                    currentPath = os.path.join(currentPath, 'scalable')

            # Now find all SVG files in the final directory
            try:
                files = [f for f in listdir(currentPath) if isfile(join(currentPath, f))]

                for file in files:
                    if file.endswith('.svg'):
                        allFiles.append({
                            "name": file.replace('.svg', ''),
                            "path": os.path.join(currentPath, file)
                        })
            except (FileNotFoundError, NotADirectoryError) as e:
                print(f"Error accessing theme directory: {e}")

        # If we didn't find any icons, try the fallback Adwaita theme
        if not allFiles and theme_name != "Adwaita":
            print(f"No icons found in {theme_name}, falling back to Adwaita")
            return self.getAppIcons("Adwaita")

        return allFiles


window = MainWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
