## 2007 Chevrolet Silverado Detailed Finite Element Model
**Version 3e, released November 2016**

The Chevrolet Silverado finite element (FE) model was developed by [Center for
Collision Safety and Analysis][CCSA] researchers at George Mason University. The
effort was sponsored by the Federal Highway Administration.

The model was created for use with the LS-DYNA FE program, and is continuously
updated to improve its capabilities in predicting responses in various impact
scenarios. Any feedback to improve the model is welcomed and highly encouraged.

Users of the model must verify their own simulations. Neither CCSA or FHWA
assume any responsibility for the validity, accuracy, or applicability of
results obtained from this model.

We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this FE
model resulting in papers and publications.

[CCSA]: https://www.ccsa.gmu.edu/
[doi:10.13021/G8F312]: https://dx.doi.org/10.13021/G8F312 "2007 Chevrolet Silverado Finite Element Model Validation Detail Mesh"

![2007 Chevrolet Silverado Detailed Finite Element Model](https://www.ccsa.gmu.edu/wp-content/uploads/2016/11/2007-chevrolet-silverado-v3.png)

### Contacts
Dhafer Marzougui <dmarzoug@gmu.edu> (703) 993‒4680  
Fadi Tahan       <tahan@gmu.edu>    (703) 993‒4633
Steve Kan        <cdkan@gmu.edu>    (703) 993‒5896  

### LS-DYNA Input files
1. silverado-detailed-v3e.key
  
  Based on VIN 2GCEC13C771511793.
  
  This file includes the complete vehicle model (parts, materials, sections,
  connections, nodes). It is 963,474 elements.
  
  The vehicle model had been validated towards full scale destructive tests
  provided by NHTSA, IIHS, & others, and non-destructive tests performed by CCSA
  at FOIL/FHWA and others. Additionally, coupon tests were performed in order to
  get the physical properties of different components.
  
2. set-silverado-detailed-v3e.key
  
  This file is used to set the simulation parameters. Simple modifcations can be
  made to this file to run different impact configurations. The file includes:
  
    - Added masses (for dummies and cargo/luggage)
    - Vehicle `*INITIAL_VELOCITY` (setup with rotating front and rear wheels)
    - `*SET_PART` for `*CONTACT_INTERIOR` (foam and rubber solids)
    - `*SET_PART` for vehicle contact (most vehicle components)
    - `*SET_NODE_LIST` for contact with ground (tires)
    - Instrumentations for measuring accelerations and intrusions
  
3. wall.key
  
  U.S. NCAP rigid wall model.
  
4. combine.key
  
  This file is used to combine the vehicle model with a barrier or another
  vehicle using the `*INCLUDE` keyword. This file also contains all the control
  cards and time intervals for the output databases.
  `*CONTACT_AUTOMATIC_SINGLE_SURFACE` is included for the vehicle components,
  and between the vehicle and barrier or another vehicle. The
  `*CONTACT_INTERIOR` is also included in this file, since only one can be
  defined and may be needed for the vehicle and barrier or two vehicles.
  
  The provided `combine.key` file is set for **NCAP Frontal Wall Impact** and
  can be easily changed to simulate other impacts.
  
#### Model units
  - Mass **t**: metric ton (1,000 kg)
  - Length **mm**: millimeter
  - Force **N**: newton
  - Time **s**: second
