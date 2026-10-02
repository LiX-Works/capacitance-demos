# Sources, derivations, assumptions and reproducibility

## User-provided requirements

All five current tilted-capacitor Markdown files and the matching ZIP README were read in full before implementation. Their checksums and the precise reading scope are in READ_LOG.json. The files prescribe the question, fixed-hinge geometry, model hierarchy, real units, partial dielectric and actual HTML QA. They do not supply trusted measured results. Their physics suggestions were independently derived and numerically tested rather than accepted as facts.

Earlier ProxiTouch archives supplied a useful TypeScript/WebGL2 scene graph, renderer, camera math, some geometry generators, local KaTeX and offline bundle pattern. They do **not** supply this project's electrostatic parameter values, quantitative solver, analytical model, field arrays, scene copy or final capacitance values. The EH/EC/EB and EDL device subject was not carried into this new investigation.

## Primary references consulted

1. NIST, 2022 CODATA recommended values, complete constants listing. Used for epsilon0 = 8.8541878188e-12 F/m. Retrieved during this task. This is an accepted constant, not a material-specific dielectric measurement.
   https://physics.nist.gov/cuu/Constants/Table/allascii.txt
2. MIT, Electromagnetic Fields and Energy, chapter 4.1. Used as a primary teaching reference for electrostatic potential, Laplace/Poisson equations and boundary-value reasoning. The actual offset-hinge/local-gap equations in this project were derived independently from the chosen coordinates.
   https://web.mit.edu/6.013_book/www/chapter4/4.1.html
3. Simulation of floating potentials in industrial applications by boundary element methods, Journal of Mathematics in Industry (2014), DOI 10.1186/2190-5983-4-13. Consulted for the boundary-element and floating-potential formulation context. No code or numerical table in this delivery is copied from the article, and the article does not validate the delivered geometry.
   https://link.springer.com/article/10.1186/2190-5983-4-13
4. KaTeX upstream MIT license, for the included local formula-rendering module. The module was recovered from the prior project; it renders native MathML without distributing webfonts.
   https://raw.githubusercontent.com/KaTeX/KaTeX/main/LICENSE

A coplanar-strip research abstract (DOI 10.1016/j.elstat.2019.103371) and a conformal-line reference (Electronics 10(11),1272,2021) were also inspected as background. They were not treated as data for this device, and no inaccessible full-text derivation is claimed to have been read. The thin-strip elliptic expression is a limiting check, with its modulus convention and finite-thickness caveat stated in MODEL_DERIVATION/NUMERICAL_REPORT.

## What comes from where

- Geometry constraints and classroom goals: current five MD files.
- Selected dimensions, air approximation, slab er=4, fixed slab position and voltage: explicit modelling choices documented in parameters.json, tried and checked here.
- Rigid transform, g=2delta, h(x), overlap, logarithmic mean and dielectric local series integrals: this task's derivations.
- Ideal-sector model: separately specified boundary-value problem and its direct analytic solution, not a solution of the real finite plates.
- C(theta), field arrays, convergence, energy/charge comparisons and 3-D checkpoints: actual delivered Python solver outputs.
- Between-node display: disclosed interpolation, not another PDE solve.
- Scientific validation: internal computational validation only; no experiment or independent peer review occurred.

## Third-party software

TypeScript 5.8.3, licensed under Apache-2.0, is included as a locally repackaged offline compiler archive. It is not represented as a freshly downloaded registry artifact. KaTeX is included under MIT license. Python numerical/QA package versions are in requirements-reproduce.txt; they are needed only to recompute data or rerun QA, not to open the standalone HTML. No font file is included.

## Frozen evidence and fresh reproduction provenance

The maintenance pass retains the existing numerical dataset and `archive/qa-evidence/` exactly as historical outputs. No new full numerical reproduction or experimental validation is claimed. Fresh FVM and air-only 3-D checkpoint generation now records the byte SHA-256 of `parameters.json` and completion state. Enrichment accepts only complete checkpoints for the same parameters and records that hash in the generated dataset provenance. Missing historical hashes are not retroactively invented.

The FVM implementation is a separate discretization, but its dielectric outer Dirichlet potential is supplied by the 2-D BEM neutral reference at n=96. Only the air cases use zero outer potential. This dependency limits the independence of the dielectric comparison and is now documented without changing the algorithm or its inherited numbers. Fresh reproduction uses staging and checks failure/provenance before replacing delivered results.
