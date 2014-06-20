#
# =============================================================================
#  PYTHON SCRIPT FOR PLOTTING SMITH CHART
# =============================================================================

import pylab
import numpy
import scipy

# valid color names
# http://w3schools.com/html/html_colornames.asp


execfile( 'size_plot.dat' )

MN  = [ 0.1001, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.8999 ]

pylab.figure( figsize=(12,12), facecolor='lightgrey' )
axes = [ 0.00, 1.2001, 0.0, 1.0 ]

pylab.axis( axes )
pylab.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
pylab.tick_params(axis='both', which='major', labelsize=16)

pylab.ylabel('Area Ratio (Bypass/Tube)', fontsize=18)
pylab.xlabel('Bypass Mach Number', fontsize=18)
pylab.grid(b=True, which='major', color='grey', linestyle='--')
#pylab.title( 'hyperloop' )
pylab.legend(loc="best")

CS = pylab.tricontour( MNbyp, AR, MNpod, MN, colors = ['darkblue','red','darkgreen','purple', 'grey','darkorange',  'black', 'lightblue'] )

fmt = {} #tricontour labels
strs = [ 'Pod MN=0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9' ]
for l,s in zip( CS.levels, strs ):
    fmt[l] = s
pylab.clabel( CS, inline=1,fontsize=14, fmt = fmt )

pylab.annotate("     Available pod area \ndecreasing relative to tube", fontsize=16, xy=(1.09, 0.486), xycoords='data', xytext=(0., 0),
        rotation=90, textcoords='offset points', bbox=dict(boxstyle="square", edgecolor='lightgrey',facecolor='lightgrey') )
 
#              x,    y,   dx,   dy,
pylab.arrow( 1.121, 0.458, 0.0, 0.10, fc='lightgrey', ec='lightgrey', head_width=0.16, head_length=0.070 )

pylab.vlines(1.0, 0, 1.0, colors='darkgrey', linestyles='dashed',lw= 3)#, label="limit")

pylab.gcf().set_size_inches(11,8)

pylab.show()


