=================================
Code Contribution
=================================

This plugin is designed to be a jumping off point for community contributions to help crowd 
source the development of the hyperloop concept. The `readme`__ on the github repository 
walks through basic installation steps, further support can be found through the main `OpenMDAO docs`__.
And the basic structure of an assembly is explained in the :ref:`usage section <Usage>`  of these docs.


.. __: https://github.com/OpenMDAO-Plugins/Hyperloop

.. __: http://openmdao.org/docs/

Coding Conventions
-----------------------

We've tried our best to follow a small set of
conventions that help keep the code neat and fairly organized. 

Variables should be lower case and connected with underscores. 

    like_this

Inputs should have default values and both inputs and outputs should be given descriptions, units, and iotypes whenever possible.

Classes capatilize the first letter of each word with no spaces.

    LikeThis

Assemblies should make explicit connections, first connecting boundary inputs, followed by inter-component connections, then boundary outputs.