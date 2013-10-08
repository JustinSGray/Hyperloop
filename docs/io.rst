============================
Model Inputs and Outputs
============================

.. note:: 
    Before describing the I/O of the model, note that this list represents the current state 
    of the model. In its current form, this model is not complete and as new analyses are added
    additional design variables and couplings will need to be added to this list. 

Design Variables
====================

The model has the following design variables: 

========================  ====================================================  ========  ===============  ===============  ===============
Variable                  Description                                           Units     Baseline Value        Min.             Max.
========================  ====================================================  ========  ===============  ===============  ===============
Mach_bypass               Mach number of the air traveling around the pod                   .95              .5              .98
------------------------  ----------------------------------------------------  --------  ---------------  ---------------  ---------------  
Mach_pod_max              Maximum travel Mach number of the pod                             .9               .5              .98              
------------------------  ----------------------------------------------------  --------  ---------------  ---------------  ---------------  
Mach_c1_in                Mach number of the air at the back of the inlet                   .6               .5              .8
------------------------  ----------------------------------------------------  --------  ---------------  ---------------  ---------------  
Ps_tube                   Static pressure of the air in the tube                  Pa         99                99              500
========================  ====================================================  ========  ===============  ===============  ===============


Constraints and State Variables
=================================

The hyperloop system presents a multidisciplinary design problem. The cyclic connections in
the above figure represent the coupling relationships between the different sub-systems. These 
couplings enforce a set of equality constraints that must be satisfied for any valid hyperloop 
design. For constraints 1 and 3, a multiplier has been applied to the constraint to scale it for 
improved numerical convergence. 
     
    #. 10*(compress.W\_in - flow\_limit.W_excess) = 0
    #. tube\_wall\_temp.ss\_temp\_residual = 0  
    #. 0.01*(pod.area\_compressor\_bypass - compress.area\_c1\_out) = 0

The model has a set of state variables that are varied to satisfy the constraints. State variables 
2 and 3 are given as a list of variables. These are lists represent linked variables. They are treated 
as a single variable for the purposes of converging the model, but remain distinct variables in the model. 

    #. compress.W\_in
    #. (compress.Ts_tube,flow_limit.Ts_tube,tube_wall_temp.temp_tube_wall)
    #. (compress.radius_tube, flow_limit.radius_tube, pod.radius_tube_inner)

Outputs
====================

There are a number of key output values that are of interest for any design. 

    #. Overall pod radius: pod.radius_inlet_outer
    #. Total mass flow through the compression system: compress.W_in
    #. Total power required to drive the compression system: compress.pwr_req
    #. Total energy needed to power the compression system for one trip: mission.energy
    #. Travel time for one trip: mission.time
    #. Maximum speed: compress.speed_max
    #. Equilibrium tube temperature: tube_wall_temp.temp

