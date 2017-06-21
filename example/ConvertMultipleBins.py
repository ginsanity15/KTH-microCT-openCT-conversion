#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 14:59:50 2017

@author: Bo Gao

This file shows how to convert multiple binary files into Open CT format

Input data:
    Directory of targeted binary files

Output data:
    Open CT file (DICOM file)

"""



import sys
sys.path.insert(0, '/Users/starbury/odl/KTH-microCT-openCT-conversion/functions')

import conversion as conv
import os
import glob

# Given the directory of binary files, users may need to modify this variable 
# based on where they store those files
file_path = '/Users/starbury/odl/KTH-microCT-openCT-conversion/example/input_data/RawBinaryFiles/'

# Given the directory of output DICOM file, users may need to modify this 
# variable based on where they would like to store those files
output_path = '/Users/starbury/odl/KTH-microCT-openCT-conversion/example/output_data/'

# Given the location of DICOM tamplate, which is provided in the repository, 
# change this variable to the directory that the dicom templated is stored
templatename = '/Users/starbury/odl/KTH-microCT-openCT-conversion/functions/template.dcm'

# Acquire the number of binary files in the targeted folder
number =  len([name for name in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, name))])

# Counting the number of projection image been converted
i = 1
for filename in glob.glob(os.path.join(file_path, '*.bin')):
    outputname = output_path + 'projection_image' + str(i) + '.dcm'
    conv.Bin2dcm(filename, outputname, templatename)
    print(str(i) + ' out of ' + str(number) + ' images has been converted')
    i += 1