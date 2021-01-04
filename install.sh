#!/bin/bash
mkdir -p ~/.local/share/nautilus/scripts
FILE=./IconChooser.py
if ! [ -f "$FILE" ]; then
	wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/IconChooser.py -P ~/.local/share/nautilus/scripts
else
	mv IconChooser.py ~/.local/share/nautilus/scripts
fi

