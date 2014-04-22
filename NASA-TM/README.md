Directory

	(main files)
	heading.tex- NASA header/footer, imports packages and subfiles
	hyperloop.tex- Main Paper Body
	appendix.tex- Appendix
	bibliography.bib- References
	build.sh - build script

	/images
		-contains all graphics
	/code
		-contains all code snippets

	(other files)
	nasalogo.pdf- NASA meatball
	NASA.cls- NASA LaTeX style sheet
	clean.sh- shell script to delete unnecessary files

Build to PDF using this command:

. build.sh


-------------------------------------------
*** Packages ***
-------------------------------------------
BibTex for references (see build script)

\cite{Cengal} to cite a source

http://en.wikipedia.org/wiki/BibTeX#Entry_types
for more info
-------------------------------------------
nomencl for nomenclature (see build script)

\nomenclature{MDAO}{Multi-disciplinary}
\nomenclature{\rho}{Density}

Build with build.sh
Edit .nls to add $$ to math equation nomenclature manually so TexMaker doesn't bark
otherwise can't interperate \dot{W}

http://en.wikibooks.org/wiki/LaTeX/Indexing
for more info
-------------------------------------------
Cleveref for section linking

\cref{app:2} to link to the following appendix section


	\crefalias{section}{appsec}
	\Appendix{Sample Source Code} \label{app:2} 


*Tip*
Label must come after caption for proper figure referencing. 

-------------------------------------------
"mathtools" -for equation 

	\begin{equation*}
	T_{t} = T_{s} * [1 + \frac{\gamma -1}{2} MN^2]
	\end{equation*}

or inline: $<equation>$

-------------------------------------------
"minted" -for code syntax highlighting (see build script)

	\begin{adjustwidth}{-3cm}{-3cm}
	\inputminted[]{python}{code/example1.py}
	\end{adjustwidth} 

Minted Help
http://www.ctan.org/tex-archive/macros/latex/contrib/minted
Read the docs to install:
http://mirrors.ibiblio.org/CTAN/macros/latex/contrib/minted/minted.pdf

if it's still not working check this:
http://tex.stackexchange.com/questions/48018/minted-not-working-on-mac