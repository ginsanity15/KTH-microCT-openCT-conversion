#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 15:27:54 2017

@author: Bo Gao

This file shows how to convert and calibrate multiple binary file into Open CT format

Input data:
    Directory of targeted binary files

Output data:
    Calibrated Open CT file (DICOM file)
    
"""

import sys
sys.path.insert(0, '/Users/starbury/odl/KTH-microCT-openCT-conversion/functions')

import conversion as conv
import calibration as cali
import os
import glob
import time

# Given the directory of binary files, users may need to modify this variable 
# based on where they store those files
file_path = '/Volumes/0767085190/20170423/LightField/'

# Given the directory of output DICOM file, users may need to modify this 
# variable based on where they would like to store those files
output_path = '/Volumes/0767085190/LCPhantom_C/'

# Given the location of DICOM tamplate, which is provided in the repository, 
# change this variable to the directory that the dicom templated is stored
templatename = '/Users/starbury/odl/KTH-microCT-openCT-conversion/functions/template.dcm'

# Given the location of the dark field image collected beforehand
dark_field = '/Users/starbury/odl/KTH-microCT-openCT-conversion/example/input_data/DarkField.dcm'

# Given the location of the light field image collected beforehand
light_field = '/Users/starbury/odl/KTH-microCT-openCT-conversion/example/input_data/LightField.dcm'

# Acquire the number of binary files in the targeted folder
number =  len([name for name in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, name))])

start_time = time.time()
# Counting the number of projection image been converted
i = 1
for filename in glob.glob(os.path.join(file_path, '*.bin')):
    outputname = output_path + 'projection_image' + str(i) + '.dcm'
    conv.Bin2dcm(filename, outputname, templatename)
    print(str(i) + ' out of ' + str(number) + ' images has been converted')
    cali.RemoveDeadPixel(outputname)
    cali.GeometryCalibration(outputname)
    cali.DarkFieldCalibration(outputname, dark_field)
    #cali.LightFieldCalibration(outputname, light_field)
    #cali.LogCalibration(outputname)
    print(str(i) + ' out of ' + str(number) + ' images has been calibrated')
    i += 1


print('All projection images have been converted')

# detector lag cannot be performed on each single image, as the effect of former
# projection image will have a summed up effect on later images, therefore, this
# calibration is performed after all DICOM files are generated
print('Now doing phase lag calibration in the entire folder...')
cali.PhaseLagCalibration(output_path)
print('All calibration finished')
print('Total time: ' + str(time.time() - start_time))
