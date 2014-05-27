%
%  `NASA.cls' - a LaTeX(2e) class file used to typeset NASA
%  reports which include coverpages, titlepages, and a report
%  documentation page (rdp) as required by NASA style requirements.

% $Id: NASA.cls,v 1.47 2009/08/20 14:45:29 wawood Exp $
% AUTHORS: Bill.Wood@NASA.gov, Bil.kleb@NASA.gov

\NeedsTeXFormat{LaTeX2e}[1994/06/01]

\ProvidesClass{NASA}[2009/8/20 v1.47 NASA class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}%
                \typeout{NOTE: Passing '\CurrentOption' option on to the
                         underlying LaTeX article class}}

% option for RDP only
\newif\if@frontcovers
\@frontcoverstrue
%
\newif\if@coveronly
\@coveronlyfalse
%
\newif\if@back
\@backtrue
%
\newif\if@RDPonly
\@RDPonlyfalse
%
\DeclareOption{RDPonly}{\@RDPonlytrue\@backfalse}
\DeclareOption{coveronly}{\@coveronlytrue\@backfalse}
\DeclareOption{nocover}{\@frontcoversfalse\@backfalse}
\ProcessOptions

\setcounter{errorcontextlines}{999}% crank up debugging output

% load article class and appropriate supporting packages:
\LoadClass[twoside,11pt]{article}
\RequirePackage{graphicx}
%
%\RequirePackage{xcolor} % Uncomment to use xcolor.sty
%                                           There is a conflict with
%                                           \usepackage{xcolor} in the
%                                           body of the report.
%
\RequirePackage[paper=letterpaper, twoside, noheadfoot,%
                lmargin=0.75in, rmargin=0.75in,%
                tmargin=0.975in, bmargin=0.75in]{geometry}[1999/10/07]
\RequirePackage{ifthen} % ifthenelse
\RequirePackage{cite}% sorting, collapses multiple entries, etc.

% Redefine caption delimeters [original from article.cls]
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#1. #2}%
  \ifdim \wd\@tempboxa >\hsize
    #1. #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}

% Redefine the bibliography labels
\def\@biblabel#1{#1.}

% New appendix command
\renewcommand{\appendix}{%
 \renewcommand{\thesection}{\Alph{section}}%
 \renewcommand{\thefootnote}{\Alph{section}\arabic{footnote}}%
 \renewcommand{\thetable}{\Alph{section}\arabic{table}}%
 \renewcommand{\thefigure}{\Alph{section}\arabic{figure}}%
 \renewcommand{\theequation}{\Alph{section}\arabic{equation}}%
 \setcounter{section}{0}%
% \setcounter{secnumdepth}{1}% start ``numbering'' sections again
 \renewcommand{\section}{%
   \newpage\thispagestyle{plain}%
   \setcounter{footnote}{0}%
   \setcounter{table}{0}%
   \setcounter{figure}{0}%
   \setcounter{equation}{0}%
   \secdef\Appendix\Appendix%
 }
}

\newcommand{\Appendix}[2][?]{%
 \refstepcounter{section}%
 {\flushleft\Large\bfseries\appendixname\ \thesection\par%
  \vspace{\baselineskip}%
  #2\par%
  \vspace{\baselineskip}}%
  \addcontentsline{toc}{section}{\protect\numberline{\thesection}{#2}}%
}

% This section stolen from chngpage.sty by Peter Wilson
\begingroup
\catcode`\Q=3
\long\gdef\@ifmtarg#1{\@xifmtarg#1QQ\@secondoftwo\@firstoftwo\@nil}
\long\gdef\@xifmtarg#1#2Q#3#4#5\@nil{#4}
\endgroup
\DeclareRobustCommand{\ch@ngetext}{%
  \setlength{\@colht}{\textheight}\setlength{\@colroom}{\textheight}%
  \setlength{\vsize}{\textheight}\setlength{\columnwidth}{\textwidth}%
  \if@twocolumn%
    \advance\columnwidth-\columnsep \divide\columnwidth\tw@%
    \@firstcolumntrue%
  \fi%
  \setlength{\hsize}{\columnwidth}%
  \setlength{\linewidth}{\hsize}%
}
\DeclareRobustCommand{\changepage}[9]{%
  \@ifmtarg{#1}{}{\addtolength{\textheight}{#1}}%
  \@ifmtarg{#2}{}{\addtolength{\textwidth}{#2}}%
  \@ifmtarg{#3}{}{\addtolength{\evensidemargin}{#3}}%
  \@ifmtarg{#4}{}{\addtolength{\oddsidemargin}{#4}}%
  \@ifmtarg{#5}{}{\addtolength{\columnsep}{#5}}%
  \ch@ngetext%
  \@ifmtarg{#6}{}{\addtolength{\topmargin}{#6}}%
  \@ifmtarg{#7}{}{\addtolength{\headheight}{#7}}%
  \@ifmtarg{#8}{}{\addtolength{\headsep}{#8}}%
  \@ifmtarg{#9}{}{\addtolength{\footskip}{#9}}%
}


% Define some variables:
\newcommand{\Year}[1]{\def\NC@year{#1}}                 \Year{}

\newcommand{\Month}[1]{\def\NC@month{\ifcase #1 \relax\or
                         01\or 02\or 03\or 04\or 05\or 06\or 07\or 08\or
                         09\else #1\fi}
                       \def\NC@monthlong{\ifcase #1 \relax\or 
                         January\or February\or March\or April\or May\or
                         June\or July\or August\or September\or October\or
                         November\or December\else
                         Error: Month=01--12.\fi}}   \Month{1}

\newcommand{\Type}[1]{\def\NC@type{#1}
                       \def\NC@typelong%
 {\ifthenelse{\equal{#1}{TM}}{Technical Memorandum}
  {\ifthenelse{\equal{#1}{TP}}{Technical Publication}
   {\ifthenelse{\equal{#1}{CR}}{Contractor Report}
    {\ifthenelse{\equal{#1}{CP}}{Conference Publication}
     {\ifthenelse{\equal{#1}{SP}}{Special Publication}
      {\ifthenelse{\equal{#1}{TT}}{Technical Translation}
       {Unknown Type}}}}}}}}                             \Type{}

\newcommand{\Acknowledgment}[1]{\def\NC@acknowledgment{%
    \if #1\empty \relax \else
    \begin{center}{\twelveptlarge Acknowledgments}\end{center}
    #1\fi}}  \Acknowledgment{}

\newcommand{\DatesCovered}[1]{\def\NC@datescovered{#1}} \DatesCovered{}

\newcommand{\Number}[1]{\def\NC@number{#1}}             \Number{}
\newcommand{\LNumber}[1]{\def\NC@lnumber{#1}}           \LNumber{}

\newcommand{\ContractNumber}[1]{\def\NC@contractnumber{#1}} \ContractNumber{}
\newcommand{\GrantNumber}[1]{\def\NC@grantnumber{#1}}       \GrantNumber{}
\newcommand{\ProgramElementNumber}[1]{\def\NC@programelementnumber{#1}}
             \ProgramElementNumber{}
\newcommand{\ProjectNumber}[1]{\def\NC@projectnumber{#1}}   \ProjectNumber{}
\newcommand{\TaskNumber}[1]{\def\NC@tasknumber{#1}}         \TaskNumber{}
\newcommand{\WorkUnitNumber}[1]{\def\NC@workunitnumber{#1}} \WorkUnitNumber{}

\newcommand{\AuthorAffiliation}[1]{\def\NC@authoraffiliation{#1}} \AuthorAffiliation{}
\newcommand{\NasaCenter}[1]{\def\NC@nasacenter{#1}}     \NasaCenter{}
\newcommand{\SubjectCategory}[1]{\def\NC@category{#1}}  \SubjectCategory{}
\newcommand{\Distribution}[1]{\def\NC@distribution{#1}}  \Distribution{}
\newcommand{\SupplementaryNotes}[1]{\def\NC@supplenotes{#1}} 
             \SupplementaryNotes{}
\renewcommand{\abstract}[1]{\def\@abstract{#1}}         \abstract{}
\newcommand{\SubjectTerms}[1]{\def\NC@subjectterms{#1}} \SubjectTerms{}
\newcommand{\Pages}[1]{\def\NC@pages{#1}}               \Pages{}

\renewcommand{\maketitle}{\relax}

%  Hardwire the font sizes for the covers

\newcommand\twelveptlarge{\@setfontsize\twelveptlarge\@xivpt{18}}
\newcommand\twelveptnormalsize{\@setfontsize\twelveptnormalsize\@xiipt{14.5}}
\newcommand\twelveptsmall{\@setfontsize\twelveptsmall\@xipt{13.6}}
\newcommand\twelveptfootnotesize{\@setfontsize\twelveptfootnotesize\@xpt\@xiipt}

%       Report Documentation Page

\def\NC@rdp{%
 \renewcommand{\thanks}[1]{\relax}
 \thispagestyle{empty}
 \changepage{}{2in}{-1in}{-1in}{}{}{}{}{}
 \begin{flushleft}
  \enlargethispage{1in}
  \begin{footnotesize}
   \fontfamily{phv}%\selectfont% switch to helvetica font
   \providecommand{\almosttiny}{\@setfontsize\almosttiny\@vipt\@viipt}
   \providecommand{\almostscript}{\@setfontsize\almostscript\@viipt\@viiipt}
   \setlength{\unitlength}{1mm}%
   \begin{picture}(185,240)(-4,-251)\thicklines
%
% put a giant box around the whole thing (used for debugging)
%
%    \put(-4,-251){\dashbox(185,240){}}
%
    \put(0,-239){\framebox(182,239){}}
    \put(0,-10){\line(1,0){182}}
    \put(0,-24){\line(1,0){182}}
    \put(0,-32){\line(1,0){182}}
    \put(110,-42){\line(1,0){72}}
    \put(110,-52){\line(1,0){72}}
    \put(0,-62){\line(1,0){182}}
    \put(110,-72){\line(1,0){72}}
    \put(110,-82){\line(1,0){72}}
    \put(0,-93){\line(1,0){182}}
    \put(0,-114){\line(1,0){182}}
    \put(121,-126){\line(1,0){61}}
    \put(0,-138){\line(1,0){182}}
    \put(0,-154){\line(1,0){182}}
    \put(0,-166){\line(1,0){182}}
    \put(0,-207){\line(1,0){182}}
    \put(0,-222){\line(1,0){182}}
    \put(0,-226){\line(1,0){60}}
    \put(109,-230){\line(1,0){73}}
%
    \put(121,0){\line(0,-1){10}}
    \put(48,-24){\line(0,-1){8}}
    \put(121,-24){\line(0,-1){8}}
    \put(110,-32){\line(0,-1){61}}
    \put(121,-93){\line(0,-1){45}}
    \put(60,-222){\line(0,-1){17}}
    \put(91,-222){\line(0,-1){17}}
    \put(109,-222){\line(0,-1){17}}
    \put(20,-226){\line(0,-1){13}}
    \put(40,-226){\line(0,-1){13}}
%
    \put(0,-10){\makebox(121,10){\bfseries REPORT DOCUMENTATION PAGE}}
    \put(121,-10){\makebox(61,10){\scriptsize\slshape
     \shortstack[c]{Form Approved\\[-.5mm] OMB No. 0704--0188}}}
    \put(2,-12){\parbox[t]{6.9in}{\almosttiny
     \setlength{\baselineskip}{6pt}
     {The public reporting burden
      for this collection of information is estimated to average 1 hour
      per response, including the time for reviewing instructions,
      searching existing data sources,
\linebreak
      gathering and maintaining the data needed, and completing and
      reviewing the collection of information.
      Send comments regarding this burden estimate or any other aspect
      of this collection
\linebreak
      of information, including suggestions for reducing this
      burden, to Department of Defense, Washington Headquarters
      Services, Directorate for Information Operations and Reports
\linebreak
      (0704-0188), 1215 Jefferson Davis Highway, Suite 1204, Arlington,
      VA 22202-4302.
      Respondents should be aware that notwithstanding any other
      provision of law, no person shall be
%
      subject to any penalty for failing to comply with a collection of
      information if it does not display a currently valid OMB control
      number.\\
%
      \bfseries\almostscript
      PLEASE DO NOT RETURN YOUR FORM TO THE ABOVE ADDRESS.}}}
%
    \put(141,-240){\makebox(0,0)[tl]{ \almostscript
     \shortstack[l]{\bfseries Standard Form 298 (Rev. 8/98)\\[-.5mm]
     \almosttiny Prescribed by ANSI Std. Z39.18}}}
%
    \put(1,-32){\makebox(46,7.5)[lt]{\bfseries\almostscript 
 1. REPORT DATE \mdseries\slshape (DD-MM-YYYY)}}
    \put(2,-32){\makebox(45,4)[tl]{01-\NC@month-\NC@year}}
%
    \put(49,-32){\makebox(71,7.5)[lt]{\bfseries\almostscript 
 2. REPORT TYPE}}
    \put(50,-32){\makebox(70,4)[lt]{\NC@typelong}}
%
    \put(122,-32){\makebox(59,7.5)[lt]{\bfseries\almostscript 
 3. DATES COVERED \mdseries\slshape (From - To)}}
    \put(123,-32){\makebox(58,4)[lt]{\NC@datescovered}}
%
    \put(1,-62){\makebox(108,29.5)[tl]{\bfseries\almostscript 
 4. TITLE AND SUBTITLE}}
    \put(2,-38.5){\parbox[t]{107mm}{\raggedright \@title}}
%
    \put(111,-42){\makebox(70,9.5)[tl]{\bfseries\almostscript
 5a. CONTRACT NUMBER}}
    \put(112,-42){\makebox(69,6)[tl]{\NC@contractnumber}}
    \put(111,-52){\makebox(70,9.5)[tl]{\bfseries\almostscript
 5b. GRANT NUMBER}}
    \put(112,-52){\makebox(69,6)[tl]{\NC@grantnumber}}
    \put(111,-62){\makebox(70,9.5)[tl]{\bfseries\almostscript
 5c. PROGRAM ELEMENT NUMBER}}
    \put(112,-62){\makebox(69,6)[tl]{\NC@programelementnumber}}
    \put(111,-72){\makebox(70,9.5)[tl]{\bfseries\almostscript
 5d. PROJECT NUMBER}}
    \put(112,-72){\makebox(69,6)[tl]{\NC@projectnumber}}
    \put(111,-82){\makebox(70,9.5)[tl]{\bfseries\almostscript
 5e. TASK NUMBER}}
    \put(112,-82){\makebox(69,6)[tl]{\NC@tasknumber}}
    \put(111,-93){\makebox(70,10.5)[tl]{\bfseries\almostscript
 5f. WORK UNIT NUMBER}}
    \put(112,-93){\makebox(69,7)[tl]{\NC@workunitnumber}}
%
    \put(1,-93){\makebox(108,30.5)[lt]{\bfseries\almostscript 
 6. AUTHOR(S)}}
    \put(2,-68.5){\parbox[t]{107mm}{\raggedright \@author}}
%
    \put(1,-114){\makebox(119,20.5)[tl]{\bfseries\almostscript 
 7. PERFORMING ORGANIZATION NAME(S) AND ADDRESS(ES)}}
    \put(2,-114){\makebox(118,17)[tl]{\shortstack[l]
     {NASA \NC@nasacenter}}}
%
    \put(122,-114){\makebox(59,20.5)[tl]{\bfseries\almostscript
     \newlength{\tmpind}\settowidth{\tmpind}{8.}\shortstack[l]{
 8. PERFORMING ORGANIZATION\\ \hspace*{\tmpind} REPORT NUMBER}}}
    \put(123,-114){\makebox(58,14)[tl]{L--\NC@lnumber}}
%
    \put(1,-138){\makebox(119,23.5)[lt]{\bfseries\almostscript
 9. SPONSORING/MONITORING AGENCY NAME(S) AND ADDRESS(ES)}}
    \put(2,-138){\makebox(118,20)[tl]{\shortstack[l]{National 
     Aeronautics and Space Administration\\ Washington, DC 20546-0001}}}
%
    \put(122,-126){\makebox(59,11.5)[tl]{\bfseries\almostscript
 10. SPONSOR/MONITOR'S ACRONYM(S)}}
    \put(123,-126){\makebox(58,8)[tl]{NASA}}
%
    \put(122,-138){\makebox(59,11.5)[tl]{\bfseries\almostscript
     \settowidth{\tmpind}{11.} \shortstack[l]{
 11. SPONSOR/MONITOR'S REPORT\\ \hspace{\tmpind} NUMBER(S)}}}
    \put(123,-138){\makebox(58,5)[tl]{NASA/\NC@type --\NC@year --\NC@number}}
%
    \put(1,-154){\makebox(180,15.5)[tl]{\bfseries\almostscript
 12. DISTRIBUTION/AVAILABILITY STATEMENT}}
    \put(2,-144.5){\parbox[t]{179mm}{\raggedright
     Unclassified-Unlimited \\
     Subject Category \NC@category \\
     Availability: NASA CASI (443) 757-5802 \hspace{2cm}
%      Distribution: \NC@distribution%
}}
%
    \put(1,-166){\makebox(180,11.5)[lt]{\bfseries\almostscript
 13. SUPPLEMENTARY NOTES}}
    \put(2,-160.5){\parbox[t]{179mm}{\raggedright\scriptsize
     An electronic version can be found at 
     {http://ntrs.nasa.gov}.\\
     \NC@supplenotes}}
%
    \put(1,-207){\makebox(180,40.5)[tl]{\bfseries\almostscript 
 14. ABSTRACT}}
    \put(2,-172.5){\parbox[t]{179mm}{\raggedright \@abstract}}
%
    \put(1,-222){\makebox(180,14.5)[tl]{\bfseries\almostscript 
 15. SUBJECT TERMS}}
    \put(2,-213.5){\parbox[t]{179mm}{\raggedright \NC@subjectterms}}
%
    \put(1,-226){\makebox(58,3.5)[tl]{\bfseries\almostscript
 16. SECURITY CLASSIFICATION OF:}}
    \put(1,-239){\makebox(18,12.5)[tl]{\bfseries\almostscript a. REPORT}}
    \put(2,-239){\makebox(17,9){U}}
    \put(21,-239){\makebox(18,12.5)[tl]{\bfseries\almostscript b. ABSTRACT}}
    \put(22,-239){\makebox(17,9){U}}
    \put(41,-239){\makebox(18,12.5)[tl]{\bfseries\almostscript c. THIS PAGE}}
    \put(42,-239){\makebox(17,9){U}}
%
    \put(61,-239){\makebox(29,16.5)[tl]{\bfseries\almostscript
     \settowidth{\tmpind}{17.}\shortstack[l]{
 17. LIMITATION OF\\ \hspace{\tmpind} ABSTRACT}}}
    \put(62,-239){\makebox(28,10){UU}}
%
    \put(92,-239){\makebox(16,16.5)[tl]{\bfseries\almostscript
     \settowidth{\tmpind}{18.}\shortstack[l]{
 18. NUMBER\\ \hspace{\tmpind} OF\\ \hspace{\tmpind} PAGES}}}
    \put(93,-239){\makebox(15,7){\NC@pages}}
%
    \put(110,-230){\makebox(71,7.5)[tl]{\bfseries\almostscript
 19a. NAME OF RESPONSIBLE PERSON}}
    \put(111,-230){\makebox(70,4)[tl]{
     STI Help Desk (email: {\tt help@sti.nasa.gov})}}
%
    \put(110,-239){\makebox(71,7.5)[tl]{\bfseries\almostscript
 19b. TELEPHONE NUMBER \slshape (Include area code)}}
    \put(111,-239){\makebox(70,4)[tl]{(443) 757-5802}}
%
   \end{picture}
  \end{footnotesize}
 \end{flushleft}
}%   end of NC@rdp


\AtBeginDocument{%
 \if@RDPonly
% \changepage{textheight}{textwidth}{evensidemargin}{oddsidemargin}
%            {columnsep}{topmargin}{headheight}{headsep}{footskip}
  \changepage{-0.5in}{-1in}{.5in}{.5in}{}{}{}{}{0.5in}
  \NC@rdp
  \end{document}
%
 \else % not RDPonly
 \if@frontcovers
%
% cover page
%
 \setcounter{page}{-3}
 \pagestyle{empty}
 \renewcommand{\thanks}[1]{\\ #1}
 \begin{flushleft}
 {\twelveptlarge NASA/\NC@type --\NC@year --\NC@number \par}%
 \vskip 2em%
 \includegraphics[height=1.35in]{nasalogo}\par%
 \vskip 1em%
 {\Huge\bfseries\@title\par}%
 \vskip 3em%
 {\twelveptnormalsize\itshape\NC@authoraffiliation\par}%
 \vfill%
 \makebox[0pt][l]{\hspace{-1in}\hspace{-\oddsidemargin}%
\hspace{-\parindent}\rule{8in}{6pt}}
 \vskip 0.5em%
 {\twelveptlarge\NC@monthlong\ \NC@year}%
%
% back of cover page
%
 \newpage\raggedbottom
 \begin{twelveptsmall}
 \newlength{\originalbaselineskip}
 \setlength{\originalbaselineskip}{\baselineskip}
 \setlength{\baselineskip}{0.9\originalbaselineskip}
 \setlength{\parskip}{1em}\setlength{\columnsep}{0.5in}
 \global\let \@nodocument \relax% to circumvent \twocolumn[ activating error flag
 \twocolumn[\centering NASA STI Program \ldots\ in Profile\vskip 2em]

Since its founding, NASA has been dedicated to the advancement of
aeronautics and space science.
The NASA scientific and technical information (STI) program plays
a key part in helping NASA maintain this important role.

The NASA STI Program operates under the auspices of the Agency Chief
Information Officer.
It collects, organizes, provides for archiving, and disseminates
NASA's STI\@.
The NASA STI Program provides access to the NASA Aeronautics and Space
Database and its public interface, the NASA Technical Report Server,
thus providing one of the largest collection of aeronautical and space
science STI in the world.
Results are published in both non-NASA channels and by NASA in the
NASA STI Report Series, which includes the following report types:
\begin{list}{$\bullet$}%
 {\settowidth{\labelwidth}{$\bullet$}%
  \setlength{\labelsep}{0.5em}%
  \setlength{\leftmargin}{\labelwidth}%
  \addtolength{\leftmargin}{\labelsep}%
  \setlength{\topsep}{0pt}}
\item TECHNICAL PUBLICATION.
  Reports of completed research or a major significant phase of research
  that present the results of NASA programs and include extensive data
  or theoretical analysis.
  Includes compilations of significant scientific and technical data and
  information deemed to be of continuing reference value.
  NASA counterpart of peer-reviewed formal professional papers, but
  having less stringent limitations on manuscript length and extent of
  graphic presentations.
\item TECHNICAL MEMORANDUM.\\
  Scientific and technical findings that are preliminary or of
  specialized interest, e.g., quick release reports, working papers, and
  bibliographies that contain minimal annotation.
  Does not contain extensive analysis.
\item CONTRACTOR REPORT.
  Scientific and technical findings by NASA-sponsored contractors and
  grantees.
\newpage
\item CONFERENCE PUBLICATION.\\
  Collected papers from scientific and technical conferences, symposia,
  seminars, or other meetings sponsored or co-sponsored by NASA\@.
\item SPECIAL PUBLICATION.
  Scientific, technical, or historical information from NASA programs,
  projects, and missions, often concerned with subjects having
  substantial public interest.
\item TECHNICAL TRANSLATION.
  English- language translations of foreign scientific and technical
  material pertinent to NASA's mission.
\end{list}

 Specialized services also include creating custom thesauri, building customized
 databases, and organizing and publishing research results.

 For more information about the NASA STI Program, see the following:
 \begin{list}{$\bullet$}%
  {\settowidth{\labelwidth}{$\bullet$}%
   \setlength{\labelsep}{0.5em}%
   \setlength{\leftmargin}{\labelwidth}%
   \addtolength{\leftmargin}{\labelsep}%
   \setlength{\topsep}{0pt}}
 \item Access the NASA STI program home page at
  \bfseries \itshape http://www.sti.nasa.gov
  \normalsize\normalfont
 \item E-mail your question via the Internet to help@sti.nasa.gov
 \item Fax your question to the NASA STI Help Desk at 443-757-5803
 \item Phone the NASA STI Help Desk at 443-757-5802
 \item Write to:\\
  NASA STI Help Desk\\
  NASA Center for AeroSpace Information\\
  7115 Standard Drive\\
  Hanover, MD 21076--1320
 \end{list}
 \renewcommand{\baselineskip}{\originalbaselineskip}
 \end{twelveptsmall}
 \vfill
%
% title page
%
 \onecolumn
  \setlength{\parskip}{0pt}%
 {\twelveptlarge NASA/\NC@type --\NC@year --\NC@number \par}%
 \vskip 2em%
 \includegraphics[height=1.35in]{nasalogo}\par%
 \vskip 1em%
 {\Huge\bfseries\@title\par}%
 \vskip 3em%
 {\twelveptnormalsize\itshape\NC@authoraffiliation\par}%
 \vfill%
 {\twelveptfootnotesize National Aeronautics and\\
 Space Administration\par}
 \vskip 0.7em%
 {\twelveptfootnotesize \NC@nasacenter\par}%
 \vskip 0.7em%
 \makebox[0pt][l]{\hspace{-1in}\hspace{-\oddsidemargin}%
\hspace{-\parindent}\rule{8in}{6pt}}
 \vskip 0.5em%
 {\twelveptlarge\NC@monthlong\ \NC@year}%
%
% back of title page
%
\newpage\raggedright\raggedbottom%
%
\vspace*{\fill}
\NC@acknowledgment
\vfill
\newlength{\noticeboxwidth}
\setlength{\noticeboxwidth}{\linewidth}
\addtolength{\noticeboxwidth}{-2\fboxrule}
\addtolength{\noticeboxwidth}{-2\fboxsep}
\begin{twelveptfootnotesize}
 \framebox{\parbox{\noticeboxwidth}{The use of trademarks or names of
   manufacturers in this report is for accurate reporting and does not
   constitute an offical endorsement, either expressed or implied, of
   such products or manufacturers by the National Aeronautics and Space
   Administration.}}
\end{twelveptfootnotesize}
\par\vspace{1in}
\vskip 0.5em
\begin{twelveptfootnotesize}
  \begin{center}
    Available from:\par
    \vskip 1em
    NASA Center for AeroSpace Information\\
    7115 Standard Drive\\
    Hanover, MD 21076-1320\\
    443-757-5802
  \end{center}
\end{twelveptfootnotesize}
\end{flushleft}
%
 \if@coveronly
  \end{document}
 \fi
%
 \newpage
%
 \fi % frontcovers
%
 \changepage{-0.5in}{-1in}{.5in}{.5in}{}{}{}{}{0.5in}
 \pagestyle{plain}
 \section*{Abstract}
 \@abstract\par
%
 \fi % RDPonly
}% AtBeginDocument


\AtEndDocument{% RDP and back cover
 \if@back
%
% Report Documentation Page
%
  \clearpage
  \ifodd\thepage\thispagestyle{empty}\null\newpage\fi% skip to even page
  \NC@rdp
%
% Back Cover (blank page and then a page with a rule at the bottom)
%
  \cleardoublepage
  \null\thispagestyle{empty}
  \newpage
  \enlargethispage{0.25in}
  \thispagestyle{empty}%
  \vspace*{\fill}%
  \makebox[0pt][l]{\hspace{-\parindent}\rule{8in}{6pt}}%
 \fi % back
}% AtEndDocument
%
% end of NASA.cls
