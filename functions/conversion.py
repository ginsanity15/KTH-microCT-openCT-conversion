#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 20:59:51 2017

@author: Bo Gao


The following is the utility script used to convert binary output data from the 
KTH-STH microCT to odl-compatible OpenCT data.

Input data:
    Binary data collected on CMOS flat panel sensor C7942CA-22 manufactured by 
    Hamamatsu. For reference, please visit the link given below.
    https://www.hamamatsu.com/resources/pdf/ssd/c7942ca-22_kacc1160e.pdf

Output data:
    DICOM-CT-PD format (aka OpenCT data), which is vendor-neutral DICOM images. 
    Each DICOM image corresponds to a projection of a CT scan, and can be 
    divided into two components following the DICOM standard, the header and 
    the image. The header stores information regarding the gantry geometry, 
    the x-ray energy spectrum, and the table movement. The image stores the 
    projection image. A CT exam consists of a series of DICOM-CT-PD files, 
    each corresponding to a projection at a specific viewing angle and table 
    location [1].

Requirements:
    numpy: fundamental package for scientific computing with Python
    
    pydicom (import as dicom): Module developed by [2] that serves to read, 
    modify and write DICOM files with python code. 
    
    _dicom_dict.py: As now the goal is to generate DICOM-CT-PD format, instead 
    of standard DICOM file, the look up dictionary provided in Pydicom 
    (_dicom_dict.py) cannot be directly used. Instead, users who are interested
    in converting KTH-STH-microCT data to DICOM-CT-PD should substitute the 
    '_dicom_dict.py' file under pydicom's path with the '_dicom_dict.py' provided
    in this repository.
    
    template.dcm: This file is also included in this repository. In short, it
    is an empty DICOM file that doesn't include anything.
    


[1] Chen, Baiyu, et al. "Technical Note: Development and validation of an 
    open data format for CT projection data." Medical physics 42.12 (2015): 
    6964-6972.
[2] Github user: scaramallion
    
