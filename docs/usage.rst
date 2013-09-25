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

.. math:: area_{bypass} = \pi*(r_{tube}**2-r_{pod}**2)

Based on the given tempreature and pressure of the air in the tube, 
we can find it’s density:

rho_air = xxxxx units 

The mass flow rate of the air bypassing the pod is then given by

W_bypass = rho_air*tube_area*V_pod

This mass flow rate grows linearly with the velocity of the pod. 
For any given flow there is a physical limitation to how the amount of 
flow you can pass through a given area. The maximum flow rate occurs when 
the velocity reaches Mach 1. This is kantrowitz limit. For the hyperloop 
concept, all the air must fit through the bypass_area, so the kantrowitz 
limit bounds the amount of air that can be passed around the pod. 

W_kantrowitz = rho_air*bypass_area*V_mach1 

If the required bypass_flow exceeds the kantrowitz limit, then the pod will 
act like a piston in a tube and start the increase the air pressure in front 
of it and lower the pressure behind it. For the baseline hyperloop design, 
the Kantrowitz limit speed is 120 meters/sec, or Mach .35, as shown in the 
figure below. The limit is reached when the required tube mass flow equals 
the kantrowitz limit flow. 

Such low speeds would not allow the hyperloop concept to significantly reduce 
travel times between Los Angeles and San Francisco. To reach higher speeds, 
a compression system is needed to help push additional air around the pod 
to enable higher travel speeds. 


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








