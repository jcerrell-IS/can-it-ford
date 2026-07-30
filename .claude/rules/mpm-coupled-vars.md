---
paths:
  - "**/*vehicle*.py"
  - "**/*mpm*.py"
  - "**/box_sdf*.py"
---
Vehicle box dimensions, particle density (rho), and total mass are coupled.
Never edit one without recomputing the other two. rho = mass / (n_particles * h^3),
so changing grid_density or box dimensions silently changes rho even if you
didn't touch it. Before any commit touching these files, print the resulting
rho and compare against the target curb weight.
