#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:36:44 2017

@author: Bo Gao

This file shows how to convert multiple binary files into Open CT format

Input data:
    Directory of targeted binary files

Output data:
    Open CT file (DICOM file)

"""



import sys
sys.path.insert(0, '/home/davlars/KTH-microCT-openCT-conversion/functions')

import conversion as conv
import os
import glob
import dicom
import calibration as cali

# Given the directory of Dark Current Images stored as binary files, users may 
# need to modify this variable based on where they store those files
file_path = '/media/davlars/0767085190/20170423/DarkCurrent/'

# Given the directory of output DICOM file, users may need to modify this 
# variable based on where they would like to store those files
output_path = '/home/davlars/KTH-microCT-openCT-conversion/example/output_data/'

# Given the location of DICOM tamplate, which is provided in the repository, 
# change this variable to the directory that the dicom templated is stored
templatename = '/home/davlars/KTH-microCT-openCT-conversion/functions/template.dcm'

# Acquire the number of binary files in the targeted folder
number =  len([name for name in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, name))])

# Counting the number of projection image been converted
for filename, i in zip(glob.glob(os.path.join(file_path, '*.bin')), range(number)):
    img = conv.bin2img(filename, templatename)
    if i == 0:
        DC = img/number
    else:
        DC += img/number
    print(str(i+1) + ' out of ' + str(number) + ' Dark Field images has been considered')
    
ds = dicom.read_file(templatename)
ds.PixelData = DC.astype('uint16')

# Remove dead pixels and calibrate geometries
ds = cali.RemoveDeadPixel(ds)
ds = cali.GeometryCalibration(ds) 

# Save data
outputname = output_path + 'Dark_Field.dcm'
ds.save_as(outputname)