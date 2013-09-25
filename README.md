
Hyperloop Model
=======================

This is an open-source system model of the Hyperloop transportation 
system outlined in Elon Musk’s proposal. It's primary 
purpose is to provide a completely open-source multidisciplinary model 
as a central point for continued crowd-sourced refinement of the concept. 
The current model focusses mainly on the compression system: inlet compressors, 
heat exchangers, ducting, and nozzle. The entire model is a work in progress 
and was built with the hope that external participation can help both 
refine our estimates and expand the model to include other important 
aspects of the hyperloop concept.

Due to the cross-disciplinary nature of the problem, an overarching framework is 
needed to orchestrate the interaction between models of the various subsystems. So 
the entire model is built ontop of the OpenMDAO framework. 
OpenMDAO is an open source effort, out of the NASA Glenn Research Center,  
that suits the needs of this problem well. It provides advanced modeling and optimization 
capabilities and provides a flexible structure to grow and refine the hyperloop models. 
OpenMDAO includes a plugin system, which we used to build this model. The entire thing is built 
and distributed as an OpenMDAO plugin, To further improve the ability for others to expand and improve on this work. 


Installation
====================

There are two ways to use this plugin, but both assume you have already installed OpenMDAO. 
If you need to install OpenMDAO follow the [install instructions](http://openmdao.org/docs/getting-started/index.html). 
Then, make sure you have activated your openmdao environemnt. Now follow one of the two methods below: 

Working with the source code
----------------------------
Using this method will be the best option if you want to hack on the hyperloop concept to make changes.

1. clone this repository to your local machine (or clone your own fork of this repository) 
2. navigate into the top level of the repository (you will see a setup.py file there)
3. Issue the following command
    
    python setup.py develop


Installing without source
--------------------------
This is the best option if you just want to try out the hyperloop model, as is, and 
try out performance with different inputs to the model. You'll be able to change any of the 
design variable values that we have defined. 

    plugin install --github Hyperloop



