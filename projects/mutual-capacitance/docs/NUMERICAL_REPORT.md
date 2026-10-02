# Numerical report: actual computed data

The values below are the inherited frozen outputs of the delivered Python solvers, not a new computation in this maintenance pass, a normalized graphic or an experiment. Original numerical evidence is preserved under `archive/qa-evidence/`; fresh optional reproduction writes new evidence to `qa/`. Parameter SHA-256: `0b23ce74c9b690fd5c79d335ed52ef88341d4925891863338356a1401cbbac52`.

## Frozen parameter set

| Parameter | Value |
|---|---|
| L | 20 mm |
| b | 120 mm |
| Initial clear gap D | 1 mm |
| Metal thickness | 0.1 mm |
| Fixed hinge H | (-1 mm, 0.5 mm) |
| Final gap g | 2 mm = 2 delta |
| Excitation difference | 1 V |
| Air relative permittivity | 1, explicit approximation |
| epsilon0 | 8.8541878188e-12 F/m, NIST 2022 CODATA |
| Dielectric | x=3..17 mm; y=0.125..0.525 mm; er=4 |

Three candidate gaps (0.5, 1 and 2 mm) were actually tried with scaled local slab dimensions before selecting D=1 mm. It balances a visible gap, a measurable dielectric effect and a pF-scale result. No artificial attempt was made to force the result into microfarads. The trial values are saved in `archive/qa-evidence/parameter-trials.json`.

## 1. Unbounded 2-D reference method

The main solver is a constant-panel collocation boundary element method (BEM), with finite-thickness conductor rectangles and endpoint-graded panels. It uses analytic panel integrals of the normalized Green function -ln(r/L)/(2 pi), including the logarithmic self term. A unit potential difference and zero total free conductor charge determine the floating common potential. There is no artificial far box in this BEM.

Dielectric interface charge is solved from the jump implied by normal displacement continuity. The dielectric is a genuine finite rectangular region; it is not applied afterward as a global capacitance multiplier. The dielectric net-bound-charge residual is retained as a discretization diagnostic. It is not silently forced to zero. The discrete collocation approximation has a small nonzero bound-net residue, so its far-field neutrality should not be interpreted as analytically exact at finite panel count.

The displayed main sweep uses 128 panels on each length-normalized long edge: 536 total conductor panels in air and 728 panels including the dielectric. All 44 angle nodes have both air and er=4 solutions: 88 cases. Seven additional er values at theta=0 are solved for the material scan. Base scan settings are in parameters.json; extra near-zero angles are inserted explicitly by physics/generate.py to resolve the steep early response.

| theta | Air C_2D (pF) | Slab er=4 C_2D (pF) | Dielectric increase |
|---:|---:|---:|---:|
| 0 deg | 23.370050 | 29.807120 | 27.5441% |
| 1 deg | 20.013204 | 24.325101 | 21.5453% |
| 5 deg | 13.579972 | 15.165572 | 11.6760% |
| 10 deg | 10.236198 | 10.985625 | 7.3213% |
| 30 deg | 5.904305 | 6.062518 | 2.6796% |
| 60 deg | 4.139060 | 4.189919 | 1.2288% |
| 90 deg | 3.465322 | 3.491185 | 0.7463% |
| 150 deg | 3.043164 | 3.054790 | 0.3821% |
| 160 deg | 3.037703 | 3.048314 | 0.3493% |
| 180 deg | 3.073527 | 3.082590 | 0.2949% |

The shallow minimum and small late-angle rise are retained. A monotonically falling visual curve was not imposed. At 180 degrees the slab remains over part of the fixed electrode, relatively far from the narrow inter-electrode slot; its effect is therefore much smaller than at the initial parallel state. This is a result for this placement, not a universal dielectric rule.

## 2. Local and ideal-sector models

| theta | Air strip error relative to C_2D | Mapped wedge-candidate error |
|---:|---:|---:|
| 0 deg | -9.071% | -9.071% |
| 1 deg | -10.330% | -10.321% |
| 5 deg | -14.678% | -14.461% |
| 10 deg | -19.613% | -18.787% |
| 15 deg | -24.476% | -22.702% |
| 30 deg | -39.754% | -33.569% |
| 60 deg | -73.797% | -56.661% |
| 80 deg | -95.595% | -82.107% |

