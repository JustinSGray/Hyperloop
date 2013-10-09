======================
Baseline Design
======================

The modeling done identifies a number of high level trends and provides some concrete 
baseline numbers for the hyperloop concept. For the most part, the ideas and numbers given
in the original hyperloop proposal hold up using this analysis. However, the data shows that
there are two major changes to the design that need to be considered. 

    #. The tube will need to be significantly larger than the original proposal. In the original 
    proposal, the tube was sized with a diameter 2.23 meters. However, it appears that it will 
    need to have a diameter closer to 4 meters. 

    #. There is no need for significant, water based, air cooling system to remove excess 
    heat from the air that is added by the compression system as the pod travels through the tube. 
    Although the heat will cause the air to rise in temperature somewhat, the temperature rise is 
    very modest. In fact, solar radiation onto the surface of the tube has a much stronger affect. 

Tube Diameter
----------------------
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

.. math:: \dot{W}_{limit} = \rho_{air} A_{bypass} V_{Mach 1} 

If the required  :math:`\dot{W}_{bypass}` exceeds :math:`\dot{W}_{limit}`, then the pod will 
act like a piston in a tube and start the increase the air pressure in front 
of it and lower the pressure behind it. For the baseline hyperloop design, 
the limit speed is around 120 :math:`\frac{m}{s}`, or Mach .3, as shown in the 
figure below in the blue lines. The limit is reached when the required tube mass flow equals 
the kantrowitz limit flow. The value of this limit speed is strongly dependent on the 
ratio of the pod diameter to the tube diameter. 

.. figure:: images/tube_flow_limits.png
    :align: center
    :width: 800 px
    :alt: hyperloop tube limits

    Hyperloop speed limits as a function of tube radius

Such low speeds would not allow the hyperloop concept to significantly reduce 
travel times between Los Angeles and San Francisco. To reach higher speeds, 
a compression system is needed to help push additional air around the pod 
to enable higher travel speeds. The amount of air that the compression system needs 
to move is equal to the difference between the required tube flow (the solid lines) 
and the limit (the dashed lines). As speed increases, the flow demands on the 
compression system increase as well. 

The challenge is that when you increase the flow demands on the compression system, you 
also force the pod diameter to grow in order to handle the increased flow. So traveling 
faster means that the mass flow requirements grow, which drives the pod diameter up, which 
further increase the mass flow requirements. The only way to alleviate this cycle is to allow
the tube diameter to grow as you increase the maximum velocity. The model set up here converges 
on the necessary tube diameter, given a desired pod Mach number. 






