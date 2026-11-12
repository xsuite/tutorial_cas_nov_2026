# Xsuite hands-on — CAS, November 2026

Learn to build accelerator lattices, match their optics, and track particles with **Xsuite**. This tutorial explores electron storage-ring design and FCC-ee optics and beam–beam effects through Jupyter notebooks.

**[Setup instructions](setup_instructions.md)** · **[Check your installation](test_your_install.ipynb)** · **[Introduction slides](intro_slides.pptx)**

## Tutorial programme

| Part | Format | Topics | Start here |
| --- | --- | --- | --- |
| **00 · Introduction** | **Tutor-led demonstrations** | The Xtrack environment, lattice assembly, Twiss calculations and optics matching | [Introduction notebooks](00_introduction/) |
| **01 · Synchrotron design and comparison** | **Student exercises** | Build FODO and DBA rings; compare radiation equilibrium and dynamic aperture | [Assignment](01_synchrotron_design_and_comparison/notebook_00_synchrotron.ipynb) |
| **02 · FCC-ee optics and beam–beam** | **Student exercises** | Compare optics and alignment sensitivity; study beam–beam interactions and crab sextupoles | [Assignment](02_fccee_optics_and_bb/notebook_00_fccee.ipynb) |

The tutors will show the **00** notebooks; students do not need to modify them. In **01** and **02**, work through the numbered notebooks and complete the missing code.

### Optional exercises

- **Synchrotron design:** add RF and track with mean and quantum radiation; explore how quadrupole misalignments generate vertical emittance.
- **FCC-ee:** match optics with five times larger IP beta functions, distinct from the factor-eight optics supplied for the comparison exercises.

## Getting started

1. Follow the [setup instructions](setup_instructions.md) and run [the installation check](test_your_install.ipynb).
2. Clone this repository, or download it using **Code → Download ZIP**:

   ```bash
   git clone https://github.com/xsuite/tutorial_cas_nov_2026.git
   cd tutorial_cas_nov_2026
   jupyter notebook
   ```

3. Open a notebook in its tutorial folder and run its cells from top to bottom. Keep the supplied folder structure so the notebooks can find their input files.

For the synchrotron exercises, build and save the FODO and DBA rings before starting the radiation and tracking comparisons. The FCC-ee lattice and optics files are already supplied.

## Solutions

Each exercise set has a dedicated solution folder, including the input JSON files needed to run its notebooks:

- [Synchrotron design solutions](01_synchrotron_design_and_comparison/solution/)
- [FCC-ee solutions](02_fccee_optics_and_bb/solution/)

## Xsuite resources

- [User’s guide](https://xsuite.readthedocs.io/en/latest/usersguide.html) — examples and workflows
- [API reference](https://xsuite.readthedocs.io/en/latest/apireference.html) — classes and methods
- [Physics manual](https://xsuite.github.io/xsuite/docs/physics_manual/physics_man.pdf) — models and equations
- [GitHub](https://github.com/xsuite/xsuite) — source code and issue tracker
