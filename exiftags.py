
## ===========================================================================
##  NAME:       exiftags (from exif original script)
##  TYPE:       python script
##  CONTENT:    library for parsing EXIF headers
## ===========================================================================
##  AUTHORS:    rft     Robert F. Tobler
## ===========================================================================
##  HISTORY:
##
##  10-Aug-01 11:14:20  rft     last modification
##  09-Aug-01 16:51:05  rft     created
## ===========================================================================



## ---------------------------------------------------------------------------
##  'TAG_MAP'
##  	This is the map of tags that drives the parser.
## ---------------------------------------------------------------------------

from exif import *

TAG_MAP = {
	0x00fe: Tag('NewSubFileType'),
	0x00ff: Tag('SubFileType'),
	0x0100: Tag('ImageWidth'),
	0x0101: Tag('ImageLength'),
	0x0102: Tag('BitsPerSample'),
	0x0103: Tag('Compression'),
	0x0106: Tag('PhotometricInterpretation'),
	0x010a: Tag('FillOrder'),
	0x010d: Tag('DocumentName'),
	0x010e: Tag('ImageDescription'),
	0x010f: Tag('Make'),
	0x0110: Tag('Model'),
	0x0111: Tag('StripOffsets'),
	0x0112: Tag('Orientation', FormatMap({
					1:'top left side', 
					2:'top right side', 
					3:'bottom right side', 
					4:'bottom left side', 
					5:'left side top', 
					6:'right side top', 
					7:'right side bottom', 
					8:'left side bottom',
				   })),
	0x0115: Tag('SamplesPerPixel'),
	0x0116: Tag('RowsPerStrip'),
	0x0117: Tag('StripByteCounts'),
	0x011a: Tag('XResolution'),
	0x011b: Tag('YResolution'),
	0x011c: Tag('PlanarConfiguration'),
	0x0128: Tag('ResolutionUnit',
		FormatMap({
			1:	'Not Absoulute',
			2:	'Inch',
			3:	'Centimeter'
		})),
	0x012d: Tag('TransferFunction'),
	0x0131: Tag('Software'),
	0x0132: Tag('DateTime'),
	0x013b: Tag('Artist'),
	0x013e: Tag('WhitePoint'),
	0x013f: Tag('PrimaryChromaticities'),
	0x0142: Tag('TileWidth'),
	0x0143: Tag('TileLength'),
	0x0144: Tag('TileOffsets'),
	0x0145: Tag('TileByteCounts'),
	0x014a: Tag('SubIFDs'),
	0x0156: Tag('TransferRange'),
	0x015b: Tag('JPEGTables'),
	0x0201: Tag('JPEGInterchangeFormat'),
	0x0202: Tag('JPEGInterchangeFormatLength'),
	0x0211: Tag('YCbCrCoefficients'),
	0x0212: Tag('YCbCrSubSampling'),
	0x0213: Tag('YCbCrPositioning'),
	0x0214: Tag('ReferenceBlackWhite'),
	0x828d: Tag('CFARepeatPatternDim'),
	0x828e: Tag('CFAPattern'),
	0x828f: Tag('BatteryLevel'),
	0x8298: Tag('Copyright'),
	0x829a: Tag('ExposureTime', 	    	FormatRatioAsTime() ),
	0x829d: Tag('FNumber',	    	    	FormatRatioAsFloat() ),
	0x83bb: Tag('IPTC_NAA'),
	0x8773: Tag('InterColorProfile'),
	0x8822: Tag('ExposureProgram',
		    FormatMap({
			0:	'Unidentified',
			1:	'Manual',
			2:	'Program Normal',
			3:	'Aperture Priority',
			4:	'Shutter Priority',
			5:	'Program Creative',
			6:	'Program Action',
			7:	'Portrait Mode',
			8:	'Landscape Mode',
		    })),
	0x8824: Tag('SpectralSensitivity'),
	0x8825: Tag('GPSInfo'),
	0x8827: Tag('ISOSpeedRatings'),
	0x8828: Tag('OECF'),
	0x8829: Tag('Interlace'),
	0x882a: Tag('TimeZoneOffset'),
	0x882b: Tag('SelfTimerMode'),
	0x8769: Tag('ExifOffset'),
	0x9000: Tag('ExifVersion', FormatRatioAsString() ),
	0x9003: Tag('DateTimeOriginal'),
	0x9004: Tag('DateTimeDigitized'),
	0x9101: Tag('ComponentsConfiguration'),
	0x9102: Tag('CompressedBitsPerPixel'),
	0x9201: Tag('ShutterSpeedValue',	FormatRatioAsApexTime() ),
	0x9202: Tag('ApertureValue',   	    	FormatRatioAsFloat() ),
	0x9203: Tag('BrightnessValue'),
	0x9204: Tag('ExposureBiasValue',	FormatRatioAsBias() ),
	0x9205: Tag('MaxApertureValue',	    	FormatRatioAsFloat() ),
	0x9206: Tag('SubjectDistance'),
	0x9207: Tag('MeteringMode',
		FormatMap({
			0:  	'Unidentified',
			1:	'Average',
			2:	'CenterWeightedAverage',
			3:	'Spot',
			4:	'MultiSpot',
		},
    	    	make_ext = {
	    	    	'NIKON':    { 5: 'Matrix' },
    	    	})),
	0x9208: Tag('LightSource',
		FormatMap({
                        0:   'Unknown',
                        1:   'Daylight',
                        2:   'Fluorescent',
                        3:   'Tungsten',
                        10:  'Flash',
                        17:  'Standard light A',
                        18:  'Standard light B',
                        19:  'Standard light C',
                        20:  'D55',
                        21:  'D65',
                        22:  'D75',
                        255: 'Other'
		})),
	0x9209: Tag('Flash',
		FormatMap({
			0:	'no',
			1:	'fired',
			5:	'fired (?)', # no return sensed
			7:	'fired (!)', # return sensed
			9:	'fill fired',
			13:	'fill fired (?)',
			15:	'fill fired (!)',
			16:	'off',
			24:	'auto off',
			25:	'auto fired',
			29:	'auto fired (?)',
			31:	'auto fired (!)',
			32:	'not available'
		})),
	0x920a: Tag('FocalLength',  	    	FormatRatioAsFloat()),
	0x920b: Tag('FlashEnergy'),
	0x920c: Tag('SpatialFrequencyResponse'),
	0x920d: Tag('Noise'),
	0x920e: Tag('FocalPlaneXResolution'),
	0x920f: Tag('FocalPlaneYResolution'),
	0x9210: Tag('FocalPlaneResolutionUnit',
		FormatMap({
			1:  	'Inch',
			2:  	'Meter',
			3:  	'Centimeter',
			4:  	'Millimeter',
			5:  	'Micrometer',
		})),
	0x9211: Tag('ImageNumber'),
	0x9212: Tag('SecurityClassification'),
	0x9213: Tag('ImageHistory'),
	0x9214: Tag('SubjectLocation'),
	0x9215: Tag('ExposureIndex'),
	0x9216: Tag('TIFF_EPStandardID'),
	0x9217: Tag('SensingMethod'),
	0x927c: Tag('MakerNote'),
	0x9286:	Tag('UserComment',FormatRatioAsString()),
	0x9290:	Tag('SubSecTime'),
	0x9291:	Tag('SubSecTimeOriginal'),
	0x9292:	Tag('SubSecTimeDigitized'),
	0xA000:	Tag('FlashPixVersion', FormatRatioAsString()),
	0xa001: Tag('ColorSpace'),
	0xa002: Tag('ExifImageWidth'),
	0xa003: Tag('ExifImageHeight'),
	0xa005: Tag('Interoperability_IFD_Pointer'),
    	0xA20B:	Tag('FlashEnergy'),			# 0x920B in TIFF/EP
	0xA20C:	Tag('SpatialFrequencyResponse'),	# 0x920C    -  -
	0xA20E:	Tag('FocalPlaneXResolution'),	# 0x920E    -  -
	0xA20F:	Tag('FocalPlaneYResolution'),	# 0x920F    -  -
	0xA210:	Tag('FocalPlaneResolutionUnit',
                FormatMap({
                        1:      'Inch',
                        2:      'Meter',
                        3:      'Centimeter',
                        4:      'Millimeter',
                        5:      'Micrometer',
                })),	
	0xA214:	Tag('SubjectLocation'),		# 0x9214    -  -
	0xA215:	Tag('ExposureIndex'),		# 0x9215    -  -
	0xA217:	Tag('SensingMethod'),		# 0x9217    -  -
	0xA300:	Tag('FileSource', FormatMap({0x03:'Digital Still Camera'})),
	0xA301:	Tag('SceneType'),
	0xA302: Tag('CFAPattern'),
}

