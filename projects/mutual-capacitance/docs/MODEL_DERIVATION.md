# Geometry, analytical models and their boundaries

The governing source is the five new tilted-capacitor Markdown documents, not the earlier ProxiTouch EDL design. They specify goals and constraints, not an already-validated set of equations. This document records the derivation used in the delivered program. Coordinates are SI metres throughout the scientific model.

## 1. The physical definition

Let L = 20 mm be electrode length, b = 120 mm width, D = 1 mm the initial **clear face-to-face gap**, te = 0.1 mm metal thickness and delta = 1 mm the horizontal hinge offset. The lower conductor occupies x in [0,L], y in [-te,0], z in [-b/2,b/2]. The upper conductor initially occupies x in [0,L], y in [D,D+te], with the same z span. Both are ideal equipotential electronic conductors; metal conductivity and losses are outside the electrostatic calculation.

The hinge runs parallel to z through H = (-delta,D/2). For every upper-plate vertex p0,

    p(theta) = H + R(theta) (p0-H)
    R(theta) = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]

The lower conductor, dielectric slab and hinge do not move. No supplementary translation is applied to the upper plate. The renderer places the upper plate at a constant local position inside one pivot node; only the pivot rotation changes.

At theta = pi, an original point (x,y) maps to (-x-2delta,D-y). Consequently the upper rectangle becomes x in [-L-2delta,-2delta], y in [-te,0]. It is exactly coplanar with the lower finite-thickness conductor, and the physical edge-to-edge gap is

    g = 2 delta = 2.00 mm.

This result includes metal thickness. It is not a centre-plane approximation or a visually selected endpoint.

### Nonintersection

For 0 <= theta <= pi/2 the minimum upper-plate height is D/2 + delta sin(theta) + (D/2) cos(theta), which remains positive; for this parameter set it is at least 1 mm. For pi/2 <= theta <= pi, the rotated upper plate lies to the left of x = 0. Thus it neither intersects the fixed plate nor the selected dielectric region. In addition to this argument, the program checks 721 poses against the same polygon coordinates.

### Display clipping is not geometric distortion

One isotropic render scale maps metres to scene coordinates. No special vertical exaggeration or plate-thickness enlargement is used. The default view clips the central 28 mm of the 120 mm width so a 1 mm gap is readable. The UI discloses this, and the full-width control restores the complete 120 mm geometry. Cprime is always multiplied by the physical width b = 0.120 m, never by the display clipping width. The full-width control does not change any numerical value.

## 2. Local vertical-flux approximation on the actual geometry

For an initial point (u,D) on the facing surface of the upper plate,

    x = -delta + (u+delta) cos(theta) - (D/2) sin(theta)
    y = D/2 + (u+delta) sin(theta) + (D/2) cos(theta).

Eliminating u gives the true facing-plane height above the fixed electrode:

    h(x) = h0 + x tan(theta)
    h0 = (D/2)(1 + sec(theta)) + delta tan(theta).

For theta below 90 degrees, the positive projected overlap is

    W = max(0, min(L, -delta + (L+delta)cos(theta) - (D/2)sin(theta))).

The near edge of the upper projection lies left of x=0; the retained overlap is x in [0,W]. Approximate each strip of projected area b dx as a small parallel-plate capacitor. Then

    Cstrip = epsilon_air b integral[0,W] dx / h(x)
           = (epsilon_air b / tan(theta)) ln(h1/h0),
    h1 = h0 + W tan(theta).

The continuous theta -> 0 limit is epsilon_air bL/D. Using `log1p` avoids cancellation for small theta. Define the logarithmic mean gap

    dlog = (h1-h0)/ln(h1/h0),
    Cstrip = epsilon_air b W/dlog.

This keeps the actual rotation geometry while simplifying the field, not the other way around. Its restrictions are important: it treats the electric field locally as vertical, neglects coupling between strips and ignores edge/exterior fields. When projected overlap vanishes, the approximation is **undefined**, not a prediction of zero capacitance. The displayed curve stops instead of falsely continuing along the axis.

Even at zero angle the finite plates possess fringing fields. Here the ideal parallel-plate value is 21.2501 pF and the finite two-dimensional extrapolation is 23.3701 pF. Their approximately 9.07% difference, using the numerical result as the denominator, is a modelling difference rather than evidence that the solver failed its parallel limit.