The strip error already includes neglected finite-edge effects at 0 degrees. Thus there is no demonstrated sub-10% interval for this particular uncorrected local model except close to zero. There is no asserted universal angle threshold or candidate winner. Once overlap vanishes, local curves are undefined rather than artificially set to zero.

## 3. Boundary-panel refinement

| theta | er | C at n=64 (pF) | C at n=128 (pF) | C at n=192 (pF) | last relative change |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 23.369619 | 23.370050 | 23.370156 | 0.00046% |
| 0 | 4 | 29.806629 | 29.807120 | 29.807414 | 0.00099% |
| 30 | 1 | 5.904106 | 5.904305 | 5.904350 | 0.00077% |
| 30 | 4 | 6.062020 | 6.062518 | 6.062495 | 0.00037% |
| 90 | 1 | 3.465177 | 3.465322 | 3.465356 | 0.00096% |
| 90 | 4 | 3.490887 | 3.491185 | 3.491176 | 0.00025% |
| 180 | 1 | 3.073362 | 3.073527 | 3.073564 | 0.00123% |
| 180 | 4 | 3.082324 | 3.082590 | 3.082600 | 0.00031% |

The largest absolute dielectric bound-net-charge ratio in the displayed er=4 sweep is 0.01977% of the positive free charge; the largest algebraic residual in those 88 main cases is 1.473e-07. Matrix residuals and successive-grid changes are not rigorous physical error bounds. A higher-panel comparison can have a larger raw algebraic residual because of conditioning while its capacitance remains stable. The complete, unfiltered values are retained in `archive/qa-evidence/numerical-validation.json`.

## 4. Finite-volume grid and outer-domain check

A separate nonuniform Cartesian finite-volume discretization (FVM) is used at the aligned 0/180-degree states. Material faces use distance-weighted harmonic permittivity. Unlike the unbounded BEM, this checker has an artificial Dirichlet box, whose size is varied. The outer potential is zero for the air cases. For the asymmetric dielectric case (er=4), `physics/fvm_check.py` takes the floating neutral reference potential from a 2-D BEM solve with n=96; its boundary condition therefore depends on BEM. The dielectric row checks a different spatial discretization under that supplied boundary value, not a fully independent boundary-value solution. The conductor-face distance excludes the ideal-conductor half-cell, a detail corrected during development before the final report.

| theta | er | local cell size | box half extent | Q-derived C (pF) | difference to BEM |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 100 um | 80 mm | 23.335362 | -0.1487% |
| 0 | 1 | 50 um | 80 mm | 23.362656 | -0.0319% |
| 0 | 1 | 25 um | 80 mm | 23.373586 | +0.0148% |
| 180 | 1 | 100 um | 80 mm | 3.098856 | +0.8233% |
| 180 | 1 | 50 um | 80 mm | 3.108792 | +1.1466% |
| 180 | 1 | 25 um | 80 mm | 3.112786 | +1.2765% |
| 180 | 1 | 50 um | 160 mm | 3.075558 | +0.0653% |
| 180 | 1 | 50 um | 320 mm | 3.067627 | -0.1927% |
| 0 | 4 | 50 um | 120 mm | 29.796270 | -0.0370% |

The maximum charge-versus-energy capacitance difference in this FVM table is 0.0508%. These are two evaluations of the same discrete field, not two independent experiments. At 180 degrees, mesh refinement in the smaller fixed box does not converge monotonically toward the unbounded BEM because outer-boundary error remains. Expanding the box at 50 um cells reduces the discrepancy from roughly +1.15% at 80 mm to +0.065% at 160 mm and -0.193% at 320 mm. This exposes competing mesh and truncation effects instead of hiding them.

## 5. Coplanar thin-strip limit

For two equal zero-thickness coplanar strips in a homogeneous medium, use k=g/(2L+g) and Cprime=epsilon K(1-k^2)/K(k^2), where the K arguments shown are the SciPy parameter m convention. This is a limiting check, not an assertion that the 0.1 mm-thick electrodes are thin sheets.

The thin result is 2.996666 pF. The actual finite-thickness solution at 180 degrees is about 3.07353 pF, approximately 2.57% larger. Reducing thickness in a separate solve approaches the thin result:

