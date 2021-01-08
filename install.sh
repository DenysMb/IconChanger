#!/bin/bash
mkdir -p ~/.local/share/nautilus/scripts

PLACES_FILE=./PlacesIconChooser.py
APPS_FILE=./AppsIconChooser.py

move () {
	echo "MOVE"
	rm ~/.local/share/nautilus/scripts/PlacesIconChooser.py
    if ! [ -f "$PLACES_FILE" ]; then
		wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/PlacesIconChooser.py -P ~/.local/share/nautilus/scripts
	else
		mv PlacesIconChooser.py ~/.local/share/nautilus/scripts
	fi
	rm ~/.local/share/nautilus/scripts/AppsIconChooser.py
	if ! [ -f "$APPS_FILE" ]; then
		wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/AppsIconChooser.py -P ~/.local/share/nautilus/scripts
	else
		mv AppsIconChooser.py ~/.local/share/nautilus/scripts
	fi
}

link () {
	echo "LINK"
    if ! [ -f "$PLACES_FILE" ]; then
		wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/PlacesIconChooser.py
	fi
	if ! [ -f "$APPS_FILE" ]; then
		wget https://raw.githubusercontent.com/DenysMb/IconChanger/master/AppsIconChooser.py
	fi
	rm ~/.local/share/nautilus/scripts/PlacesIconChooser.py
	ln ./PlacesIconChooser.py ~/.local/share/nautilus/scripts/PlacesIconChooser.py
	rm ~/.local/share/nautilus/scripts/AppsIconChooser.py
	ln ./AppsIconChooser.py ~/.local/share/nautilus/scripts/AppsIconChooser.py
}

if [ $# = 0 ]; then
	move
else
	while [[ $# -gt 0 ]]
	do
	key="$1"

	case $key in
		-l|--link)
		link
		shift
		;;
		-m|--move)
		move
		shift
		;;
		*)    # unknown option
		echo "DEFAULT"
		POSITIONAL+=("$1") # save it in an array for later
		shift
		;;
	esac
	done
	set -- "${POSITIONAL[@]}" # restore positional parameters
fi

chmod +x ~/.local/share/nautilus/scripts/PlacesIconChooser.py
chmod +x ~/.local/share/nautilus/scripts/AppsIconChooser.py
