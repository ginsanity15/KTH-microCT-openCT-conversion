#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 13:57:31 2017

@author: Bo Gao

This file shows how to convert one binary file into Open CT format. 

Note: this file does not calibrate the images, it only converts raw
data to openCT-dicom

Input data:
    Directory of targeted binary files

Output data:
    Open CT file (DICOM file)

"""



import sys
sys.path.insert(0, '/home/davlars/KTH-microCT-openCT-conversion/functions')

import conversion as conv

# Given the location and name of the binary file, users may need to modify this
# variable based on where they store those files
filename = '/home/davlars/KTH-microCT-openCT-conversion/example/input_data/RawBinaryFiles/minict_20170423131500798_368114_0_1_0.bin'

# Given the location and name of output DICOM file, users may need to modify 
# this variable based on where they would like to store those files
outputname = '/home/davlars/KTH-microCT-openCT-conversion/example/output_data/ProjectionImage.dcm'

# Given the location of DICOM tamplate, which is provided in the repository, 
# change this variable to the directory that the dicom templated is stored
templatename = '/home/davlars/KTH-microCT-openCT-conversion/functions/template.dcm'

# Do the conversion, users can find the output file in the directory they name
conv.bin2dcm(filename, outputname, templatename)