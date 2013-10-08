===============
Introduction
===============

The hyperloop concept is a proposed transportation system that could offer lower costs and 
travel times than high speed rail system. The hyperloop consists consists of a passenger 
pod traveling in a tube under light vacuum with a compression system to help move some 
of the air around the pod. The compression system is powered by electric motors and 
on board batteries. Propulsion is provided via linear accelerators mounted on the 
tube itself. The pod rides on a set of air bearings, with pressurized air also being 
provided by the compressions system. All of these different sub-systems interact with 
each other and an effective hyperloop system will need to balance the needs of all of them. 

We propose the the design of the hyperloop should be taken from a systems perspective with 
the dual objectives of minimizing ticket cost and minimizing travel time. In order to achieve 
this goal we propose a top down design approach where the designs of all components
are optimized simultaneously with respect to the overall system goals.

An overarching framework is needed to orchestrate the interaction between models of  
various subsystems and perform the necessary optimization. This code base contains a hyperloop 
system model built by a handful of engineers and computer scientists as an `OpenMDAO.`__
plugin. The intention is to provide this code as a baseline for further public 
contribution to support an open source hyperloop design. Interested parties should feel 
to modify the code as they see fit and improve the models in areas where they have expertise. 

.. __: http://openmdao.org/

The model is broken down into 5 major sub-systems: 

    #. **Compression System (compress)**: Performance and power consumption of the compressors
    #. **Mission Analysis (mission)**: Estimate of travel time 
    #. **Pod Geometry (pod)**: Physical Dimensions and calculations that depend on them
    #. **Tube Flow Limitations (flow_limit)**: Tube flow limitations based on choked flow restrictions
    #. **Tube Wall Temperature (tube_wall_temp)**: Equilibrium temperature of the tube wall

.. figure:: images/hyperloop_assembly_xdsm.png
   :align: center
   :alt: Hyperloop assembly connections

   The overall layout of the hyperloop assembly and the connections between the components. 