# Dynamic Vehicle Traction in Floodwater

##### [**Undermind**](https://undermind.ai)

---

**Research Goal:** Identify published studies that model or measure the relationship between water depth, buoyancy-reduced wheel normal force, hydrodynamic resistance, and maximum available tire traction for a vehicle moving through water. Include actively driven vehicles as well as vehicles with prescribed or towed motion, provided the work quantifies wheel loads, traction, resistance, slip, or related force limits; a modeled drivetrain or engine torque curve is not required. Include paved-road flooding, stream crossings, flowing-water conditions, and off-road, agricultural, or four-wheel-drive river-fording contexts, since the transferable physics concerns buoyancy, wheel loading, hydrodynamic forces, and traction while the surface friction coefficient can be treated as a separate model parameter. Prioritize coupled fluid–vehicle simulations and experimental studies, including work using CFD, multibody or rigid-body dynamics, towing tests, scale models, or field measurements. Determine whether any study closes, or provides the components needed to close, the loop from increasing water depth and flow to reduced normal force and available tire force during motion. Exclude general flood hazard mapping and studies limited to vehicles at rest or passively displaced by flow unless they provide directly transferable force, load, or traction relationships relevant to a moving vehicle.

*Found 43 papers · July 21, 2026 · Estimated coverage of relevant papers: 98%*

## Summary of Results

The literature contains the force balance needed to relate flooding to loss of mobility—hydrostatic buoyancy reduces the tire-supported normal load, while drag/lift and rolling resistance set the opposing demand—but only a few moving-vehicle studies couple these terms dynamically; full-scale traction measurements make \[1, 10\] the strongest experimental anchor, and coupled CFD–multibody models provide the clearest computational closure \[3, 4\].

#### Two complementary regimes

- **Flood/ford stability:** available longitudinal/lateral resistance is typically represented as tire–surface friction times buoyancy-reduced normal load, compared with flow-induced drag (and, where material, lift). Full-scale tests directly measured traction under varying buoyancy and surface conditions (concrete, gravel, sand) and measured/modelled drag \[1\]; scaled moving-car experiments resolve buoyancy, drag, frictional and rolling resistance, identifying transitions to sliding or flotation \[5, 11, 12\].
- **Tire-scale flooded pavement:** hydrodynamic pressure can additionally unload or separate the tire from pavement. Experiments and FSI models quantify the effects of water depth, normal load, speed and slip on longitudinal/cornering force and hydroplaning \[14, 15, 17, 16\]. This supplies a depth- and speed-dependent tire-force law rather than a fixed friction coefficient.

#### Closure and remaining gap

- CFD–MBD/SPH frameworks resolve fluid loads, suspension/wheel contact and motion jointly \[4, 21, 3\]; \[2\] adds free-running shallow-water and flume-load validation. These are the most direct route to a closed depth/flow → wheel-load → tire-force → motion loop.
- Most flood-hazard studies instead close a quasi-static incipient-sliding/flotation balance \[Kell92, Shu11, Xia11b, Arr15\], or prescribe/limit vehicle motion. They provide transferable load and resistance components but generally do not measure transient per-wheel normal loads and slip/traction simultaneously. Off-road egress models explicitly include buoyancy, suspension, soil reaction and wheel loading \[7, 8\], making them useful for extending the loop to soft terrain.

## Paper Catalog (43 papers)

