===============
Introduction
===============

This plugin provides contains the Hyperloop model built using OpenMDAO. 


===================
Modeling Summary
===================

The following sections outline the preliminary modeling work conducted by 
our team. Our main focus was to produce a model that predicts the instantaneous 
power required to run a transport capsule at the conditions specified in the 
original work. These power requirements are a function of the capsule air 
cycle and thermal conditions. The resultant power could then be combined 
with the estimated travel time to size the battery and coolant storage 
requirements. The following section provides a brief summary of the assumptions 
and modeling that went into each sub-system necessary to perform this analysis. 

For the sake of conciseness, each section serves as a general summary. 
The reader is recommended to refer to the actual source code and 
included documentation for full implementation details. The current 
model omits economic, structural, safety, and infrastructure considerations; 
areas that become more prominent once the core engineering concept is deemed 
sufficiently feasible. These aspects are equally important to the overall 
design and they represent the next required step in producing a viable hyperloop 
design concept. 

-----------------------------
Tube Airflow Requirements
-----------------------------

The hyperloop pod travels through a fixed diameter tube. As it travels, 
it must displace air around itself. The displaced air moves past the 
pod with a relative velocity equal to the travel speed of the pod and 
must fit into the area between the pod and the tube wall. If you assume 
a circular cross section for the pod, then the area for the air to 
travel through is given by 

.. math:: A_{bypass} = \pi(r_{tube}^2-r_{pod}^2)

Given the conditions in the tube, we know the density of air to be 
0.00118 :math:`\frac{kg}{m^3}`. The mass flow rate of the air 
bypassing the pod is then given by

.. math:: \dot{W}_{bypass} = \rho_{air} A_{tube} V_{pod}

Since :math:`\rho_{air}` and :math:`A_{tube}` are both constant for given tube size 
and pressure, mass flow rate grows linearly with the velocity of the pod. 

For any given flow there is a physical limitation to how the amount of 
flow you can pass through a given area. The maximum flow rate occurs when 
the velocity reaches Mach 1. For the hyperloop concept, all the air must fit 
through the area between the pod and the tube, called :math:`A_{bypass}`. When 
the air going through :math:`A_{bypass}` reaches Mach 1, no additional flow can pass through. 
This is called the Kantrowitz limit. 

.. math:: \dot{W}_{kantrowitz} = \rho_{air} A_{bypass} V_{Mach 1} 

If the required  :math:`\dot{W}_{kantrowitz}` exceeds the kantrowitz limit, then the pod will 
act like a piston in a tube and start the increase the air pressure in front 
of it and lower the pressure behind it. For the baseline hyperloop design, 
the Kantrowitz limit speed is 120 meters/sec, or Mach .35, as shown in the 
figure below. The limit is reached when the required tube mass flow equals 
the kantrowitz limit flow. 

.. figure:: images/kantrowitz_limit.png
   :align: center
   :alt: kantrowitz limit for hyperloop

   The Kantrowitz limit for the baseline hyperloop concept

Such low speeds would not allow the hyperloop concept to significantly reduce 
travel times between Los Angeles and San Francisco. To reach higher speeds, 
a compression system is needed to help push additional air around the pod 
to enable higher travel speeds. However it serves as a nice saftey margin 
that, even if the pod lost power to its compression system, the hyperloop 
could still travel at a lower speed. 


-----------------------------
Compression System
-----------------------------

-----------------------------
Battery Pack
-----------------------------

-----------------------------
Tube Temperature
-----------------------------

Water/Steam Storage Requirements 
=================================

Equilibrium Tube Temperature
=================================

-----------------------------
Geometry
-----------------------------

============================
Future Modeling RoadMap
============================

-----------------------------
System Design Optimization
-----------------------------

-----------------------------
Battery and Motors 
-----------------------------

-----------------------------
Air Bearings
-----------------------------

-----------------------------
Vacuum Pumps
-----------------------------

-----------------------------
Solar Power Generation
-----------------------------

-----------------------------
Pod Structural Design
-----------------------------

-----------------------------
Component Mass Estimation
-----------------------------

-----------------------------
Linear Accelerators
-----------------------------

-----------------------------
Route Optimization
-----------------------------








