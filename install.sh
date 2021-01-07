#!/bin/bash
mkdir -p ~/.local/share/nautilus/scripts
PLACES_FILE=./PlacesIconChooser.py
APPS_FILE=./AppsIconChooser.py
if ! [ -f "$FILE" ]; then
	wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/PlacesIconChooser.py -P ~/.local/share/nautilus/scripts
	wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/AppsIconChooser.py -P ~/.local/share/nautilus/scripts
else
	mv PlacesIconChooser.py ~/.local/share/nautilus/scripts
	mv AppsIconChooser.py ~/.local/share/nautilus/scripts
fi
chmod +x ~/.local/share/nautilus/scripts/PlacesIconChooser.py
chmod +x ~/.local/share/nautilus/scripts/AppsIconChooser.py
