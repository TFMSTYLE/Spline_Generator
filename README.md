# Spline Generator

![spline-thumb](https://github.com/user-attachments/assets/39b6c86b-8448-485a-b835-8a6fd0a977a2)

**Author:** The French Monkey (TFMSTYLE)  
**Version:** 1.0.4  

---

## Overview

The Spline Generator creates complex, parametric curve systems — from simple spirals and waves to fractal structures and chaotic attractors.  
Each curve is defined mathematically, allowing for precise and procedural generation of unique spline patterns.  
The add-on includes three main categories of shapes — **Simple**, **Fractal**, and **Chaotic** — each containing a wide variety of parametric functions.  
Perfect for use in motion graphics, generative art, scientific visualization, or as base curves for modeling and geometry node workflows.

---

## Parameters

### Category
Defines the main family of spline generation algorithms.  
Available categories include:

- **Simple:** Classical geometric and mathematical splines.  
- **Fractal:** Recursive and self-similar curves.  
- **Chaotic:** Dynamical system attractors and non-linear trajectories.

---

### Shape Type
Specifies the particular mathematical function used to generate the curve.  
Shape options depend on the selected **Category**:

#### Simple Shapes
Includes parametric forms such as:
- **Spiral**, **Helix**, **Wave**, **Zigzag**  
- **Lissajous**, **Spirograph**, **Rose**  
- **Superformula**, **Torus Knot**, **Butterfly**, **Golden Spiral**  
- **Vortex**, **Infinity**, **Ripple Ring**, **Twist Ribbon**

#### Fractal Shapes
Includes recursively generated and self-similar structures:
- **Koch Curve**, **Dragon Curve**, **Hilbert Curve**  
- **Lévy C Curve**, **Tree**, **Peano Curve**  
- **Spiral Fractal**, **Fractal Vine**, **3D Cantor Spiral**  
- **Sierpiński Triangle**, **Logarithmic Spiral**

#### Chaotic Shapes
Includes complex attractor systems and differential equations:
- **Lorenz**, **Rössler**, **Aizawa**, **Chen**, **Dadras**, **Halvorsen**  
- **Thomas**, **Rikitake**, **Chua**, **Rabinovich**, **Dequan–Li**  
- **Hadley**, **Burke–Shaw**, **Lü–Chen**, **Black Hole Vortex**

---

### Segments
Controls the number of evaluated points along the curve.  
Higher values increase precision and smoothness but can impact performance.

---

### Size
Sets the global scale of the generated spline.  
Affects all coordinate magnitudes proportionally.

---

### Offset
Applies variation to internal curve parameters depending on the algorithm.  
Typically affects spiral expansion, deformation, or phase shifts.

---

### Wave
Modulates sinusoidal or oscillatory displacement along the spline.  
Used to add ripples, turbulence, or undulations to base shapes.

---

### Symmetry
Defines the symmetry count or iteration multiplier used by certain patterns.  
For attractors and mathematical curves, it often influences periodicity or complexity.

---

### Height
Controls the amplitude of vertical or Z-axis displacement.  
Useful for adding 3D relief or depth to otherwise planar splines.

---

### Fractal Depth
Specifies the number of recursive iterations for fractal-based splines.  
Higher values produce greater detail and self-similar complexity.

---

## Operators

### Generate Spline
Creates a new spline object based on the selected category, shape type, and parameters.  
The curve is generated as a 3D polyline, suitable for extrusion, geometry node instancing, or further modification.

---

## Usage Notes

- Select a **Category** to access relevant spline types.  
- Adjust **Segments**, **Size**, and **Height** to scale and refine the curve.  
- Use **Offset** and **Wave** to introduce organic variation.  
- Increase **Fractal Depth** carefully for recursive shapes to avoid excessive complexity.  
- Generated curves are fully procedural and can be converted to mesh or used as curve modifiers.  
- Chaotic attractors like **Lorenz** and **Rossler** may require fine-tuning for balanced output.  
- Ideal for procedural modeling, animation paths, and parametric design workflows.