## ---------------------------------------------------------------------------
##  The EXIF parser is completely table driven.
## ---------------------------------------------------------------------------

CANON_IXUS_MAKERNOTE_TAG_MAP = {
	0x0000: Tag(None),
	0x0001: Tag(None, FormatTable({
			0x0001: Tag( 'MacroMode', FormatMap({1:'macro',2:'normal'}) ),
			0x0004: Tag( 'FlashMode', FormatMap({0:'flash not fired',1:'auto',2:'on',3:'red-eye reduction',4:'slow syncro',5:'auto + red-eye reduction', 16:'external flash'})  ),
			0x0005: Tag( 'ContinuousDriveMode', FormatMap({0:'single or timer',1:'continuous'})),
			0x0007: Tag( 'FocusMode', FormatMap({0:'One-Shot',1:'AI Servo',2:'AI Focus',3:'MF',4:'Single',5:'Continuous'})),
			0x000A: Tag( 'Image Size', FormatMap({0:'large',1:'medium',2:'small'})),
			0x000B: Tag( 'EasyShootingMode', FormatMap({0: 'Full Auto',1: 'Manual', 2: 'Landscape', 3: 'Fast Shutter', 4: 'Slow Shutter', 5: 'Night',6: 'B&W', 7: 'Sepia', 8: 'Portrait', 9: 'Sports', 10: 'Macro / Close-Up', 11: 'Pan Focus',})),
			0x000D: Tag( 'Contrast', FormatMap({0xFFFF:'low',1:'high',0:'normal'})),
			0x000E: Tag( 'Saturation', FormatMap({0xFFFF:'low',1:'high',0:'normal'})),
			0x000F: Tag( 'Sharpness', FormatMap({0xFFFF:'low',1:'high',0:'normal'})),
#			0x0010: Tag( 'ISO', FormatMap({15:'auto',16:'50',17:'100',18:'200',19:'400'})),
			17:	Tag( 'MeteringMode', FormatMap({3: 'Evaluative', 4: 'Partial', 5: 'Center-weighted'})),
			19:	Tag( 'AFPoint', FormatMap({0x3000: 'none (MF)', 0x3001: 'auto-selected', 0x3002: 'right', 0x3003: 'center', 0x3004: 'left'})),
			20: 	Tag( 'Exposure mode', FormatMap({0: 'Easy shooting', 1: 'Program',2: 'Tv-priority',3: 'Av-priority',4: 'Manual',5: 'A-DEP',})),
			23:	Tag( 'LongFocalLength' ),
			24:	Tag( 'ShortFocalLength' ),
			25:     Tag( 'FocalUnits' ),
			29:	Tag( 'FlashDetails', FormatMap({8192: 'Internal Flash', 4: 'FP sync enabled'}) ),
		})),
	0x0002: Tag(None),
	0x0003: Tag(None),
	0x0004: Tag(None, FormatTable({
		7: Tag( 'WhiteBalance', FormatMap({0: 'Auto',1: 'Sunny',2: 'Cloudy',3: 'Tungsten',4: 'Flourescent',5: 'Flash',6: 'Custom', })),
		15:Tag( 'FlashBias', FormatMap({ 0xffc0: '-2 EV', 0xffcc: '-1.67 EV',0xffd0: '-1.50 EV',0xffd4: '-1.33 EV',0xffe0: '-1 EV',0xffec: '-0.67 EV',0xfff0: '-0.50 EV',0xfff4: '-0.33 EV',0x0000: '0 EV',0x000c: '0.33 EV',0x0010: '0.50 EV',0x0014: '0.67 EV',0x0020: '1 EV', 0x002c: '1.33 EV',0x0030: '1.50 EV',0x0034: '1.67 EV',0x0040: '2 EV', })),
		19:Tag( 'SubjectDistance' ), 
	})),
	0x0006: Tag('ImageType'),
	0x0007: Tag('FirmwareVersion'),
	0x0008: Tag('ImageNumber'),
	0x0009: Tag('OwnerName'),
	0x000C: Tag('CamerSerial'),
	0x000D: Tag(None),
	0x000F: Tag('CustomFunctions'),
	0x0010: Tag(None),
}

