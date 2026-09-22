## 2010 Toyota Yaris Detailed Finite Element Model
**Version 2j, released October 2016**

The Toyota Yaris finite element (FE) model was developed by [Center for
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

Addition information can be found in the [Validation][doi:10.13021/G8CC7G].

[CCSA]: https://www.ccsa.gmu.edu/
[doi:10.13021/G8CC7G]: https://dx.doi.org/10.13021/G8CC7G "2010 Toyota Yaris Finite Element Model Validation Detail Mesh"

![2010 Toyota Yaris Detailed Finite Element Model](https://www.ccsa.gmu.edu/wp-content/uploads/2016/10/2010-toyota-yaris-detailed-v2.png)

### Contacts
Rudolf Reichert  <reichert@gmu.edu> (703) 993-4565  
Dhafer Marzougui <dmarzoug@gmu.edu> (703) 993-4680  
Steve Kan        <cdkan@gmu.edu>    (703) 993-5896  

### LS-DYNA Input files
1. yaris-detailed-v2j.key
  
  Based on VIN JTDBT4K37A4067025.
  
  This file includes the complete vehicle model (parts, materials, sections,
  connections, nodes). It is 1,519,587 elements.
  
  The vehicle model includes the interior components (instrument panel, seats,
  trim, etc.) that are indispensable for occupant protection analysis.
  
  The vehicle model had been validated towards full scale destructive tests
  provided by NHTSA & IIHS, and non-destructive tests performed by CCSA at
  FOIL/FHWA and others. Additionally, coupon tests were performed in order to
  get the physical properties of different components.
  
2. set-yaris-detailed-v2j.key
  
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
