r"""
=================================
EX1: Topology of Electron Density
=================================

Compute critical points and visualize it for cyclobutadiene.

"""

from chemtools import Molecule, UniformGrid, TopologicalTool

# 1. Build Topology model

mol = Molecule.from_file('c4h4.fchk')
cub = UniformGrid.from_molecule(mol, spacing=0.1, extension=0.1, rotate=False)
top = TopologicalTool.from_molecule(mol, points=cub.points)

# 2. Generate vmd script: fname.vmd
#    To visualize the iso-surface, use command: $ vmd -e fname.vmd

top.generate_scripts('c4h4.vmd')


# DISCARD BELOW:
# the code below is for displaying the ELF image on the website, you should remove it
# when running the script on your machine.
from tools.rug import plot_existing_image

plot_existing_image('top_c4h4.jpg')