OLYMPUS_MAKERNOTE_TAG_MAP = {
	0x0200: Tag('SpecialMode'),
	0x0201: Tag('JpegQual'),
	0x0202: Tag('Macro'),
	0x0207: Tag('SoftwareRelease'),
	0x0208: Tag('PictInfo'),
	0x0209: Tag('CameraID'),
	0x0F00: Tag('DataDump'),
}

	


## ---------------------------------------------------------------------------
##  Nikon 99x MakerNote Tags http://members.tripod.com/~tawba/990exif.htm
## ---------------------------------------------------------------------------
NIKON_99x_MAKERNOTE_TAG_MAP = {
	0x0001:	Tag('MN_0x0001'),
	0x0002:	Tag('MN_ISOSetting'),
	0x0003:	Tag('MN_ColorMode'),
	0x0004:	Tag('MN_Quality'),
	0x0005:	Tag('MN_Whitebalance'),
	0x0006:	Tag('MN_ImageSharpening'),
	0x0007:	Tag('MN_FocusMode'),
	0x0008:	Tag('MN_FlashSetting'),
	0x000A:	Tag('MN_0x000A'),
	0x000F:	Tag('MN_ISOSelection'),
	0x0080:	Tag('MN_ImageAdjustment'),
	0x0082:	Tag('MN_AuxiliaryLens'),
	0x0085:	Tag('MN_ManualFocusDistance',  	FormatRatioAsFloat() ),
	0x0086:	Tag('MN_DigitalZoomFactor',    	FormatRatioAsFloat() ),
	0x0088:	Tag('MN_AFFocusPosition',
		FormatMap({
			'\00\00\00\00': 'Center',
			'\00\01\00\00': 'Top',
			'\00\02\00\00': 'Bottom',
			'\00\03\00\00': 'Left',
			'\00\04\00\00': 'Right',
		})),
	0x008f:	Tag('MN_0x008f'),
	0x0094:	Tag('MN_Saturation',
		FormatMap({
			0: '0',
			1: '1',
			2: '2',
			-3: 'B&W',
			-2: '-2',
			-1: '-1',
		})),
	0x0095:	Tag('MN_NoiseReduction'),
	0x0010:	Tag('MN_DataDump'),
	0x0011:	Tag('MN_0x0011'),
	0x0e00:	Tag('MN_0x0e00'),
}


