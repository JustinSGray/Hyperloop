#!/bin/bash
#build pdf (with bibtex), by defualt do a quick build
"/usr/texbin/pdflatex" -synctex=1 -shell-escape -interaction=nonstopmode heading.tex
if [ "$1" == "-f" ]; then #add -f flag to do full build
	bibtex heading.aux
	makeindex heading.nlo  -s nomencl.ist -o heading.nls
	"/usr/texbin/pdflatex" -synctex=1 -shell-escape -interaction=nonstopmode heading.tex
	"/usr/texbin/pdflatex" -synctex=1 -shell-escape -interaction=nonstopmode heading.tex

	mv heading.pdf hyperloop.pdf
fi
#. clean.sh
