# Permission request to CCSA at George Mason, DRAFT, NOT SENT

Drafted 2026-08-26. **Nothing here has been sent.** Josie sends it, or does not.

Suggested route: the contact address on https://www.ccsa.gmu.edu/. If a named maintainer for the
2010 Toyota Yaris coarse v1l model can be found in the upstream README, address it to them and
copy the general address.

Suggested subject: **Permission to redistribute the 2010 Toyota Yaris FE model in a public
research repository**

---

Dear CCSA team,

I am an undergraduate researcher at Claremont McKenna College. This past summer I took part in
the NSF SCIPE REU at the Texas Advanced Computing Center, working with Dr. Krishna Kumar's group
at UT Austin on a project called Can It Ford, which compares a standard flood-safety rule for
vehicles against coupled material-point simulation.

The 2010 Toyota Yaris coarse v1l finite element model your group developed under FHWA
sponsorship is the vehicle geometry in that work. I converted the LS-DYNA deck into a watertight
surface mesh and every simulation result in the project runs on it. I am grateful for it: a
crash-validated model is what let an undergraduate project use real vehicle geometry instead of
a box.

I am writing about two things.

**First, acknowledgement.** The README shipped with the model asks that CCSA at GMU and the FHWA
be acknowledged in papers and publications. I want to confirm the wording I am using is what you
would want:

> The 2010 Toyota Yaris finite element model used in this work was developed by researchers at
> the Center for Collision Safety and Analysis (CCSA) at George Mason University, under
> sponsorship of the Federal Highway Administration (FHWA). We acknowledge CCSA at GMU and the
> FHWA, as requested by the model distributors. Neither CCSA nor FHWA assumes any responsibility
> for the validity, accuracy, or applicability of the results presented here.

**Second, redistribution, which is the actual question.** My project code is in a public GitHub
repository, and the repository currently also contains copies of the model files themselves, so
that anyone can reproduce the mesh conversion from the original deck rather than trusting my
output. That is roughly 160 MB across 22 files, including `yaris-coarse-v1l.key`.

I could not find any licence, copyright notice or redistribution statement shipped with the
model, so I do not want to assume that redistributing it is permitted. I would rather ask than
presume.

Would you be willing to confirm one of the following?

1. Redistribution of the model files in a public research repository is permitted, with the
   acknowledgement above.
2. Redistribution is permitted under specific conditions, which you would state.
3. Redistribution is not permitted, in which case I will remove the files and instead document
   how to obtain them from you directly.

Whichever the answer, I will follow it. If it is 3, I would appreciate guidance on how you would
like the model referenced so that the work stays reproducible without redistributing anything.

Thank you for making these models available, and for any guidance you can give.

Best regards,

Josie Cerrell
Integrated Sciences, Claremont McKenna College
jcerrell29@cmc.edu
Repository: https://github.com/jcerrell-IS/can-it-ford

---

## Notes for Josie before sending

- **Option 3 is a real possibility.** Decide before sending whether you are willing to remove the
  files, because the email promises you will. Removing from `HEAD` alone does not unpublish
  them: history rewriting would be needed, and `docs/CCSA_LICENCE_DECISION_2026-08-26.md`
  section C sets out what that costs.
- The 160 MB figure is measured: 22 files, 160,322,098 bytes on `origin/main`.
- Do not describe the models as NHTSA-hosted. Whether the canonical Yaris copy is NHTSA-hosted or
  CCSA-hosted is unresolved, and the phrasing above avoids claiming either.
- Consider copying Dr. Kumar, since a reply may bear on the paper.
