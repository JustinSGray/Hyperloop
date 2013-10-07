"""
XDSM tex source writer utility. Three methods:
1. addComp(name, style, string, stack=False)
      name: [string] label of the component
      style: [string] Tikz block style, defined in diagram_styles.tex
      string: [string] name of the component that appears in the pdf
      stack: [boolean] adds the stack option
2. addDep(out, inp, style, string, stack=False)
      out: [string] label of the component that depends on the variable
      inp: [string] label of the component that computes the variable
      style: [string] Tikz block style, defined in diagram_styles.tex
      string: [string] name of the variable that appears in the pdf
      stack: [boolean] adds the stack option
3. write(filename, compilepdf=False)
      filename: [string] write to filename+'.pdf'
      compilepdf: [string] whether to run pdflatex on the tex file
"""

class XDSM(object):

    def __init__(self):
        self.inds = {}
        self.comps = []
        self.deps = []

    def addComp(self, name, style, string, stack=False):
        self.inds[name] = len(self.comps)
        self.comps.append([name, style, string, stack])

    def addDep(self, out, inp, style, string, stack=False):
        self.deps.append([out, inp, style, string, stack])

    def getCmds(self):
        def write(i, j, name, style, string, stack):
            M[i][j] = '    \\node' 
            M[i][j] += ' [' + style + (',stack]' if stack else ']')
            M[i][j] += ' (' + name + ')'
            M[i][j] += ' {' + string + '};'
            M[i][j] += ' &\n' if j < n-1 else (' \\\\\n    %Row ' + str(i+2) + '\n')

        n = len(self.comps)
        inds = self.inds

        names = [ [ None  for j in range(n) ] for i in range(n) ]      
        for name, style, string, stack in self.comps:
            names[inds[name]][inds[name]] = name
        for out, inp, style, string, stack in self.deps:
            names[inds[inp]][inds[out]] = out+'-'+inp

        M = [ [ ('    &\n' if j<n-1 else '    \\\\\n')  for j in range(n) ] for i in range(n) ]        
        for name, style, string, stack in self.comps:
            write(inds[name], inds[name], name, style, string, stack)
        for out, inp, style, string, stack in self.deps:
            write(inds[inp], inds[out], out+'-'+inp, style, string, stack)

        H = [ ''  for i in range(n) ]
        for i in range(n):
            minj = i
            maxj = i
            for out, inp, style, string, stack in self.deps:
                j = inds[out]
                if inds[inp] is i:
                    minj = j if j < minj else minj
                    maxj = j if j > maxj else maxj
            if minj is not maxj:
                H[i] = '   '
                H[i] += ' (' + names[i][minj] + ')'
                H[i] += ' edge [DataLine]'
                H[i] += ' (' + names[i][maxj] + ')\n'

        V = [ ''  for j in range(n) ]
        for j in range(n):
            mini = j
            maxi = j
            for out, inp, style, string, stack in self.deps:
                i = inds[inp]
                if inds[out] is j:
                    mini = i if i < mini else mini
                    maxi = i if i > maxi else maxi
            if mini is not maxi:
                V[j] = '   '
                V[j] += ' (' + names[mini][j] + ')'
                V[j] += ' edge [DataLine]'
                V[j] += ' (' + names[maxi][j] + ')\n'

        return M, H, V

    def write(self, filename, compilepdf=False):
        w = lambda s: f.write(s+'\n')

        n = len(self.comps)
        M, H, V = self.getCmds()

        f = open(filename+'.tex','w')

        w('\\documentclass{article}')
        w('\\usepackage{geometry}')
        w('\\usepackage{amsfonts}')
        w('\\usepackage{amsmath}')
        w('\\usepackage{amssymb}')
        w('\\usepackage{tikz}')
        w('')
        w('\\input{diagram_border}')
        w('')
        w('\\begin{document}')
        w('')
        w('\\input{diagram_styles}')
        w('')
        w('\\begin{tikzpicture}')
        w('')

        w('  \\matrix[MatrixSetup]')
        w('  {')
        w('    %Row 1')
        for i in range(n):
            for j in range(n):
                f.write(M[i][j])
        w('  };')
        w('')

        w('  \\begin{pgfonlayer}{data}')
        w('    \\path')
        w('    % Horizontal edges')
        for i in range(n):
            f.write(H[i])
        w('    % Vertical edges')
        for j in range(n):
            f.write(V[j])
        w('    ;')
        w('  \\end{pgfonlayer}')

        w('')
        w('\\end{tikzpicture}')
        w('')
        w('\\end{document}')

        f.close()

        if compilepdf:
            self.compilepdf(filename)

    def compilepdf(self, filename):
        import os
        os.system('pdflatex ' + filename + '.tex')
