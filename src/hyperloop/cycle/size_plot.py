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

pylab.ylabel('Area Ratio (Bypass/Tube)')
pylab.xlabel('Bypass Mach Number')
pylab.grid(b=True, which='major', color='grey', linestyle='--')
#pylab.title( 'hyperloop' )
pylab.legend(loc="best")

CS = pylab.tricontour( MNbyp, AR, MNpod, MN, colors = ['darkblue','red','darkgreen','purple', 'grey','darkorange',  'black', 'lightblue'] )
pylab.clabel( CS, inline=1, fontsize=10 )


pylab.show()