|  | Year | Cit/yr | Title | Authors | Journal |
|---:|:--:|:--:|:---|:---|:---|
| 1 | 2019 | 5.6 | Full‐scale testing of stability curves for vehicles in flood waters ([link](https://doi.org/10.1111/jfr3.12527)) | Grantley P. Smith, B. Modra, and S. Felder | Journal of Flood Risk Management |
| 2 | 2026 |  | Predicting Vehicle-Water Interaction in Shallow Water: Simulations and Experimental Validation ([link](https://doi.org/10.1115/1.4071177)) | Hao He et al. | Journal of Computational and Nonlinear Dynamics |
| 3 | 2024 | 1.7 | Modeling of Vehicle Mobility in Shallow Water with Data-Driven Hydrodynamics Model ([link](https://doi.org/10.1115/1.4064971)) | Hiroki Yamashita et al. | Journal of Computational and Nonlinear Dynamics |
| 4 | 2015 | 0.3 | Coupled Multibody Dynamics and Smoothed Particle Hydrodynamics for Modeling Vehicle Water Fording ([link](https://doi.org/10.1115/DETC2015-47142)) | T. Wasfy, Hatem M. Wasfy, and J. Peters |  |
| 5 | 2020 | 1.7 | Hydrodynamic effect on non‐stationary vehicles at varying Froude numbers under subcritical flows on flat roadways ([link](https://doi.org/10.1111/jfr3.12657)) | Syed Hamid Hussain Shah, Z. Mustaffa, Eduardo Matínez‐Gomariz, and K. Yusof | Journal of Flood Risk Management |
| 6 | 2022 | 2.7 | A numerical approach to understand the responses of passenger vehicles moving through floodwaters ([link](https://doi.org/10.1111/jfr3.12828)) | E. Al-Qadami et al. | Journal of Flood Risk Management |
| 7 | 1969 | 0.0 | STUDIES OF OFF-ROAD VEHICLES IN THE RIVERINE ENVIRONMENT. VOLUME II. ANALYTICAL METHOD FOR EGRESS EVALUATION ([link](https://doi.org/10.21236/ad0697160)) | D. Sloss, I. R. Ehrlich, and G. Worden |  |
| 8 | 1974 |  | Mathematical Model of Wheeled Vehicles Exiting from the Riverine Environment ([link](https://www.semanticscholar.org/paper/0a7854a76e0fba1dd0d030feaeffb107b98d1d18)) | M. Jurkat |  |
| 9 | 2018 | 0.1 | Development of In-Plane Truck Tire-Flooded Surface Interaction Models Using FEA-SPH Techniques ([link](https://doi.org/10.1115/DETC2018-85006)) | Zeinab El-Sayegh, M. El-Gindy, I. Johansson, and F. Öijer | Volume 3: 20th International Conference on Advanced Vehicle Technologies; 15th International Conference on Design Education |
| 10 | 2017 | 0.2 | Experimental testing of flood hazard curves for a partially submerged vehicle ([link](https://www.semanticscholar.org/paper/f9991961e7cd296cfa2597cb90d13abbc3aed3fe)) | Grantley P. Smith, B. Modra, and S. Felder |  |
| 11 | 2019 | 1.6 | Hazard risks pertaining to partially submerged non-stationary vehicle on low-lying roadways under subcritical flows ([link](https://doi.org/10.1016/j.rineng.2019.100032)) | Syed Hamid Hussain Shah, Z. Mustaffa, Eduardo Matínez‐Gomariz, K. Yusof, and E. Al-Qadami | Results in Engineering |
| 12 | 2021 | 0.5 | FROUDE NUMBER VARIANCE WITH RESPECT TO THE HYDRODYNAMIC RESPONSE OF A NON-STATIC VEHICLE AT A LOW-LYING FLOODED ROADWAY ([link](https://doi.org/10.31436/iiumej.v22i1.1502)) | Syed Hamid Hussain Shah et al. | IIUM Engineering Journal |
| 13 | 2021 | 2.6 | Full-scale experimental investigations on the response of a flooded passenger vehicle under subcritical conditions ([link](https://doi.org/10.1007/s11069-021-04949-6)) | E. Al-Qadami, Z. Mustaffa, Syed Hamid Hussain Shah, Eduardo Matínez‐Gomariz, and K. Yusof | Natural Hazards |
| 14 | 2010 | 0.2 | Effect of Water Depth and Translational Velocity on Tire Force and Moment Characteristics ([link](https://doi.org/10.4271/2010-01-0770)) | Jeffrey Dinges, D. F. Tandy, S. Hanba, and Jung Bae |  |
| 15 | 2019 | 2.1 | Longitudinal hydroplaning performance of passenger car tires ([link](https://doi.org/10.1080/00423114.2019.1693047)) | Markus Maleska, F. Petry, D. Fehr, W. Schuhmann, and M. Böhle | Vehicle System Dynamics |
| 16 | 2020 | 3.0 | Prediction of Hydroplaning Potential Using Fully Coupled Finite Element-Computational Fluid Dynamics Tire Models ([link](https://doi.org/10.1115/1.4047393)) | Ashkan Nazari et al. | Journal of Fluids Engineering |
| 17 | 2013 | 0.4 | Hydroplaning of Rolling Tires under Different Operating Conditions ([link](https://doi.org/10.1061/9780784413005.045)) | S. Srirangam, K. Anupam, A. Scarpas, and C. Kasbergen |  |
| 18 | 2026 |  | Characterization of Vehicle Tire Hydroplaning Using Numerical Simulation and Field Full-Scale Accelerated Loading Methods ([link](https://doi.org/10.3390/app16073433)) | Wentao Wang, Xiang Han, Hua Rong, Y. Miao, and Linbing Wang | Applied Sciences |
| 19 | 2023 | 0.3 | Predicting Vehicle Motion in Shallow Water with Data-Driven Hydrodynamics Model ([link](https://doi.org/10.1115/detc2023-115254)) | Hiroki Yamashita et al. | Volume 10: 19th International Conference on Multibody Systems, Nonlinear Dynamics, and Control (MSNDC) |
| 20 | 2014 |  | A comparative study of four fluid-solid coupling methods for applications in ground vehicle mobility ([link](https://www.semanticscholar.org/paper/2a3a1ddcee73fe17b8e6203c0322022c28c50616)) | A. Pazouki et al. |  |
| 21 | 2016 |  | Investigation of the Vehicle Mobility in Fording ([link](https://www.semanticscholar.org/paper/61da26b63ef7bf224b6a8cac098e077de207423d)) | A. Pazouki, P. Jayakumar, and D. Negrut |  |
| 22 | 2022 | 3.0 | Coupled multibody dynamics and computational fluid dynamics approach for amphibious vehicles in the surf zone ([link](https://doi.org/10.1016/j.oceaneng.2022.111607)) | H. Yamashita et al. | Ocean Engineering |
| 23 | 2021 | 0.4 | Amphibious Vehicle Water Egress Modeling and Simulation Using CFD and Bekker’s Methodology ([link](https://doi.org/10.4271/2021-01-0252)) | N. Tison | SAE Technical Paper Series |
| 24 | 2023 | 1.5 | Research on launching, water exiting, and river crossing of an amphibious vehicle ([link](https://doi.org/10.1063/5.0174148)) | Bolong Liu, Xiaojun Xu, and Dibo Pan | Physics of Fluids |
| 25 | 2018 | 0.6 | Instability Criteria for Vehicles in Motion Exposed to Flood Risks ([link](https://doi.org/10.1051/MATECCONF/201820307003)) | Syed Hamid Hussain Shah, Z. Mustaffa, Do Kyun Kim, and K. Yusof |  |
| 26 | 2018 | 1.3 | Influence of forces on vehicle’s instability in floodwaters ([link](https://doi.org/10.1016/J.ASEJ.2018.01.001)) | Syed Hamid Hussain Shah, Z. Mustaffa, K. Yusof, and M. Nor | Ain Shams Engineering Journal |
| 27 | 2015 | 4.4 | Drag and lift contribution to the incipient motion of partly submerged flooded vehicles ([link](https://doi.org/10.1016/J.JFLUIDSTRUCTS.2015.06.010)) | C. Arrighi, J. C. Alcérreca‐Huerta, H. Oumeraci, and F. Castelli | Journal of Fluids and Structures |
| 28 | 2012 | 4.5 | Experimental studies on the interaction between vehicles and floodplain flows ([link](https://doi.org/10.1080/15715124.2012.674040)) | F. Teo, J. Xia, R. Falconer, and B. Lin | International Journal of River Basin Management |
| 29 | 2017 | 8.8 | A new experiments-based methodology to define the stability threshold for any vehicle exposed to flooding ([link](https://doi.org/10.1080/1573062X.2017.1301501)) | E. Martínez‐Gomariz, Manuel Gómez, B. Russo, and S. Djordjević | Urban Water Journal |
| 30 | 2023 | 1.0 | Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling ([link](https://doi.org/10.3390/su151713262)) | E. Al-Qadami, M. Razi, W. S. Damanik, Z. Mustaffa, and E. Martínez‐Gomariz | Sustainability |
| 31 | 2023 | 1.1 | Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements ([link](https://doi.org/10.1111/jfr3.12885)) | Fatima Azhar, V. Pauwels, and H. Bui | Journal of Flood Risk Management |
| 32 | 2023 | 2.1 | Experimental testing to determine stability thresholds for partially submerged vehicles at different flow orientations ([link](https://doi.org/10.1016/j.jhydrol.2023.129525)) | Xiaozhe Hu, Junqi Li, Wenhai Wang, and X. Fang | Journal of Hydrology |
| 33 | 1967 | 0.6 | LOW LEVEL CAUSEWAYS ([link](https://www.semanticscholar.org/paper/598636f53664980764239c5563493dbed74956fc)) | A. Bonham and R. Hattersley |  |
| 34 | 1992 | 0.6 | Stability of Cars and Children in Flooded Streets ([link](https://www.semanticscholar.org/paper/c87e6816cba9960523f6df8f2990d9fd9626270e)) | R. Keller and B. Mitsch |  |
| 35 | 2011 | 5.5 | Incipient velocity for partially submerged vehicles in floodwaters ([link](https://doi.org/10.1080/00221686.2011.616318)) | C. Shu, J. Xia, R. Falconer, and B. Lin | Journal of Hydraulic Research |
| 36 | 2011 | 6.5 | Formula of incipient velocity for flooded vehicles ([link](https://doi.org/10.1007/S11069-010-9639-X)) | J. Xia, F. Teo, B. Lin, and R. Falconer | Natural Hazards |
| 37 | 2022 | 0.7 | Transient, 3D CFD, Moving Mesh Simulation of Vehicle Water Wading in a Water Tunnel with Inclined Entry-Exit ([link](https://doi.org/10.4271/2022-01-0768)) | M. Varshney et al. | SAE Technical Paper Series |
| 38 | 2021 | 1.7 | CFD Method Development for Simulating Water Fording for a Passenger Car ([link](https://doi.org/10.4271/2021-01-0205)) | M. Varshney et al. |  |
| 39 | 1978 |  | Study and Parametric Analysis of Trafficability, Running Gear, and Stability Considerations for Nearshore Bottom-Crawling Vehicles ([link](https://www.semanticscholar.org/paper/9201d349e29cda64218f162e0a1857a7797063da)) | G. W. Turnage and W. Seabergh |  |
| 40 | 2021 | 1.2 | Fundamental study on underwater trafficability for tracked vehicle ([link](https://doi.org/10.1016/j.jterra.2021.07.001)) | Mitsuru Yamada, Genki Yamauchi, and Takeshi Hashimoto | Journal of Terramechanics |
| 41 | 1971 | 0.1 | Trafficability of Soils: Effects of Surface Conditions on Drawbar Pull of a Wheeled Vehicle ([link](https://www.semanticscholar.org/paper/2b14783f57bf7d62ad8ed0245a1cf3a1bf82c52b)) | E. S. Rush and J. Robinson |  |
| 42 | 2026 |  | Geometry-Aware Surrogate for Real-Time Hydrodynamics Estimation of Autonomous Ground Vehicles in Amphibious Environments ([link](https://www.semanticscholar.org/paper/66a0b8a7e37fdf711ad50974911187bf5c00f294)) | Ammar Waheed, Luke Gallantree, and Zohaib Hasnain |  |
| 43 | 2014 | 1.2 | Stability and Drag Analysis of Wheeled Amphibious Vehicle Using CFD and Model Testing Techniques ([link](https://doi.org/10.4028/www.scientific.net/AMM.592-594.1210)) | R. More, P. Adhav, K. Senthilkumar, and M.W. Trikande | Applied Mechanics and Materials |

### Paper Details

1\. · 100% match · 2019 · 5.6 cit/yr\
**Full‐scale testing of stability curves for vehicles in flood waters** ([link](https://doi.org/10.1111/jfr3.12527))\
Grantley P. Smith, B. Modra, and S. Felder\
*Journal of Flood Risk Management* · Mar 5, 2019 · 41 citations

> Flood fatality data show that world‐wide, flood related deaths are increasingly associated with people perishing in vehicles that become unstable driving through floodwaters. Previous research on vehicle stability in flood flows has predominantly focussed on model scale testing. This paper presents novel testing determining stability thresholds of full‐scale, road‐going vehicles in floodwaters. Traction forces for various flow depths and buoyancy conditions were directly measured for three types of prototype vehicles. Friction coefficients for prototype vehicles were determined for different bed surface conditions including concrete, gravel, and sand highlighting that a worst‐case friction coefficient must be considered. Novel direct measurements of drag coefficients were conducted for a range of flow conditions of a model‐scale vehicle complementing the prototype tests. The combination of measured forces provided vehicle stability thresholds applicable to a range of vehicle types. While this study was the most comprehensive stability assessment to date, all tests were conducted under laboratory conditions and more conservative threshold criteria must be applied to account for violent flood waters and uneven surfaces.

------------------------------------------------------------------------

2\. · 100% match · 2026\
**Predicting Vehicle-Water Interaction in Shallow Water: Simulations and Experimental Validation** ([link](https://doi.org/10.1115/1.4071177))\
Hao He et al.\
*Journal of Computational and Nonlinear Dynamics* · Feb 19, 2026 · 0 citations

> Accurate prediction of coupled vehicle-water interaction is crucial for assessing vehicle mobility capabilities in complex water environments, including river crossings and water fording. For this purpose, various computational models have been proposed to predict vehicle-fluid interactions using coupled multibody dynamics and computational fluid dynamics (CFD) solvers, as well as emerging data-driven approaches to replace computationally intensive CFD models. Despite advances in computational approaches for modeling vehicle-fluid interactions, only limited studies have been conducted regarding the validation of the models in real physical settings. There are few or no experimental data available to characterize hydrodynamic loads for the evaluation of transient vehicle responses in shallow water. Therefore, this study presents the validation of the physics-based and data-driven coupled vehicle-water interaction models using a model-scale vehicle operated in shallow water. To this end, the transient vehicle cornering responses in shallow water, predicted by both physics-based and data-driven models, are compared with those from free-running vehicle experiments conducted in a shallow water pool. The predictive ability and computational benefits of the data-driven hydromechanics model are then examined. Furthermore, the hydrodynamic loads on the model-scale vehicle subjected to incoming water flow are measured through flume experiments and used to validate the hydrodynamic loads predicted by the simulation model. The results presented in this study provide confidence in virtual testing of vehicles in complex water environments and lay the foundation for characterizing hydrodynamic load responses on vehicles operated in shallow water environments.

------------------------------------------------------------------------

3\. · 100% match · 2024 · 1.7 cit/yr\
**Modeling of Vehicle Mobility in Shallow Water with Data-Driven Hydrodynamics Model** ([link](https://doi.org/10.1115/1.4064971))\
Hiroki Yamashita et al.\
*Journal of Computational and Nonlinear Dynamics* · Feb 29, 2024 · 4 citations

> In this study, a data-driven hydrodynamics model is proposed to enable quick prediction of vehicle mobility in shallow water, considering the effect of tire-soil interaction. To this end, a high-fidelity coupled vehicle-water interaction model using computational fluid dynamics (CFD) and multibody dynamics (MBD) solvers is developed to characterize the hydrodynamic loads exerted on a vehicle operated in shallow water, and it is used to generate training data for the data-driven hydrodynamics model. To account for the history-dependent hydrodynamic behavior, a Long Short-Term Memory (LSTM) neural network is introduced to incorporate effects of the historical variation of vehicle motion states as the input to the data-driven model, and it is used to predict hydrodynamic loads online exerted on vehicle components in the MBD mobility simulation. The impacts of hydrodynamic loads on the vehicle mobility capability in shallow water are examined for different water depths and incoming flow speeds using the high-fidelity coupled CFD-MBD model. Furthermore, it is demonstrated that the vehicle-water interaction behavior in scenarios not considered in the training data can be predicted using the proposed LSTM data-driven hydrodynamics model. However, the use of non-LSTM layers, which do not account for the sequential variation of vehicle motion states as the input, leads to an inaccurate prediction. A substantial computational speedup is achieved with the proposed LSTM-MBD vehicle-water interaction model while ensuring accuracy, compared to the computationally expensive high-fidelity coupled CFD-MBD model.

------------------------------------------------------------------------

4\. · 100% match · 2015 · 0.3 cit/yr\
**Coupled Multibody Dynamics and Smoothed Particle Hydrodynamics for Modeling Vehicle Water Fording** ([link](https://doi.org/10.1115/DETC2015-47142))\
T. Wasfy, Hatem M. Wasfy, and J. Peters\
Aug 2, 2015 · 3 citations

> Multibody dynamics and smoothed particle hydrodynamics (SPH) are integrated into one solver for predicting the water fording dynamic response of ground vehicles. Multibody dynamics models are used for the various vehicle systems including: suspension system, wheels, steering system, axles, differential, and engine. A penalty technique is used to impose joint and normal contact constraints (between the tires and ground, and between the tires/vehicle body and the fluid particles). An asperity-based friction model is used to model joint and contact friction. Water is modeled using an SPH particle-based approach along with a large eddy-viscosity turbulence model. A contact search algorithm that uses a Cartesian Eulerian grid around the water pool is used to allow fast contact detection between particles. A recursive bounding box contact search algorithm is used to allow fast contact detection between polygonal contact surfaces (representing the tires and vehicle body) and the fluid particles. The governing equations of motion for the solid bodies and the fluid particles are solved along with joint/constraint equations using a time-accurate explicit solution procedure. The integrated solver is used to predict the dynamic response of a Humvee-type vehicle moving through a shallow water pool.Copyright © 2015 by ASME

------------------------------------------------------------------------

5\. · 100% match · 2020 · 1.7 cit/yr\
**Hydrodynamic effect on non‐stationary vehicles at varying Froude numbers under subcritical flows on flat roadways** ([link](https://doi.org/10.1111/jfr3.12657))\
Syed Hamid Hussain Shah, Z. Mustaffa, Eduardo Matínez‐Gomariz, and K. Yusof\
*Journal of Flood Risk Management* · Jul 28, 2020 · 10 citations

> Water is essentially a powerful component, strong enough to even move vehicles at the lowest hydraulic parameters. The flow orientation as well as the geometric and physical characteristics of a vehicle attribute to the way floodwaters affect and control the vehicle. Herein an effort has been made to study the hydrodynamic impact on a non‐stationary vehicle partially submerged attempting to cross a flooded roadway (flat conditions). In arriving at the outcomes, extensive experimental testing was carried out on a Malaysian made city car, Perodua Viva (1:10), which was controlled to be partially submerged under the influence of subcritical flows. The experimental data was proven through theoretical equations based on the instability failure modes. The variation of the Froude number with respect to varying hydrodynamic forces has been further explored and conversed. The incipient velocity formulation proposed herein has been validated through the experimental data and the results showed good agreement between the two with a correlation coefficient of R2 = 0.85. Among the main findings, it was noticed that the buoyancy force governed vehicle weight at depths greater than and equal to 0.0457 m for the scaled model. On the other hand, below critical depth, the dominancy of the drag force over frictional resistance and driving force caused sliding instability.

------------------------------------------------------------------------

6\. · 100% match · 2022 · 2.7 cit/yr\
**A numerical approach to understand the responses of passenger vehicles moving through floodwaters** ([link](https://doi.org/10.1111/jfr3.12828))\
E. Al-Qadami et al.\
*Journal of Flood Risk Management* · Jun 14, 2022 · 11 citations

> Watercourses and roadways commonly intersect in their layout at many locations through bridges, drainages, and fords. During heavy rain events, watercourses may overflow causing serious disturbance toward traffic movement. Under such circumstances, attempting to drive through these intersections can be extremely dangerous. Therefore, understanding the responses of the vehicles moving through floodwaters is of utmost importance. Between 1967 and 2021, several studies have been published investigating the stability of static flooded vehicles. However, studies on the stability of vehicles in the movement are not sufficient at which only few experimental studies were published. Herein, for the very first time numerical simulations were conducted to investigate the hydrodynamic forces on a full‐scale medium‐size passenger vehicle moving perpendicular to the incoming floodwaters. Sliding and floating instability modes were observed by detecting the position of the vehicle centre of mass at each time step. Further, horizontal (FH) and vertical (FV) forces were measured and plotted against the governing flow parameters. Finally, it was observed that the critical flow depth was 0.38 m, while the minimum depth×velocity threshold function was 0.39 m2/s, for the tested vehicle. Later, a comparison between simulation outcomes and previously published experimental work was performed and a good agreement was observed.

------------------------------------------------------------------------

7\. · 100% match · 1969 · 0.0 cit/yr\
**STUDIES OF OFF-ROAD VEHICLES IN THE RIVERINE ENVIRONMENT. VOLUME II. ANALYTICAL METHOD FOR EGRESS EVALUATION** ([link](https://doi.org/10.21236/ad0697160))\
D. Sloss, I. R. Ehrlich, and G. Worden\
Oct 1, 1969 · 1 citations

> Abstract : A limited computer-simulation model describing the dynamics of a swimming vehicle egressing from a stream is formulated. The effects of soil reactions, hydrostatic forces, suspension and tire dynamics, and auxiliary egress assist forces are considered. Results of a parametric study are presented for a four-wheeled, box-shaped vehicle egressing onto a hard, uniformly sloped bank. Length, freeboard, center of gravity, suspension spring and damping rates, initial velocity, and bank coefficient are varied in the analysis. A correlation study, which validates the computer simulation model, is also described. Plots of normal wheel-loading versus distance up the bank, showing a comparison between the computer simulation and scale-model tests, are included. Recommendations for a comprehensive parametric study and a correlation study with full-scale vehicles are made.

------------------------------------------------------------------------

8\. · 100% match · 1974\
**Mathematical Model of Wheeled Vehicles Exiting from the Riverine Environment** ([link](https://www.semanticscholar.org/paper/0a7854a76e0fba1dd0d030feaeffb107b98d1d18))\
M. Jurkat\
Feb 1, 1974 · 0 citations

> Abstract : A two-dimensional, vertical-plane, computer simulation model describing the dynamics of a wheeled vehicle exiting from the riverine environment is presented. The model includes the effects of soft soil, suspensions, buoyancy, drive train characteristics and the inertial reactions of the unsprung masses. The body is modeled as a composite of rectangular sections; the tires are rigid. The stream bottom and bank surface can be any specified arbitrary geometry; their soil properties are specified by the land locomotion soil value system.

------------------------------------------------------------------------

9\. · 100% match · 2018 · 0.1 cit/yr\
**Development of In-Plane Truck Tire-Flooded Surface Interaction Models Using FEA-SPH Techniques** ([link](https://doi.org/10.1115/DETC2018-85006))\
Zeinab El-Sayegh, M. El-Gindy, I. Johansson, and F. Öijer\
*Volume 3: 20th International Conference on Advanced Vehicle Technologies; 15th International Conference on Design Education* · Aug 26, 2018 · 1 citations

> The performance of a vehicle highly depends on the tire-terrain interaction characteristics. The terrain on which a vehicle operates can vary dramatically. This paper focuses on the evaluation of an in-plane truck tire performance running over the flooded surface. The truck tire is modeled using Finite Element Analysis (FEA) technique and validated against measured data. The water is modeled using Smoothed Particle Hydrodynamics (SPH), which includes water material properties. The tire-terrain interaction algorithm is defined using node-symmetric node-to-segment contact with edge treatment. The performance characteristics of the interaction include the rolling resistance coefficient, vertical, longitudinal tread and longitudinal tire stiffnesses. The simulations are repeated for several operating conditions such as inflation pressure, applied vertical load, and water depth. The flooded surface results are compared with previously published data. This work will be extended to include the prediction of the full in-plane and out-of-plane rigid ring tire model parameters while the tire is operating under various conditions.

------------------------------------------------------------------------

10\. · 100% match · 2017 · 0.2 cit/yr\
**Experimental testing of flood hazard curves for a partially submerged vehicle** ([link](https://www.semanticscholar.org/paper/f9991961e7cd296cfa2597cb90d13abbc3aed3fe))\
Grantley P. Smith, B. Modra, and S. Felder\
2 citations

> Every year floods cause enormous damage and loss of life on a global scale including fatalities that occurred in vehicles becoming unstable in floodwaters. Historically, threshold conditions for vehicle instability in floodwaters have been investigated at model scale and have relied on correct scaling of the immersed vehicle weight and tyre friction, and assumptions about the buoyant behaviour of the vehicle. Instability criteria have been determined through measurement of the flow hydrodynamics, which initiated movement, of the model scale vehicle. Novel, prototype scale testing was conducted at the UNSW Water Research Laboratory measuring the threshold forces required to move a partially buoyant, full-scale vehicle. The flow hydrodynamics required to reproduce these instability threshold forces were then determined using a 18:1 scale model. Several novel results were obtained from the testing, including the measurement of the coefficient of drag of a vehicle under partially submerged conditions, and characterisation of the vehicle’s buoyant behaviour in water and subsequent traction available at the tyres. This paper provides an overview of the laboratory investigations, presents the measured data and discusses the relevance of the new tests for flood hazard curves.

------------------------------------------------------------------------

11\. · 98% match · 2019 · 1.6 cit/yr\
**Hazard risks pertaining to partially submerged non-stationary vehicle on low-lying roadways under subcritical flows** ([link](https://doi.org/10.1016/j.rineng.2019.100032))\
Syed Hamid Hussain Shah, Z. Mustaffa, Eduardo Matínez‐Gomariz, K. Yusof, and E. Al-Qadami\
*Results in Engineering* · Sep 1, 2019 · 11 citations

> Abstract Rivers overflowing onto the floodplains can seriously disrupt the transportation system which can cause significant risks to moving or parked vehicles. The major flooding occurrence at the East Coast of Malaysia in December 2014 for instance, exhibited several hazards and fatalities involving vehicle submergence when the road conditions at low-lying flooded roadways were not known to the road users. To imitate a similar situation, the hydraulic characteristics of river overtopping an adjacent low-lying roadway during floods and the dynamics response of a vehicle attempting to cross over such flows were carried out in a modelled experimental set up. With that regards, a Perodua Viva which represents the medium-sized Malaysian passenger car was manufactured (1:10), ensuring similarity laws. Further, to monitor significant threats a flooded vehicle could face, the low-lying roadway model was designed to the allowable grade of five percent as proposed in Arahan Teknik (Jalan), ATJ 8/86. Keeping in view the height of the car and subcritical state of the flow, the range of water depths between 0.047 and 0.089 m, whereas for velocities, it was controlled to be in between 0.20 and 0.39 m/s, respectively. The buoyancy depth was noticed at depths greater than and equal to 0.055 m. Below critical depth, mode of sliding failure relied on the dominancy of varying horizontal pushing forces, namely frictional resistance, rolling friction, drag and driving forces.

------------------------------------------------------------------------

12\. · 94% match · 2021 · 0.5 cit/yr\
**FROUDE NUMBER VARIANCE WITH RESPECT TO THE HYDRODYNAMIC RESPONSE OF A NON-STATIC VEHICLE AT A LOW-LYING FLOODED ROADWAY** ([link](https://doi.org/10.31436/iiumej.v22i1.1502))\
Syed Hamid Hussain Shah et al.\
*IIUM Engineering Journal* · Jan 4, 2021 · 3 citations

> In terms of stability, the response of static cars in floodwaters has been widely investigated. However, the hydrodynamics of a non-static vehicle exposed to such events are less explored. Herein the study ponders the assessment of the hydrodynamic forces experienced by a non-static vehicle attempting to cross a low-lying flooded street. With that regards, a Perodua Viva was modeled (1:10) and tested in the Hydraulics Laboratory under partial submergence and sub-critical flows, fulfilling the similarity laws. Since the Froude number could best analyze the flow conditions, the behavior of the hydrodynamic forces and the Froude number have been the focus of this investigation. From the study of outcomes, an inverse relation of the Froude number with respect to the buoyancy force, along with positive trends relating to drag, frictional, and rolling resistance, were noticed. ABSTRAK: Dari segi kestabilan, tindak balas kereta statik dalam air banjir telah banyak dikaji. Walau bagaimanapun, hidrodinamik kenderaan tidak statik yang terdedah kepada kejadian seperti itu kurang diterokai. Kajian ini menilai daya hidrodinamik kenderaan tidak statik yang cuba melintas jalan raya yang banjir. Sehubungan itu, sebuah Perodua Viva dimodelkan (1:10) dan diuji dalam Makmal Hidraulik di bawah perendaman separa dan didedahkan kepada aliran sub-kritikal, seperti ketika kejadian. Manakala nombor Froude adalah terbaik dalam menganalisa keadaan aliran air. Oleh itu, tindak balas daya hidrodinamik dan nombor Froude menjadi fokus penyelidikan ini. Dapatan kajian menunjukkan kaitan terbalik nombor Froude pada daya apungan, sedangkan tren positif yang berkaitan dengan daya tarik, geseran dan rintangan guling diperhatikan.

------------------------------------------------------------------------

13\. · 91% match · 2021 · 2.6 cit/yr\
**Full-scale experimental investigations on the response of a flooded passenger vehicle under subcritical conditions** ([link](https://doi.org/10.1007/s11069-021-04949-6))\
E. Al-Qadami, Z. Mustaffa, Syed Hamid Hussain Shah, Eduardo Matínez‐Gomariz, and K. Yusof\
*Natural Hazards* · Jul 26, 2021 · 13 citations

------------------------------------------------------------------------

14\. · 88% match · 2010 · 0.2 cit/yr\
**Effect of Water Depth and Translational Velocity on Tire Force and Moment Characteristics** ([link](https://doi.org/10.4271/2010-01-0770))\
Jeffrey Dinges, D. F. Tandy, S. Hanba, and Jung Bae\
Apr 12, 2010 · 3 citations

------------------------------------------------------------------------

15\. · 86% match · 2019 · 2.1 cit/yr\
**Longitudinal hydroplaning performance of passenger car tires** ([link](https://doi.org/10.1080/00423114.2019.1693047))\
Markus Maleska, F. Petry, D. Fehr, W. Schuhmann, and M. Böhle\
*Vehicle System Dynamics* · Nov 19, 2019 · 14 citations

> ABSTRACT It is universally agreed that tire hydroplaning has a significant impact on road safety. The occurrence of this phenomenon makes it difficult to appropriately manage accelerating, braking or steering, due to a considerable reduction of wheel forces. In this research project, the longitudinal hydroplaning test was conducted, according to the common VDA test procedure under acceleration. Results are presented, which quantify test parameters during the measurement, such as vehicle velocity, gate distance and longitudinal tire slip ratio. The article further identifies the impact of test conditions (wheel normal load, tire inflation pressure and water depth) on the longitudinal hydroplaning performance. In addition, the respective dynamic tire footprint characteristics are determined and linked to the performance. In the course of the analysis, it is shown that the empirical equation, developed by Horne to predict the critical hydroplaning velocity of truck tires, can be applied to passenger car tires. These results contribute to enabling a better understanding of how footprint characteristics affect longitudinal hydroplaning performance under acceleration conditions.

------------------------------------------------------------------------

16\. · 83% match · 2020 · 3.0 cit/yr\
**Prediction of Hydroplaning Potential Using Fully Coupled Finite Element-Computational Fluid Dynamics Tire Models** ([link](https://doi.org/10.1115/1.4047393))\
Ashkan Nazari et al.\
*Journal of Fluids Engineering* · Jun 26, 2020 · 18 citations

> Hydroplaning is a phenomenon that occurs when a layer of water between the tire and pavement pushes the tire upward. The tire detaches from the pavement, preventing it from providing sufficient forces and moments for the vehicle to respond to driver control inputs such as breaking, accelerating, and steering. This work is mainly focused on the tire and its interaction with the pavement to address hydroplaning. Using a tire model that is validated based on results found in the literature, fluid–structure interaction (FSI) between the tire-water-road surfaces is investigated through two approaches. In the first approach, the coupled Eulerian–Lagrangian (CEL) formulation was used. The drawback associated with the CEL method is the laminar assumption and that the behavior of the fluid at length scales smaller than the smallest element size is not captured. To improve the simulation results, in the second approach, an FSI model incorporating finite element methods (FEMs) and the Navier–Stokes equations for a two-phase flow of water and air, and the shear stress transport k–ω turbulence model, was developed and validated, improving the prediction of real hydroplaning scenarios. With large computational and processing requirements, a grid dependence study was conducted for the tire simulations to minimize the mesh size yet retain numerical accuracy. The improved FSI model was applied to hydroplaning speed and cornering force scenarios.

------------------------------------------------------------------------

17\. · 80% match · 2013 · 0.4 cit/yr\
**Hydroplaning of Rolling Tires under Different Operating Conditions** ([link](https://doi.org/10.1061/9780784413005.045))\
S. Srirangam, K. Anupam, A. Scarpas, and C. Kasbergen\
Jul 9, 2013 · 5 citations

> In the present study, a three dimensional hydroplaning model was developed to quantify the hydroplaning speed at different operating conditions of tire under flooded pavement conditions. The hydroplaning speed was simulated for no slip and partial slip cases of tire. The hydroplaning speed was also computed for different yaw angles for rolling cases. Loss of braking traction due to hydroplaning is characterized by computing longitudinal friction force with respect to a variety of slip speeds up to hydroplaning. Impending hydroplaning risk on directional stability of vehicle was studied by plotting the cornering force against a range of rolling speeds up to hydroplaning. The fluid-structure-interaction was performed by means of the Coupled Eulerian Lagrangian approach in the finite element context. The proposed model provides insight on the influence of hydroplaning conditions on braking and steering efficiency of a vehicle.

------------------------------------------------------------------------

18\. · 77% match · 2026\
**Characterization of Vehicle Tire Hydroplaning Using Numerical Simulation and Field Full-Scale Accelerated Loading Methods** ([link](https://doi.org/10.3390/app16073433))\
Wentao Wang, Xiang Han, Hua Rong, Y. Miao, and Linbing Wang\
*Applied Sciences* · Apr 1, 2026 · 0 citations

> Increasingly frequent extreme rainfall commonly leads to water accumulation on the road surface, elevating vehicle tire hydroplaning to a major threat to driving safety. Existing research mainly focused on tire model optimization or predicting critical hydroplaning speed features based on empirical formulas and numerical simulations. However, there is a lack of systematic validation of the tire–water–pavement coupling interaction under realistic pavement conditions, with particular insufficient attention paid to pavement dynamic responses. In this study, numerical simulation and field full-scale accelerated loading methods were applied to investigate dynamic response characteristics of the tire–water–pavement coupling interaction system. Parametric analyses were first performed to investigate the influences of vehicle speed, vehicle load, water-film thickness, and tire lateral position on the mechanical behaviors of the fluid–structure interaction for a moving vehicle tire. Subsequently, field-measured dynamic responses’ features were used to validate the numerical model, which was then further applied to predict critical conditions of vehicle tire hydroplaning. Finally, the mechanisms of hydroplaning and corresponding mitigation measures were discussed. The study revealed that increasing vehicle speed and water-film thickness, as well as decreasing vehicle load, would reduce the pavement supporting force. The tire–pavement contact stress and strain decreased from the vehicle tire’s center position towards its shoulders. The predicted critical hydroplaning condition suggested that increasing vehicle load mitigated hydroplaning by reducing the proportion of water-induced hydrodynamic lifting force relative to the total vehicle load. When the water depth is relatively shallow, the hydroplaning risk increases rapidly with water depth, while the water’s adverse impact on tire–pavement contact force gradually diminishes as water depth continues to increase. It implies that a vehicle with a relatively low axle load driving on the pavement with a thin thickness of retained water in light rain will still face the hydroplaning risk, as the pavement’s supporting force may be substantially reduced in this weather. The findings provide theoretical foundations and experimentally supported insights on driving safety assessment and anti-skid design of water-covered pavement.

------------------------------------------------------------------------

19\. · 75% match · 2023 · 0.3 cit/yr\
**Predicting Vehicle Motion in Shallow Water with Data-Driven Hydrodynamics Model** ([link](https://doi.org/10.1115/detc2023-115254))\
Hiroki Yamashita et al.\
*Volume 10: 19th International Conference on Multibody Systems, Nonlinear Dynamics, and Control (MSNDC)* · Aug 20, 2023 · 1 citations

> In this study, a numerical procedure for predicting vehicle mobility in shallow water is proposed with the data-driven hydrodynamic force and moment model. To this end, the high-fidelity coupled CFD-MBD model is developed to characterize the hydrodynamic loads exerted on the vehicle in shallow water and used to generate the training dataset for the proposed data-driven model. The neural networks are called from the MBD mobility solver every time step to determine the hydrodynamic loads, given the current vehicle motion states and water conditions, allowing for predicting the transient responses of the vehicle interacting with shallow water. It is demonstrated by several numerical examples that the complex vehicle-water interaction behavior was accurately predicted by the proposed data-driven hydrodynamics model while achieving a substantial computational speedup.

------------------------------------------------------------------------

20\. · 72% match · 2014\
**A comparative study of four fluid-solid coupling methods for applications in ground vehicle mobility** ([link](https://www.semanticscholar.org/paper/2a3a1ddcee73fe17b8e6203c0322022c28c50616))\
A. Pazouki et al.\
0 citations

> Motivated by the desire to investigate vehicle fording scenarios, we analyze four frameworks for the simulation of the fluid-solid interaction problem. While all of these approaches rely on a general multibody dynamics simulation framework that supports impact, contact, and constraint, they differ in (i) the fluid representation; (ii) the simulation methodology; and (iii) the fluid-solid interfacing mechanism. The first approach relies on an explicit-implicit, Lagrangian-Lagrangian (LL), solution to the coupled Navier-Stokes and Newton-Euler equations of motion. The fluid momentum and continuity equations, dv dt =− 1 ρ ∇p+ μ ρ ∇2v+ f (1)

------------------------------------------------------------------------

21\. · 70% match · 2016\
**Investigation of the Vehicle Mobility in Fording** ([link](https://www.semanticscholar.org/paper/61da26b63ef7bf224b6a8cac098e077de207423d))\
A. Pazouki, P. Jayakumar, and D. Negrut\
May 29, 2016 · 0 citations

> Abstract : This contribution concerns a general purpose fluid-multibody system (MBS) simulation framework that can be used to analyze the fluid-solid, two-way coupled dynamics at low to medium Reynolds numbers (0 Re 1500). The simulation framework can be leveraged to investigate MBS applications that include (i) rigid and flexible bodies of arbitrary geometry; (ii) bilateral constraints (joints); (iii) unilateral constraints associated with impact and contact phenomena; and (iv) friction/cohesion.The fluid dynamics problem is formulated using the fluid momentum and continuity, i.e., Navier-Stokes equations. These equations are spatially discretized via a weakly compressible smoothed particle hydrodynamics (SPH) Lagrangian method \[1\], which relies on moving markers to store state information associated with fluid phase. The space dependent variables, such as velocity and pressure, are smoothed out locally via a scalar function. That is, to obtain a variable, a gradient, or a hydrodynamics force at an arbitrary location of the domain, one needs to account for partial contributions coming from nearby markers. External forces such as fluid-solid interaction (FSI) force are added to the hydrodynamics force. The fluid equations of motion, which upon spatial discretization become a set of ordinary differential equations, are solved explicitly using a second order Runge-Kutta integration method.Of several approaches that have been considered in the literature to model the fluid-solid coupling, we show that using a point-cloud discretization of a solid results in an accurate calculation of the fluid-solid coupling forces \[2\]. In this approach, the MBS dynamics is solved by providing the solver with distributed forces captured by the point cloud representation.

------------------------------------------------------------------------

22\. · 68% match · 2022 · 3.0 cit/yr\
**Coupled multibody dynamics and computational fluid dynamics approach for amphibious vehicles in the surf zone** ([link](https://doi.org/10.1016/j.oceaneng.2022.111607))\
H. Yamashita et al.\
*Ocean Engineering* · Aug 1, 2022 · 12 citations

------------------------------------------------------------------------

23\. · 64% match · 2021 · 0.4 cit/yr\
**Amphibious Vehicle Water Egress Modeling and Simulation Using CFD and Bekker’s Methodology** ([link](https://doi.org/10.4271/2021-01-0252))\
N. Tison\
*SAE Technical Paper Series* · Apr 6, 2021 · 2 citations

> ABSTRACT A significant challenge for wheel- and propeller-driven amphibious vehicles during swimming operations involves the egress from bodies of water. The vehicle needs to be able to swim to the ramp of a vessel, and then propel itself up the ramp using water propellers and wheels simultaneously. To accurately predict the ability of the vehicle to climb the ramp, it is important to accurately model: (1) the interaction of the flow through the propellers, around the vehicle hull, and away from the ramp; (2) the wheel / ramp interaction; (3) the suspension system spring, damping, and motion-limiting forces, tire deformation and loading characteristics, and wheel and hull motions (both translation and rotation); and (4) the drivetrain power distribution to the wheels. Detailed modeling and simulation of these physics and processes – such as the wheel, hull, and suspension system motions and force interactions, propeller rotation and resulting flow, etc. – would be highly computationally expensive. Therefore, to make the water egress problem more tractable to solve, various modeling simplifications – such as the use of an actuator disc methodology for propeller flow modeling and Wong’s terramechanics methodology for the wheel / ramp interaction – were introduced to facilitate rapid simulation. The integration of a customized six-degree-of-freedom (6DOF) body dynamics solver with a multiphase Volume of Fluid (VOF) computational fluid dynamics (CFD) solver (STAR-CCM+) resulted in an efficient, robust, comprehensive methodology for modeling and simulating amphibious vehicle water egress for various environmental and vehicle characteristics and operational conditions. Citation: N. Tison, “Wheeled Amphibious Vehicle Water Egress M&S Using CFD and Simplified Vehicle Modeling Methodologies”, In Proceedings of the Ground Vehicle Systems Engineering and Technology Symposium (GVSETS), NDIA, Novi, MI, Aug. 13-15, 2019.

------------------------------------------------------------------------

24\. · 61% match · 2023 · 1.5 cit/yr\
**Research on launching, water exiting, and river crossing of an amphibious vehicle** ([link](https://doi.org/10.1063/5.0174148))\
Bolong Liu, Xiaojun Xu, and Dibo Pan\
*Physics of Fluids* · Nov 1, 2023 · 4 citations

> The main focus of this paper is the amphibious vehicle’s water-land trans-media capability, specifically its ability to efficiently carry out transportation tasks in rivers and nearshore areas. This capability relies on three key processes: launching, water exiting, and river crossing. To study these processes, hydrodynamic numerical simulations are conducted. The Reynolds-averaged Navier–Stokes) equation, simplified terra mechanics model, and body force method are adopted to analyze the trans-media and self-propulsion processes. Results indicate that the optimal launching speed is around 15 km/h, with a stable trim and heave, and a launching angle range of 15°–25° for insubmersibility and stability. Furthermore, high-speed water exiting enhances insubmersibility and imposes lower requirements on road adhesion conditions, outperforming low-speed water exiting. In terms of self-propelled river crossing, higher heading angles and faster river currents improve hydrodynamic lift, with the fastest crossing achieved at a 10° heading angle for a current speed of 2.5 m/s and a forward speed of 30 km/h.

------------------------------------------------------------------------

25\. · 59% match · 2018 · 0.6 cit/yr\
**Instability Criteria for Vehicles in Motion Exposed to Flood Risks** ([link](https://doi.org/10.1051/MATECCONF/201820307003))\
Syed Hamid Hussain Shah, Z. Mustaffa, Do Kyun Kim, and K. Yusof\
5 citations

> Flooded roads have somewhat become a norm to the society and among the damages that floods can pose, there are fatalities and harm caused to people. Floating debris such as vehicles, manipulated by floodwaters could potentially cause harm not only to the public safety but also towards the public and private-owned properties. In the past, research on vehicle’s instabilities have been solely dedicated to static vehicles which are normally translated as vehicles parked on road surface. A vehicle when exposed to floodwater get influenced by different hydrodynamic forces and becomes prone to different instability modes, namely sliding, floating and toppling. Outcomes on such modes are somehow recognised in the works on static vehicles, but the mechanics of a moving vehicle under such influences have not been studied. Herein the influence of floodwater flows on the vehicle attempting to cross a flooded path (partial submergence) is presented. With that regards, a non-stationary model vehicle with the scale ratio of 1:10 (Perodua Viva) was used and a series of experiments were conducted. Moreover, a new formula to estimate the incipient velocity for a moving vehicle has been introduced and the prediction accuracy of the proposed formula has been validated using experimental data. Measurements were taken including approaching velocities and water depths, through which the instability was computed.

------------------------------------------------------------------------

26\. · 56% match · 2018 · 1.3 cit/yr\
**Influence of forces on vehicle’s instability in floodwaters** ([link](https://doi.org/10.1016/J.ASEJ.2018.01.001))\
Syed Hamid Hussain Shah, Z. Mustaffa, K. Yusof, and M. Nor\
*Ain Shams Engineering Journal* · Dec 1, 2018 · 10 citations

> Abstract Flood hazards to vehicle have become more frequent and noticeable in the recent years. Therefore, this paper aims at estimating the forces observed on a partially submerged vehicle in floodwater, namely frictional, buoyancy, lift and drag forces. An understanding of the relevant forces involved is necessary to attempt to characterize the instability thresholds of vehicles in floodwater flows. With that regards, a model vehicle with the scale ratio of 1:24 was used and a series of flume experiments were conducted. While determining the vertical pushing force, the influence of lift force was found insignificant due to sub-critical state of the flow. Moreover, the critical water depth at which the up-thrust force governed was observed when the water depth exceeded 0.042 m. Below critical depth, the vehicle stability governed unless the drag force imposed by the flowing water was lower than the frictional force between the tires and floodplain surface.

------------------------------------------------------------------------

27\. · 54% match · 2015 · 4.4 cit/yr\
**Drag and lift contribution to the incipient motion of partly submerged flooded vehicles** ([link](https://doi.org/10.1016/J.JFLUIDSTRUCTS.2015.06.010))\
C. Arrighi, J. C. Alcérreca‐Huerta, H. Oumeraci, and F. Castelli\
*Journal of Fluids and Structures* · Aug 1, 2015 · 48 citations

------------------------------------------------------------------------

28\. · 52% match · 2012 · 4.5 cit/yr\
**Experimental studies on the interaction between vehicles and floodplain flows** ([link](https://doi.org/10.1080/15715124.2012.674040))\
F. Teo, J. Xia, R. Falconer, and B. Lin\
*International Journal of River Basin Management* · Mar 21, 2012 · 65 citations

------------------------------------------------------------------------

29\. · 50% match · 2017 · 8.8 cit/yr\
**A new experiments-based methodology to define the stability threshold for any vehicle exposed to flooding** ([link](https://doi.org/10.1080/1573062X.2017.1301501))\
E. Martínez‐Gomariz, Manuel Gómez, B. Russo, and S. Djordjević\
*Urban Water Journal* · Mar 22, 2017 · 82 citations

------------------------------------------------------------------------

30\. · 48% match · 2023 · 1.0 cit/yr\
**Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling** ([link](https://doi.org/10.3390/su151713262))\
E. Al-Qadami, M. Razi, W. S. Damanik, Z. Mustaffa, and E. Martínez‐Gomariz\
*Sustainability* · Sep 4, 2023 · 3 citations

> A vehicle exposed to flooding may lose its stability and wash away resulting in potential injuries and fatalities. Traffic disruption, infrastructure damage, and economic losses are also additional effects of the washed vehicles. Therefore, understanding the responses of passenger vehicles during flood events is of the utmost importance to reduce flood risks and develop accurate safety guidelines. Previously, flooded vehicle stability was investigated experimentally, theoretically, and numerically. However, numerical investigations are insufficient, of which only a few studies have been published since 1967. Furthermore, coupled motion simulations have not been employed to investigate the hydrodynamic forces on flooded vehicles. In this paper, a numerical framework was proposed to assess the response of a full-scale medium-size passenger vehicle exposed to floodwaters through three-dimensional computational fluid dynamic modelling. The vehicle was simulated under subcritical and supercritical flows with the Froude number ranging between 0.09 and 2.46. The results showed that the vehicle experienced the floating instability mode once the flow depth reached 0.38 m, while the sliding instability mode was observed once the depth×velocity threshold function exceeded 0.36 m2/s. In terms of hydrodynamic forces, it was noticed that the drag force decreased with the increment of the Froude number and flow velocity. On the other hand, the fraction and buoyancy forces are mainly governed by the flow depth at the vehicle vicinity. The drag coefficient was noticed to be less than 1 for supercritical flows and more than 1 for subcritical flows. The numerical results obtained through the framework introduced in this study demonstrate favorable agreement with three different previously published experimental outcomes.

------------------------------------------------------------------------

31\. · 46% match · 2023 · 1.1 cit/yr\
**Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements** ([link](https://doi.org/10.1111/jfr3.12885))\
Fatima Azhar, V. Pauwels, and H. Bui\
*Journal of Flood Risk Management* · Jan 24, 2023 · 4 citations

> This study combines laboratory experiments and numerical modelling in a novel manner to assess vehicle stability. Assessing vehicle stability forms the basis of hazard classification criteria, which in turn helps in forming safety guidelines for stream crossings and planning of evacuation routes in times of floods. These criteria are based on theoretical and physical model studies carried out on different vehicle models. This article demonstrates the application of a numerical method to determine the vehicle stability threshold so that the need for a physical model study for each kind of vehicle may be avoided. The numerical investigation is performed using smoothed particle hydrodynamics (SPH) with the vehicle oriented perpendicular to the flow direction, as this is the most critical orientation. A physical model study is also performed and its results are used to validate the SPH model. The results confirm the current Australian Rainfall and Runoff (ARR) safety criteria for stationary vehicles. It also suggests that the ARR stability curve can shift depending on the road conditions that affect the vehicle’s sliding mechanism.

------------------------------------------------------------------------

32\. · 44% match · 2023 · 2.1 cit/yr\
**Experimental testing to determine stability thresholds for partially submerged vehicles at different flow orientations** ([link](https://doi.org/10.1016/j.jhydrol.2023.129525))\
Xiaozhe Hu, Junqi Li, Wenhai Wang, and X. Fang\
*Journal of Hydrology* · Apr 1, 2023 · 7 citations

------------------------------------------------------------------------

33\. · 42% match · 1967 · 0.6 cit/yr\
**LOW LEVEL CAUSEWAYS** ([link](https://www.semanticscholar.org/paper/598636f53664980764239c5563493dbed74956fc))\
A. Bonham and R. Hattersley\
Aug 1, 1967 · 37 citations

> THIS REPORT COVERS A LABORATORY STUDY OF THE HYDRAULICS OF WATER FLOW OVER LOW LEVEL CAUSEWAYS. HYDRAULIC INVESTIGATIONS INCLUDED MODEL STUDIES IN A FLUME TO DETERMINE LIFT AND DRAG EFFECT OF FLOOD FLOW ON A CAR ON A FLOODED CROSSING. THIS RESEARCH WAS CARRIED OUT TO ESTABLISH CRITERIA FOR THE SAFE DESIGN OF SUBMERSIBLE CAUSEWAYS FOR COUNTRY ROADS IN AUSTRALIA. /TRRL/

------------------------------------------------------------------------

34\. · 40% match · 1992 · 0.6 cit/yr\
**Stability of Cars and Children in Flooded Streets** ([link](https://www.semanticscholar.org/paper/c87e6816cba9960523f6df8f2990d9fd9626270e))\
R. Keller and B. Mitsch\
22 citations

> A procedure is presented for determining the stability of cars and children on flooded roadways. From specifications provided by car companies, buoyancy forces were determined for a range of water depths. A force balance was then established, linking the buoyant force, weight, frictional resistance, and drag force due to flowing water and the product of water velocity (V) and depth (D) at the point of instability was established. It is shown that this product varies with depth. The same procedure was applied to the case of children and all the results combined to produce a safe envelope of V x D versus D. The graph can be used as a design aid where streets must act as floodways in times of major flood events.

------------------------------------------------------------------------

35\. · 38% match · 2011 · 5.5 cit/yr\
**Incipient velocity for partially submerged vehicles in floodwaters** ([link](https://doi.org/10.1080/00221686.2011.616318))\
C. Shu, J. Xia, R. Falconer, and B. Lin\
*Journal of Hydraulic Research* · Nov 21, 2011 · 81 citations

------------------------------------------------------------------------

36\. · 36% match · 2011 · 6.5 cit/yr\
**Formula of incipient velocity for flooded vehicles** ([link](https://doi.org/10.1007/S11069-010-9639-X))\
J. Xia, F. Teo, B. Lin, and R. Falconer\
*Natural Hazards* · Jul 1, 2011 · 98 citations

------------------------------------------------------------------------

37\. · 34% match · 2022 · 0.7 cit/yr\
**Transient, 3D CFD, Moving Mesh Simulation of Vehicle Water Wading in a Water Tunnel with Inclined Entry-Exit** ([link](https://doi.org/10.4271/2022-01-0768))\
M. Varshney et al.\
*SAE Technical Paper Series* · Mar 29, 2022 · 3 citations

------------------------------------------------------------------------

38\. · 32% match · 2021 · 1.7 cit/yr\
**CFD Method Development for Simulating Water Fording for a Passenger Car** ([link](https://doi.org/10.4271/2021-01-0205))\
M. Varshney et al.\
Apr 6, 2021 · 9 citations

------------------------------------------------------------------------

39\. · 30% match · 1978\
**Study and Parametric Analysis of Trafficability, Running Gear, and Stability Considerations for Nearshore Bottom-Crawling Vehicles** ([link](https://www.semanticscholar.org/paper/9201d349e29cda64218f162e0a1857a7797063da))\
G. W. Turnage and W. Seabergh\
Dec 1, 1978 · 0 citations

> Abstract : The Surfzone Transition Analytical Methodology (STAM) is a computerized mathematical model that was developed to predict the trafficability and stability performance of bottom-crawling vehicles operating in the nearshore region (from shoreline to 150-ft water depth). STAM input requires detailed mathematical descriptions of (a) the vehicle’s design characteristics, (b) its performance requirements, and (c) the specific nearshore environment. From these descriptions, STAM predicts (a) vehicle trafficability performance in terms of vehicle/obstacle interference and vehicle ability to negotiate soft soil, develop drawbar pull, and maintain tractive force while operating on either a fine-grained or a coarse-grained ocean bottom, and (b) vehicle stability performance in terms of vehicle resistance to lateral and to longitudinal overturn, plus vehicle ability to maintain forward motion and to resist side sliding. STAM predicts the performance of only two-track, single-chassis bottom-crawling vehicles because this well-developed chassis/running gear combination was judged most suitable for near-future nearshore operations.

------------------------------------------------------------------------

40\. · 28% match · 2021 · 1.2 cit/yr\
**Fundamental study on underwater trafficability for tracked vehicle** ([link](https://doi.org/10.1016/j.jterra.2021.07.001))\
Mitsuru Yamada, Genki Yamauchi, and Takeshi Hashimoto\
*Journal of Terramechanics* · Sep 1, 2021 · 6 citations

> Abstract In recent years, water disasters have increased in Japan. In water disaster, remote controlled vehicles which work for disaster recovery must run in water environment. Since underwater ground is likely to be soft, the vehicle has a risk of stuck. If a vehicle gets stuck at disaster sites, rescue work is difficult because it is not easily to access to that area. We must make a method for judging whether to run or not. For this purpose, we must quantitatively clarify the relationship between the trafficability and the strength, bearing capacity, etc. of underwater ground. We measured the cone index of underwater ground. From results, we confirmed that fragile layer was formed on the surface layer in underwater ground. We measured drawbar pull of a tracked carrier in test field. As a result, maximum drawbar pull of underwater ground was lower than on the ground. After slip occurs, drawbar pull of underwater ground was smaller than ground significantly.

------------------------------------------------------------------------

41\. · 26% match · 1971 · 0.1 cit/yr\
**Trafficability of Soils: Effects of Surface Conditions on Drawbar Pull of a Wheeled Vehicle** ([link](https://www.semanticscholar.org/paper/2b14783f57bf7d62ad8ed0245a1cf3a1bf82c52b))\
E. S. Rush and J. Robinson\
Apr 1, 1971 · 3 citations

> “A study was conducted to (a) investigate the effects of soil surface conditions on one-pass drawbar pull capabilities of a wheeled vehicle, (b) relate optimum drawbar pull to soil strength as measured by several instruments, (c) develop tentative equations for predicting optimum tractive coefficient, and (d) determine effects of tire characteristics (tread pattern and deflection) on drawbar pull. One hundred and six drawbar pullslip tests were conducted with a 3/4-ton M37 truck at a gross weight of 7240 lb. One tire size (9.00-16, 8-PR), two tread patterns (smooth and nondirectional military), and two tire deflections (15% and 35%) were tested. Surface conditions varied from dry and firm, to wetted with small amounts of water, to flooded. Asphalt surfaces also were tested” (p. xi).

------------------------------------------------------------------------

42\. · 24% match · 2026\
**Geometry-Aware Surrogate for Real-Time Hydrodynamics Estimation of Autonomous Ground Vehicles in Amphibious Environments** ([link](https://www.semanticscholar.org/paper/66a0b8a7e37fdf711ad50974911187bf5c00f294))\
Ammar Waheed, Luke Gallantree, and Zohaib Hasnain\
May 18, 2026 · 0 citations

> Autonomous ground vehicles operating in shallow water or flood-prone terrains require dynamic models that account for hydrodynamic forces. However, the simulation and planning tools currently available either lack the physical fidelity or are too computationally expensive to run in real time. This work presents a per-surface neural network surrogate that bridges this gap by predicting geometry-resolved hydrodynamic forces at real-time rates, trained entirely on high-fidelity CFD data from two geometrically distinct vehicles. A vehicle specific Signed Distance Field (SDF) provides per-surface submergence inputs, allowing the model to resolve how loading varies with vehicle geometry, depth, and flow direction. On held-out CFD data, the surrogate achieves a longitudinal-force symmetric MAPE (sMAPE) of 13% and a vertical-force sMAPE of 3-12%, with inference running under 0.9,ms per sample. To evaluate the model under real-world conditions, water wading trials of a full-scale vehicle at different submersion depths are used. Motion capture derived kinematics serve as the surrogate inputs, and the resulting predictions are tested to reproduce known physical relationships between force, speed, and depth. The predicted drag follows quadratic speed scaling ($`R^2 \geq 0.97`$) and the buoyancy intercepts scale linearly with depth ($`R^2 = 0.973`$). Neither relationship is encoded in the model training loss, both emerge from the per-surface architecture summing individually predicted surface forces. The resulting framework provides a pathway for embedding physically grounded hydrodynamics into the simulation and planning loops that autonomous ground vehicles depend on in amphibious environments.

------------------------------------------------------------------------

43\. · 22% match · 2014 · 1.2 cit/yr\
**Stability and Drag Analysis of Wheeled Amphibious Vehicle Using CFD and Model Testing Techniques** ([link](https://doi.org/10.4028/www.scientific.net/AMM.592-594.1210))\
R. More, P. Adhav, K. Senthilkumar, and M.W. Trikande\
*Applied Mechanics and Materials* · Jul 1, 2014 · 14 citations

> Amphibious design of combat vehicle has become a challenging task in the context of increase in Gross Vehicle weight (GVW) of present generation combat vehicles due to demand for high protection levels and higher capacity engine and transmission, incorporation of multiple weapon systems, increased ammunition storage and larger addition of electrical and electronic items. Development of combat vehicles is complex and very expensive, and normally limited with less number of prototypes. The scale modeling and CFD analysis offers a viable solution to accomplish the amphibian design of a combat vehicle with adequate confidence before manufacturing the actual prototype. In the present work, an approach involving experimental towing test using scaled model and CFD simulation has been used to carry out the amphibious design of an 8X8, wheeled, combat vehicle with GVW of 22 ton. In this work, a 1/5th scaled model of the vehicle was manufactured and tested in the towing tank at different test speeds for drag and stability analysis. CFD analysis was carried out on the full scale model to gain adequate details about the dynamics of vehicle in the water in addition to drag estimation. Good correlation has been found in drag values and the flow patterns obtained from towing tank tests and CFD simulations.