# FIXME, NIKON_D1H_MAKERNOTE_TAG_MAP is a copy of NIKON_99x_MAKERNOTE_TAG_MAP.
# Although it's been adjusted by analogy and analysis published in the web,
# some tags may be not accurate, as they weren't tested having the camera in front.

NIKON_D1H_MAKERNOTE_TAG_MAP = {    
	0x0001:	Tag('MN_FamilyID'),
	0x0002:	Tag('MN_ISOSetting'),
	0x0003:	Tag('MN_ColorMode'),
	0x0004:	Tag('MN_Quality'),
	0x0005:	Tag('MN_Whitebalance'),
	0x0006:	Tag('MN_ImageSharpening'),
	0x0007:	Tag('MN_FocusMode'),
	0x0008:	Tag('MN_FlashSetting'),
	0x000A:	Tag('MN_0x000A'),
	0x000F:	Tag('MN_ISOSelection'),
    0x0081:	Tag('MN_ImageAdjustment'),
	0x0082:	Tag('MN_AuxiliaryLens'),
    0x0084:	Tag('MN_LensInformation',  	FormatRatioAsFloat() ),
	0x0085:	Tag('MN_ManualFocusDistance',  	FormatRatioAsFloat() ),
	0x0086:	Tag('MN_DigitalZoomFactor',    	FormatRatioAsFloat() ),
	0x0088:	Tag('MN_AFFocusPosition',
		FormatMap({
			'\00\00\00\00': 'Center',
			'\00\01\00\00': 'Top',
			'\00\02\00\00': 'Bottom',
			'\00\03\00\00': 'Left',
			'\00\04\00\00': 'Right',
		})),
	0x008f:	Tag('MN_0x008f'),
	0x0094:	Tag('MN_Saturation',
		FormatMap({
			0: '0',
			1: '1',
			2: '2',
			-3: 'B&W',
			-2: '-2',
			-1: '-1',
		})),
	0x0095:	Tag('MN_NoiseReduction'),
	0x0010:	Tag('MN_DataDump'),
	0x0011:	Tag('MN_0x0011'),
	0x0e00:	Tag('MN_0x0e00'),
}