"""

import numpy as np
import dicom

def Bin2dcm(filename, outputname, templatename):
    ds = dicom.read_file(templatename)
    f = open(filename,'r')
    counter = 0
    # Input information to header file of OpenCT data, as information created 
    # below comes directly from the detector, no modification should be made
    # here
    temp = np.fromfile(f, dtype=np.uint8, count=4)
    counter += 4

    ds.version = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1

    ds.imageNx = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.imageNy = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.windowX0 = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.windowY0 = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.windowX1 = np.fromfile(f, dtype=np.int16, count=1)
    counter += 2

    ds.windowY1 = np.fromfile(f, dtype=np.int16, count=1)
    counter += 2

    ds.numberOfSummedImages = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.frameWidth_ms = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.triggerWidth_ms = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2

    ds.dataType = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1

    ds.binningMode = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1

    ds.triggerMode = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1

    ds.sumMode = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1

    ds.xRayOn = np.fromfile(f, dtype=np.uint8, count=1)
    counter += 1
    
    ds.cycleId = 0
    ds.targetType = 0
    ds.imageNumer = 0
    if ds.version > 1:
        ds.ycleId = np.fromfile(f, dtype=np.uint32, count=1)
        counter += 4
        ds.targetType = np.fromfile(f, dtype=np.uint8, count=1)
        counter += 1
        ds.imageNumer = np.fromfile(f, dtype=np.uint32, count=1)
        counter += 4
        
    ds.acquisitionDate = np.fromfile(f, dtype = 'c', count=23)
    counter += 23
    
    ReferringPhysicianLength = np.fromfile(f, dtype=np.uint16, count=1)
    counter += 2
    ds.ReferringPhysicianName = 'BoGao'
    if (ReferringPhysicianLength > 0):
        ds.ReferringPhysicianName = np.fromfile(f, dtype= 'c', count = ReferringPhysicianLength)
        counter += ReferringPhysicianLength

    blankPartSize = 512 - counter
    nosense = np.fromfile(f, dtype=np.uint8, count=blankPartSize)

    prec = np.uint8
    
    if ( ds.version==1 ):
        #This is because there was a bug in version 1
        if ( ds.dataType==1 or ds.dataType==0 ):
            prec=np.uint16
        if ( ds.dataType==2 ):
            prec=np.uint32
    else:
        #version 2 works well
        if ( ds.dataType==0 or ds.dataType==3 ):
            prec=np.uint8
        if ( ds.dataType==1 or ds.dataType==4 ):
            prec=np.uint16 
        if ( ds.dataType==2 or ds.dataType==5):
            prec=np.uint32 
        if ( ds.dataType==6 ):
            prec=np.float32 
        if ( ds.dataType==7 ):
            prec=np.dtype('d')

    length = ds.imageNx[0].astype(int)
    width = ds.imageNy[0].astype(int)
    img=np.fromfile(f, dtype = prec, count = length*width)
    img=np.reshape(img, [length, width])
    
    # Store projection data, we can't use "pixel_array" here, as it is 
    # designed only for read in data, instead, use the tag:"PixelData"
    ds.PixelData = img
    
    # Put information in Header File that are not included in binary file
    # output by the sensor. Based on the setting of micro-CT, parameters in
    # this section may require certain change
    ds.ReconstructionPixelSpacing = [0.05,0.05]
    ds.RotationDirection = 'CW'
    ds.NumberOfFramesInRotation = (300)
    ds.StartAngle = (0)
    ds.ScanArc = (2*np.pi)
    ds.NumberofDetectorRows = (2400)
    ds.NumberofDetectorColumns = (2400)
    ds.DetectorElementTransverseSpacing = (120)
    ds.DetectorElementAxialSpacing = (120)
    ds.DistanceSourceToDetector = (369.6)
    ds.DistanceSourceToPatient = (260)
    ds.RadialPosition = (109.6)
    ds.DetectorBinning = [1, 1]
    ds.PatientName = 'Phantoms'
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    ds.SOPInstanceUID = '1.3.6.1.4.1.9590.100.1.2.17353085712120733511713534870901379162'
    ds.Modality = 'micro-CT'
    ds.Manufacturer = 'STH_KTH'
    ds.KVP = 40
    ds.HUCalibrationFactor = 0.8096
    ds.DataCollectionDiameter = 369.6
    ds.ExposureTime = 1500
    ds.XrayTubeCurrent = 600
    ds.SpiralPitchFactor = 0
    ds.StudyInstanceUID = 'First_Instance'
    ds.SeriesInstanceUID = 'MicroCT.LowContrastPhantom1'
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.SamplesPerPixel = (1)
    ds.PhotometricInterpretation = 'MONOCHROME2'
    ds.Rows = (2400)
    ds.Columns = (2400)
    ds.RescaleIntercept = ''
    ds.RescaleSlope = ''
    ds.DetectorSystemArrangementModule = 'CT IMG ACQUISITION'
    ds.DetectorShape = 'FLAT'
    ds.DetectorDynamicsModule = 'CT IMG ACQUISITION'
    ds.SourceDynamicsModule = 'CT IMG ACQUISITION'
    ds.DetectorElementTransverseSpacing = 120
    ds.DetectorElementAxialSpacing = 120
    ds.NumberofSources = (1)
    ds.SourceIndex = (1)
    ds.ProjectionDataDefinitions = 'CT IMG ACQUISITION'
    ds.TypeofProjectionData = 'CIRCULAR'
    ds.TypeofProjectionGeometry = 'CONEBEAM'
    ds.PreprocessingFlagsModule = 'CT IMG ACQUISITION'
    ds.BeamHardeningCorrectionFlag = 'No'
    ds.GainCorrectionFlag = 'No'
    # Flat Field Correction is a private tag, we need to define its index and assing value
    ds.add_new(0x70391006, 'CS', '1')
    ds[0x70391006].value = 'No'
    ds.DarkFieldCorrectionFlag = 'NO'
    ds.BadPixelCorrectionFlag = 'NO'
    ds.ScatterCorrectionFlag = 'NO'
    ds.LogFlag = 'No'
    ds.LesionInformationModule = 'CT IMG ACQUISITION'
    
    ds.save_as(outputname)