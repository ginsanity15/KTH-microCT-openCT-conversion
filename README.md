# KTH-microCT-openCT-conversion
Repository to convert microCT raw output bin-data to openCT format, including correction for dark current, geometry misalignment, phase lag, and light field. 

## Requirements

The script rely on several python modules, paritculatrly 

```
os
glob
dicom
```

The ```dicom``` module can be most easily installed by ```easy_install pydicom```. Note that the conversion here intends to generate DICOM-CT-PD-format, instead of standard DICOM. For this, the default ```_dicom_dict.py``` dictionary in ```pydicom``` has to be replaced by the ```_dicom_dict.py``` file given in this repository. Generally, this file (to be replaced) can be found in ```/path/to/lib/python2.7/site-packages/pydicom-0.9.8-py2.7.egg/dicom/```.

For the reconstruction, the python library [```odl```](https://github.com/odlgroup/odl/) is also used. 


## Files

### functions/calibration.py
Utility file for calibrating microCT data, including
```
RemoveDeadPixel
GeometryCalibration
DarkFieldCalibration
LightFieldCalibration
LogCalibration
PhaseLagCalibration
```

Note that for ```GeometryCalibration```, ```pUP``` and ```pLEFT``` corresponds to calibration measurements in the form of ```dx``` and ```-dz```, respectively (see thesis by L. di Sopra). 

### functions/conversion.py
Utility for conversion of microCT data. Header information is hard coded and has to be adjusted to the settings of the microCT (e.g. ```NumberOfFramesInRotation```, ```DistanceSourceToDetector```, etc. all in lines 172-226). 

### example/DarkCurrentConversion.py
Conversion of acquired dark current images into dicom-format (```Dark_Field.dcm```). Needs input in the form of the directory where the DC images are located, and a template dicom file (given by default in this directory). 

### example/LightFieldConversion.py
Conversion of acquired light field images into dicom-format (```Light_Field.dcm```). Needs input in the form of the directory where the LF images are located, the converted dark current image, and a template dicom file (given by default in this directory).

### example/ConvertOneBin.py
Example conversion of one bin-file into openCT-dicom format. NOTE: This does not include correction from DC, LF, etc.

### example/ConvertMultipleBins.py
Example conversion of multiple bin-files into openCT-dicom format. NOTE: This does not include correction from DC, LF, etc.

### example/ConvertAndCalibrateBins.py
Conversion of microCT bin-files to openCT-dicom. This includes geometry alignment, DC correction, and phase lag. Requires input directories, template file, and dark current dicom.

### example/FBP_reconstruction.py
Simple example of coarse FBP reconstruction of generated dcm-data using [```odl```](https://github.com/odlgroup/odl/). 

## Usage
1) Make sure you have the correct ```_dicom_dict.py``` in the ```pydicom```-directory.
2) Run ```DarkCurrentCorrection.py``` to generate ```Dark_Field.dcm```
3) Run ```LightFieldCorrection.py``` to generate ```Light_Field.dcm```
4) Run ```ConvertAndCalibrateBins.py``` to convert and calibrate raw bin data
5) Reconstruct using e.g. ```FBP_reconstruction.py```



