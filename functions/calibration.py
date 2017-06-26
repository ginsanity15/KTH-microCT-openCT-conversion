#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:46:18 2017

@author: Bo Gao

This file includes functions to perform different kinds of calibration.

Input data:
    Projection images store in DICOM-CT-PD format.

Output data:
    Modified OpenCT data with calibrated projection image and updated value at
    the corresponding tag in header file.

Requirements:
    numpy: fundamental package for scientific computing with Python
    
    pydicom (import as dicom): Module developed by [1] that serves to read, 
    modify and write DICOM files with python code. 
    
    _dicom_dict.py: As now the goal is to generate DICOM-CT-PD format, instead 
    of standard DICOM file, the look up dictionary provided in Pydicom 
    (_dicom_dict.py) cannot be directly used. Instead, users who are interested
    in converting KTH-STH-microCT data to DICOM-CT-PD should substitute the 
    '_dicom_dict.py' file under pydicom's path with the '_dicom_dict.py' provided
    in this repository.

[1] Github user: scaramallion
"""

import numpy as np
import dicom
import os
import glob

def RemoveDeadPixel(DICOM_name):
    ds = dicom.read_file(DICOM_name)
    img = ds.pixel_array
    # Below four lines serves to remove region of dead pixels on detector, what
    # we did is to substitute region correspond to dead pixels with neighbor 
    # region that does not have dead pixel
    img[7,:] = img[9,:]
    img[2350:2400,:] = img[1:51,:]
    img[2356,:] = img[2355,:]
    img[:,2251:2400] = img[:,1:150]
    img[27, 1882] = img[27,1883]
    img[52, 482] = img[52, 483]
    img[198, 612] = img[197, 612]
    img[207, 67] = img[207, 66]
    img[257, 383] = img[257, 382]
    img[273, 340] = img[273, 341]
    img[273, 713] = img[273, 714]
    img[274, 712] = img[273, 714]
    img[274, 713] = img[273, 714]
    img[275, 712] = img[273, 714]
    img[356, 487] = img[356, 488]
    img[367, 545] = img[367, 546]
    img[403, 1432] = img[403, 1433]
    img[439, 75] = img[439, 76]
    img[459, 1512] = img[459, 1513]
    img[496, 205] = img[496, 206]
    img[524, 1634] = img[524, 1635]
    img[628, 691] = img[628, 692]
    img[632, 920] = img[632, 921]
    img[657, 206] = img[657, 207]
    img[770, 2161] = img[770, 2162]
    img[876, 514] = img[876, 515]
    img[979, 429] = img[979, 428]
    img[1097, 689] = img[1097, 688]
    img[1098, 689] = img[1098, 688]
    img[1123, 2065] = img[1123, 2064]
    img[1352, 702] = img[1352, 701]
    img[1407, 434] = img[1407, 433]
    img[1463, 11] = img[1463, 10]
    img[1572, 402] = img[1572, 401]
    img[1604, 333] = img[1604, 332]
    img[1712, 422] = img[1712, 421]
    img[1749, 2180] = img[1749, 2181]
    img[1787, 2369] = img[1787, 2368]
    img[1822, 547] = img[1822, 548]
    img[1838, 1959] = img[1838, 1958]
    img[1839, 1973] = img[1839, 1972]
    img[1867, 1155] = img[1867, 1154]
    img[1882, 1673] = img[1882, 1672]
    img[1893, 2085] = img[1893, 2084]
    img[1949, 2088] = img[1949, 2087]
    img[1992, 60] = img[1992, 61]
    img[1999, 312] = img[1999, 313]
    img[1999, 578] = img[1999, 579]
    img[2019, 414] = img[2019, 413]
    img[2019, 415] = img[2019, 414]
    img[2020, 413] = img[2020, 412]
    img[2020, 414] = img[2020, 412]
    img[2020, 415] = img[2020, 412]
    img[2044, 470] = img[2044, 470]
    img[2051, 2144] = img[2050, 2144]
    img[2059, 1822] = img[2058, 1821]
    img[2071, 2189] = img[2070, 2188]
    img[2092, 371] = img[2091, 370]
    img[2120, 207] = img[2119, 206]
    img[2258, 761] = img[2257, 760]

    # Store the calibrated projection image back
    ds.PixelData = img
    # Modify tag: BadPixelCorrectionFlag to inform the user dead pixels in 
    # projection image have been removed
    ds.BadPixelCorrectionFlag = 'YES'
    ds.save_as(DICOM_name)
    
def GeometryCalibration(DICOM_name):
    # correction parameters for geometry, credit to Lorenzo and University of Arizonal
    pUP = 29
    pLEFT = 13
    ds = dicom.read_file(DICOM_name)
    img = ds.pixel_array
    Mup = img[:,0:pUP]
    Mdown = img[:,pUP:]
    img = np.append(Mdown, Mup, axis=1)
    Mleft = img[0:pLEFT,:]
    Mright = img[pLEFT:,:]
    img = np.append(Mright, Mleft, axis=0)
    # Store the calibrated projection image back
    ds.PixelData = img
    # No corresponding tag in header file
    ds.save_as(DICOM_name)

def DarkFieldCalibration(DICOM_name, DarkField):
    ds = dicom.read_file(DICOM_name)
    DF = dicom.read_file(DarkField)
    img = ds.pixel_array
    DarkCurrent = DF.pixel_array
    img = (img-DarkCurrent)
    # No pixel could have a value larger then 4096
    img[img>4096] = 0
    # Store the calibrated projection image back
    ds.PixelData = img
    # Modify tag: DarkFieldCorrection to inform the user this kind of correction
    # has been made
    ds.DarkFieldCorrectionFlag = 'YES'
    ds.save_as(DICOM_name)
 
# It seems DICOM can only store data of type 'unit16', since LightField correction
# and log calibration will change the intensity of something into the range of [0,1]
# Before DICOM changes its standard, below two kinds of calibration are not recommended
# to perform at pro-processing stage
def LightFieldCalibration(DICOM_name, LightField):
    ds = dicom.read_file(DICOM_name)
    LF = dicom.read_file(LightField)
    img = ds.pixel_array
    LightF = LF.pixel_array
    LightF[LightF == 0] = np.max(LightF)
    # Store the calibrated projection image back
    # Store it as "float16" as the division applied below will automatically change
    # the data from "float16" to "float64"
    ds.PixelData = (img/LightF).astype('float16')
    # Modify tag: FlatFieldCorrection to inform the user this kind of correction
    # has been made
    # Flat Field Correction is a private tag, we need to define its index and 
    # assign value through its index
    ds.add_new(0x70391006, 'CS', '1')
    ds[0x70391006].value = 'YES'
    ds.save_as(DICOM_name)
    
def LogCalibration(DICOM_name):
    ds = dicom.read_file(DICOM_name)
    img = ds.pixel_array
    img = -np.log(img)
    # After log calibration, information stored in img is attenuation coefficient,
    # which cannot be smaller than 0
    img[img<0] = 0
    # Store the calibrated projection image back
    ds.PixelData = img.astype('float16')
    # Modify tag: FlatFieldCorrection to inform the user this kind of correction
    # has been made
    ds.LogFlag = 'YES'
    ds.save_as(DICOM_name)

# Unlike function given above, Phase Lag Calibration cannot be performed on one
# single image

# Probably we should design it to proceed one folder of DICOM files
def PhaseLagCalibration(dicom_folder_path):
    # correction parameters for Phase Lag, credit to Lorenzo
    step = 4
    a = step * np.array([3.71, 0.33, 0.027])
    b = np.array([0.99, 0.0019, 0.0012])
    
    # i will be used as a flag to determine if the DICOM image currently 
    # being processed is the first projection image
    i = 0
    
    # Load in uncorrected projection image
    for filename in glob.glob(os.path.join(dicom_folder_path, '*.dcm')):
        ds = dicom.read_file(filename)
        img = ds.pixel_array
        size_n, size_m = img.shape
        if i == 0:
            phase = np.zeros([size_n, size_m], dtype = 'uint16')
            S1 = np.zeros([size_n, size_m], dtype = 'uint16')
            S2 = np.zeros([size_n, size_m], dtype = 'uint16')
            S3 = np.zeros([size_n, size_m], dtype = 'uint16')    
        S1 = img - phase + S1*np.exp(-a[0])
        S2 = img - phase + S2*np.exp(-a[1])
        S3 = img - phase + S3*np.exp(-a[2])
        phase = (b[0]*S1*np.exp(-a[0]) + b[1]*S2*np.exp(-a[1]) + b[2]*S3*np.exp(-a[2]))
        phase = phase.astype('uint16')
        img = img - phase
        # After Phase Lag calibration, intensities at certain pixels may drop
        # to a value lower than zero, code below can forbid this from happening
        img[img<0] = 0
        # Store the calibrated projection image back
        ds.PixelData = img
        
        # No corresponding tag in header file
        ds.save_as(filename)
        # Go to calibrate next image
        i += 1 
        