| thickness | computed C (pF) | relative to thin formula |
|---:|---:|---:|
| 100.0 um | 3.073551 | +2.5657% |
| 20.0 um | 3.015272 | +0.6209% |
| 2.0 um | 2.999001 | +0.0780% |

The exact input/result rows above are preserved verbatim because they identify each tested thickness.

## 6. Real finite-width 3-D checkpoints

A separate air-only constant rectangular-panel BEM integrates 1/r analytically over all six faces of each finite rectangular conductor. It imposes the same voltage difference and total-charge neutrality as the 2-D problem. No periodic extrusion is used. Three actual meshes (528, 1360, 2576 panels) were solved at each of three angles.

| theta | 528 panels (pF) | 1360 panels (pF) | 2576 panels (pF) | finest excess over C_2D | last grid change |
|---:|---:|---:|---:|---:|---:|
| 0 deg | 23.569949 | 23.634366 | 23.649741 | +1.196% | 0.065% |
| 90 deg | 3.657869 | 3.688806 | 3.696443 | +6.669% | 0.207% |
| 180 deg | 3.264697 | 3.297469 | 3.305710 | +7.553% | 0.250% |

These checks quantify the finite-width limitation: about +1.20%, +6.67%, +7.55% at 0,90,180 degrees respectively. They are not a converged whole-angle 3-D reference, a rigorous uncertainty interval, or a dielectric 3-D validation. The application distinguishes the 3-D diamonds from the main C_2D curve. It does not stretch a three-point correction over every angle.

## 7. Invariants, generated field data and display accuracy

The ten Python validation checks cover endpoint geometry, collision exclusion, panel convergence, er=1, zero dielectric thickness, shrinking slab thickness, width scaling, voltage invariance, arbitrary logarithmic reference scale in neutral air, the coplanar thin limit and the strip parallel limit as grouped in the machine-readable report. Fifteen frontend checks additionally compare the browser transforms, SI-unit conversion, samples, analytical formula values and data decoding to the Python output.

Full field maps use a 117 by 101 display sampling grid over x=-30..28 mm, y=-10..30 mm. A material-detail window uses 141 by 96 samples over x=-3..23 mm, y=-0.55..4.2 mm. Changing the sampling window does not change the solved geometry. Potential is stored in volts and field magnitude in V/m via 16-bit encodings. The field magnitude palette explicitly saturates below about 32 V/m and above about 3162 V/m; this is not a representation of a mathematically resolved conductor-edge peak.

The main solver traces a fixed family of field paths. The display chooses a bounded subset and repeats them in several z slices to show the 2-D section spatially. This is not a full 3-D field-line solution. There are no moving particles presented as charges travelling through air. Finite node interpolation smooths the display; it does not claim exact topology at every unsolved angle.

## 8. Scope not validated

No fabricated sensor, measurement, mechanical hinge design, drive frequency, leakage, dielectric loss, breakdown field, certified material, thermal/air environmental correction, material anisotropy or full 3-D dielectric sweep was validated. The reported absolute numbers are credible reproducible results of explicitly stated electrostatic models, not laboratory readings.

## 9. Fresh interpolation midpoint checks

An additional 86 solves (43 interval midpoints for each of air and er=4) were compared with the browser's linear C interpolation. The largest sampled relative difference was 1.4776%. This is a measured interpolation discrepancy at the tested midpoints, not a rigorous bound over every possible angle. Main curve nodes remain the independently solved values, and non-node UI readouts continue to be explicitly marked as interpolated. The corresponding independent checks are in archive/qa-evidence/interpolation-check.json.

## 10. Maintenance verification and reproduction guards

The maintenance pass preserves all numerical arrays and historical evidence. Fresh generation stops if any required numerical validation check fails. Fresh FVM and 3-D reports record the exact `parameters.json` byte SHA-256 and a completion flag; enrichment rejects missing, mismatched or incomplete checkpoint provenance before solving new fields. Historical reports without these fields remain historical evidence and cannot be silently reused as fresh checkpoints.

`physics/reproduce.py` runs the whole chain against copied inputs in a temporary staging directory, then checks parameter provenance and all required outputs before publishing. A failed solve or validation leaves the previously delivered numerical data untouched. Fast safety regressions use synthetic runners to exercise rejection and rollback; they do not constitute a rerun of the scientific sweep.
