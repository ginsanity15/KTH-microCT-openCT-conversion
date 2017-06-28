#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 14:33:33 2017

@author: Bo Gao

The following is the utility script used to convert binary output data form the 
KTH-STH microCT to odl-compatible OpenCT data.

Input data:

Output data:

Requirements:
    pydicom (import dicom)
    ...
    
"""

import numpy as np
import odl
import odl_multigrid as multigrid
import pickle
import sys
sys.path.insert(0, '/Users/starbury/odl/STH-Multigrid-Reconstruction/functions')

import display_function as df
import sinogram_generation as sg

# %%
# Given the path that stores all those projection images in DICOM format, users 
# may need to modify this based on the directory they store the dataset
DICOM_path = '/Users/starbury/odl/STH-Multigrid-Reconstruction/Data'

# Directory for storing the .txt file that includes information of the reconstructed image 
output_store_path = '/home/davlars/Bo/real/Data_LC_512/TV/'

# Define the reconstruction space, these two points should be the opposite of each other
min_pt = [-20,-20,-1]
max_pt = [20, 20, 1]

# TODO: write a function to truncate projection image to include ROI only and 
# output the combined sinogram as well as one DICOM file (arbitrarily, we are 
# only interested in the identical information stored in header file)
sino, ds = sg.sino_gene(DICOM_path, min_pt, max_pt)

# These three numbers corresponds to the number of projection image as well as
# the size of each projection image
num, L1, L2 = sino.shape

# ODL only support reconstruction of projection data collected counter clockwise,
# read in information from projection image's header part, if the projection image
# is collected clockwise, convert its order to counter clockwise
rot_dir = ds.RotationDirection
if rot_dir == 'CW':
    sino_first = sino[0:1,:,:]
    sino_rest = sino[1:num,:,:]
    sino_rest = np.flipud(sino_rest)
    sino = np.concatenate([sino_first, sino_rest])

# Read out geometry information about the micro-CT scanner from the header of
# the DICOM file
src = ds.DistanceSourceToPatient
src = np.float(src)
det = ds.RadialPosition
det = np.float(det)

# Read in information on where each projeciton is collected 
initial = ds.StartAngle
initial = np.float(initial)
end = ds.ScanArc
end = np.float(end)

# Number of pixels along each row and column on projection image
length = ds.NumberofDetectorRows
length = np.int(length)
width = ds.NumberofDetectorColumns
width = np.int(width)

# Check is the detector has performed binning (e.g. combine intensity on four pixels
# and output as one) on the output projection 
Binning_scale = ds.DetectorBinning
Bin_scale = 1/float(Binning_scale[0])

# cell refers to the size of pixel on detector
cell = ds.DetectorElementTransverseSpacing/length * int(Bin_scale)
cell = np.float(cell)

# pixel_space refers to the size of pixel on reconstruction space
pixel_space = ds.ReconstructionPixelSpacing
pixel_space = np.float(pixel_space[0])

# Below sets the max number of pixels included in one direction on coarse grid
# This can be given arbitrarily, however, through testing, it is not recommend
# to set a value lower than 50, even when this number equals 50, an obvious
# difference on intensity can be observed at ROI and backgound
coarse_length = 200
coarse_length_x = np.int(coarse_length * max_pt[0]/max(max_pt))
coarse_length_y = np.int(coarse_length * max_pt[1]/max(max_pt))
coarse_length_z = np.int(coarse_length * max_pt[2]/max(max_pt))

# Define space to store background image and ROI
filename_c = output_store_path + 'FBP' + '_coarse_space_' + str(coarse_length) + '.txt'

# Define the reconstruction space (both coarse grid and fine grid) depends on the 
# setting give above
coarse_discr = odl.uniform_discr(min_pt, max_pt, [coarse_length_x, coarse_length_y, coarse_length_z])

# Define the detector
det_min_pt = -np.array([L1/2, L2/2])*cell
det_max_pt = -det_min_pt
detector_partition = odl.uniform_partition(det_min_pt, det_max_pt, [L1, L2])

# Define the angle that each projeciton image is collected
angle_partition = odl.uniform_partition(0, end - initial, num)

# Geometry of the projection (Parallel beam, Fan Flat beam or Cone Flat Beam)
geometry = odl.tomo.CircularConeFlatGeometry(angle_partition, detector_partition, 
                                             src, det)

# Define the forward operator of the masked coarse grid
coarse_ray_trafo = odl.tomo.RayTransform(coarse_discr, geometry,impl='astra_cuda')

# Make phantom in the product space
pspace = coarse_ray_trafo.domain

# Hann filter is used as it is the filter that is least sensitive to noise
# Frequency scaling is selected empirically    
fbp_coarse = odl.tomo.fbp_op(coarse_ray_trafo, filter_type = 'Hann', frequency_scaling = 0.1)
    
reco = coarse_ray_trafo.domain.zero()
data = coarse_ray_trafo.range.element(sino*1000)
    
# %% Reconstruction
reco = fbp_coarse(data)
reco.show()
# %% Storing the image
f = open(filename_c,'wb')
coarse_image = reco[0].asarray()
pickle.dump(coarse_image,f)