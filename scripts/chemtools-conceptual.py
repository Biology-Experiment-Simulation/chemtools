#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ChemTools is a collection of interpretive chemical tools for
# analyzing outputs of the quantum chemistry calculations.
#
# Copyright (C) 2014-2015 The ChemTools Development Team
#
# This file is part of ChemTools.
#
# ChemTools is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ChemTools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
"""
Conceptual Density Functional Theory Script.

This script allows the user to use ChemTools from a command line.
"""


from __future__ import print_function

import sys
import argparse

from chemtools import HortonMolecule
from chemtools import __version__, CubeGen, print_vmd_script_isosurface
from chemtools import GlobalConceptualDFT, LocalConceptualDFT


def parse_args_global(arguments):
    """Parse command-line arguments for computing global conceptual DFT indicators."""
    # description message
    description = """
    """

    parser = argparse.ArgumentParser(prog='chemtools-conceptual.py global',
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version',
                        version="%%(prog)s (ChemTools version %s)" % __version__)

    # required arguments
    parser.add_argument('model', help='Energy model.')
    parser.add_argument('file_wfn',
                        help='Wave-function file. Supported formats: fchk, mkl, molden.input, wfn.')

    return parser.parse_args(arguments)


def parse_args_local(arguments):
    """Parse command-line arguments for computing local conceptual DFT indicators."""
    # description message
    description = """
    """
    parser = argparse.ArgumentParser(prog='chemtools-conceptual.py local',
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--version', action='version',
                        version="%%(prog)s (ChemTools version %s)" % __version__)

    # required arguments
    parser.add_argument('model', help='Energy model.')
    parser.add_argument('prop', type=str, help='The local property to plot iso-surface.')
    parser.add_argument('output_name', help='Name of generated cube files and vmd script.')
    parser.add_argument('file_wfn', nargs='*',
                        help='Wave-function file(s). Supported formats: fchk, mkl, molden.input, '
                             'wfn. If one files is provided, the frontier moleculer orbital (FMO) '
                             'approach is invoked, otherwise the finite difference (FD) approach '
                             'is taken.')

    # optional arguments
    parser.add_argument('--cube', default='0.2,4.0', type=str, metavar='N',
                        help='Specify the cubic grid used for visualizing iso-surface. '
                             'This can be either a cube file with .cube extension, or a '
                             'user-defined cubic grid specified by spacing and padding parameters '
                             'separated by a comma. For example, 0.2,5.0 which specifies 0.2 a.u. '
                             'distance between grid points, and 5.0 a.u. extension of cubic grid '
                             'on each side of the molecule. This cube is used for evaluating '
                             'the local property and visualizing the iso-surface using VMD. '
                             '[default=%(default)s]')
    parser.add_argument('--isosurface', default=0.005, type=float,
                        help='iso-surface value of local property to visualize. '
                             '[default=%(default)s]')
    # parser.add_argument('--color', default='b', type=str,
    #                     help='color of reduced density gradient vs. signed density scatter plot. '
    #                     '[default=%(default)s]')
    return parser.parse_args(arguments)


def main_conceptual_global(args):
    """Build GlobalConceptualDFT class and print global descriptors."""
    # build global tool
    model = GlobalConceptualDFT.from_file(args.file_wfn, args.model)
    # print available descriptors
    print(model)


def main_conceptual_local(args):
    """Build LocalConceptualDFT class and dump a cube file of local descriptor."""
    # load the first molecule
    mol = HortonMolecule.from_file(args.file_wfn[0])

    # make cubic grid
    if args.cube.endswith('.cube'):
        # load cube file
        cube = CubeGen.from_cube(args.cube)
    elif len(args.cube.split(',')) == 2:
        # make a cubic grid
        spacing, threshold = [float(item) for item in args.cube.split(',')]
        cube = CubeGen.from_molecule(mol.numbers, mol.pseudo_numbers, mol.coordinates,
                                     spacing, threshold)
    else:
        raise ValueError('Argument cube={0} is not recognized!'.format(args.cube))

    # build global tool
    model = LocalConceptualDFT.from_file(args.file_wfn, args.model, cube.points)
    # check whether local property exists
    if not hasattr(model, args.prop):
        raise ValueError('The {0} local conceptual DFT class does not contain '
                         '{1} attribute.'.format(args.model, args.prop))
    if callable(getattr(model, args.prop)):
        raise ValueError('The {0} argument is a method, please provide an attribute of '
                         '{1} local conceptual DFT.'.format(args.prop, args.model))

    # name of files
    cubefile = '{0}.cube'.format(args.output_name)
    vmdfile = '{0}.vmd'.format(args.output_name)
    # dump cube file of local property
    cube.dump_cube(cubefile, getattr(model, args.prop))
    # generate VMD scripts for visualizing iso-surface with VMD
    print_vmd_script_isosurface(vmdfile, cubefile, isosurf=args.isosurface)


if __name__ == '__main__':
    # get command-line arguments & task
    command_args = sys.argv[1:]
    task = command_args.pop(0)

    if task == 'global':
        # parse command-line arguments
        parsed_args = parse_args_global(command_args)
        main_conceptual_global(parsed_args)

    elif task == 'local':
        # parse command-line arguments
        parsed_args = parse_args_local(command_args)
        main_conceptual_local(parsed_args)

    elif task == 'condensed':
        raise NotImplementedError("")

    else:
        raise ValueError("Task not recognized! options: [global, local, condensed].")
