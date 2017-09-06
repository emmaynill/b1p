#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import openbabel
import numpy as np
from optparse import OptionParser
from simulation_iterator import simulation_iterator
from Particles import Particles

def die(message = ''):
    print('An error occurred')
    if message:
        print(message)

    sys.exit(1)

def die_prompt(message=''):
    print(message)
    res = raw_input('Type y for exit: ')
    if res == 'y':
        sys.exit(1)

def handle_arguments():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="get crystal structure from FILE", metavar="FILE")
    parser.add_option("-s", "--spin", dest="spin", help="Set the simulated spin", metavar="SPIN")
    parser.add_option("-l", "--dampening", dest="l", help="(OPTIONAL) Set the dampening factor", metavar="DAMP")
    parser.add_option("-T", "--temperature", dest="T", help="Set the temperature", metavar="TEMP")
    parser.add_option("-B", "--magneticfield", dest="B", help="Set the external B field, comma delimited (-B x,y,z)", metavar="MAGN")
    parser.add_option("-N", "--iterations", dest="N_simulation", help="Set the amount of iterations", metavar="ITER")
    parser.add_option("--dt", dest="dt", help="Set the dt", metavar="DT")

    (options, args) = parser.parse_args()

    if not options.filename:
        die('An inputfile is required!')

    denominator = 1
    if options.spin:
        if '/' in options.spin:
            denominator = float(options.spin.split('/')[1])

        options.spin = float(options.spin.split('/')[0]) / denominator

    if not options.spin or options.spin < 2:
        die_prompt('This simulation uses semiclassical approximations that are best for spin 2 or higher! Are you sure you want to continue?')

    if options.l:
        options.l = float(options.l)
    else:
        options.l = 5e-4

    if options.T:
        options.T = float(options.T)
    else:
        die('You must set the temperature!')

    if options.B and ',' in options.B:
        B = options.B.split(',')
        options.B = np.array([0, 0, 0], dtype='float64')

        if B[0]:
            options.B[0] = float(B[0])

        if B[1]:
            options.B[1] = float(B[1])

        if B[2]:
            options.B[2] = float(B[2])

    else:
        print('No external B field applied')
        options.B = np.array([0, 0, 0])

    if options.N_simulation:
        options.N_simulation = int(options.N_simulation)
    else:
        die('You must set the iterations (N_simulation)!')

    if options.dt:
        options.dt = float(options.dt)
    else:
        die('You must set the dt (for example 4.14e-15)!')

    return options

def handle_constant_properties(options):
    # Set data directory
    # TODO: Optional parameter for data dir.
    options.data_dir = os.path.dirname(os.path.abspath(__file__)) + '/data'

    # Ensure data dir exists
    if not os.path.isdir(options.data_dir):
        os.makedirs(options.data_dir)

    """
    Physical quantities
    """
    options.k_b = 1.38064852e-23
    options.g = -2.002
    options.mu_b = 9.274009994e-24
    options.hbar = 1.054571800e-34
    options.J = -0.142 * options.k_b
    options.gamma = options.g * options.mu_b / options.hbar

    return options

def handle_molecule_from_file(options):
    obConversion = openbabel.OBConversion()
    obConversion.SetInAndOutFormats("cml", "mdl")

    mol = openbabel.OBMol()
    obConversion.ReadFile(mol, options.filename)

    return Particles(mol, options)

def main():
    options = handle_arguments()
    options = handle_constant_properties(options)

    particles = handle_molecule_from_file(options)

    results = simulation_iterator(options, particles)

    return results

if __name__ == '__main__':
    main()