## 3. A separate ideal wedge

To understand curved fields without claiming an exact solution of the finite opening plates, use a separate annular sector r0 <= r <= r1, 0 <= phi <= alpha. The radial faces are zero-thickness equipotential boundaries at 0 and DeltaV. The circular inner and outer boundaries are insulating. In this deliberately ideal domain,

    potential(r,phi) = DeltaV phi/alpha,
    E_phi = -DeltaV/(alpha r), E_r = 0,
    Cprime_sector = epsilon_air ln(r1/r0)/alpha,
    Csector = b Cprime_sector.

Equipotentials are radial, while field lines follow circles. This follows directly by substituting the potential into the polar Laplace equation and integrating surface charge or field energy. At alpha=60 degrees, r0=5 mm, r1=30 mm, b=120 mm and DeltaV=1 V, the result is 1.818 pF, with field magnitudes 191.0 V/m and 31.8 V/m at the inner and outer radii respectively.

The insulating arcs and zero-thickness faces are part of this exact ideal model. Real finite plates do not possess those insulating circular boundaries, and the ideal wedge is not drawn or described as the actual finite-thickness capacitor.

### Mapped candidate, not a universal correction

For theta>0 and W>0, intersecting the extended facing planes motivates r0=h0/tan(theta), r1=r0+W. The corresponding candidate is Cwedge=Cstrip_air tan(theta)/theta. A second-side candidate in the raw data adds the complementary angular-sector contribution with factor 1+theta/(2pi-theta). These are deliberately labelled candidates; neither has the correct open-end boundaries of the finite plates. The chart does not force either to fit by choosing an arbitrary multiplicative calibration. The small-angle limit matches the same strip limit; that alone does not make it globally accurate.

## 4. Partial dielectric and local series thickness

The slab is fixed at x=3..17 mm, y=0.125..0.525 mm, with the same extrusion width. Its thickness is t=0.400 mm and the main example has relative permittivity er=4. It is a generic lossless, linear, isotropic dielectric parameter, **not** a measured or certified named material. Air is approximated by vacuum permittivity; the small environmental correction is outside this model.

At each overlapped x within the slab footprint, approximate air plus dielectric as a local series stack. The effective electrical thickness is

    hel(x) = h(x) - t + t/er = h(x) - t(1-1/er).

Consequently

    Cdiel_strip = epsilon_air b [integral_uncovered dx/h(x)
                     + integral_covered dx/(h(x)-t(1-1/er))].

The integration domains are intersections with the **actual projected overlap**. Outside the slab, the original air term remains. Slab height above the lower electrode does not affect this local one-dimensional series sum, but it does affect the two-dimensional field solution. That distinction is itself a model limitation, not a reason to omit the slab position from the solver.

The finite BEM applies piecewise epsilon(x,y) at the real rectangular material boundary. Tangential E and normal D continuity determine induced interfacial charge; no uniform multiplication of the air solution is used.

## 5. Interpreting the number shown on screen

The main curve is C_2D = b Cprime. Cprime is the two-dimensional capacitance per unit extrusion width, in F/m; C_2D is an absolute capacitance estimate in F, displayed as pF. It is not labelled a measured value or a complete finite-width 3-D solution.

The extra three air-only 3-D calculations are independent checkpoints at 0,90,180 degrees, with all six conductor faces. They show that finite-width end effects grow from about 1.2% at the parallel configuration to about 7.55% at coplanarity for b/L=6. The application exposes this difference rather than hiding it in an unverified correction factor. It does not claim a whole-angle 3-D curve or a dielectric 3-D validation.

Discrete angle nodes and material-scan points are solved in advance. Between angle nodes the browser explicitly interpolates C and field data; it never presents an interpolated frame as a newly solved PDE. The numerical table, geometry, graph and captions consume the same frozen parameters and theta state.

### Finite-volume comparison boundary condition

The aligned-state finite-volume checker uses its own Cartesian spatial discretization and an artificial outer Dirichlet box. Air cases use outer potential zero. The asymmetric dielectric case uses the neutral common-potential reference from the 2-D BEM at n=96 for its outer faces. Its capacitance comparison therefore tests a separate discretization with a BEM-supplied boundary potential; it is not a fully independent dielectric boundary-value validation. The original algorithm and the frozen numbers are retained.
