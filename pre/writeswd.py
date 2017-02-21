#this program writes the swd file for maxent

import numpy as np

def writeswd(outFileName, trainSamples, imageNames, extractionValues)

	#validate input parameters
	if not(type(outFileName) is str):
		print("Error, outFileName is not type string.  Abort.")
		return

	if not(type(trainSamples) is np.ndarray):
		print("Error, trainSamples is not type numpy.ndarray. Abort.")
		return

	if not(type(extractionValues) is list):
		print('Error, extractionValues is not type list. Abort.')
		return

	if (trainSamples.ndim != 1):
		print("Error, dimension of trainSamples not correct. Abort.")
		return

	nsamples = 0
	for image in extractionValues:
		if not(type(image) is np.ndarray):
			print("Error, extractionValues type in list is not numpy.ndarray. Abort.")
			return
		if (nsamples == 0):
			nsamples = len(image)
		else:
			if (nsamples != len(image)):
				print('Error, extractionValues array length is not equal among images. Abort.')
				return

	if (trainSamples.shape[0] != nsamples):
		print('Error, trainSample size is not equal to extractionValue sample size. Abort.')
		return

	if (len(imageNames) != len(extractionValues)):
		print('Error, size of image names is not equal to size of extraction values.  Abort.')
		return

	#end of validation

	with open(outFileName, 'w') as output:
		#write header
		header = 'Class,X,Y,'
		header = header + ','.join(imageNames)
		output.write(header+'\n')

		xcoord = trainSamples['xcoord']
		ycoord = trainSamples['ycoord']
		classname = trainSamples['classname']

		#write extraction values
		for index in range(nsamples):
			outline = classname[index] + ',{:.2f},{:.2f}'.format(xcoord,ycoord)
			for image in extractionValues:
				outline = outline + ',' + str(image[index])
			outline = outline + '\n'
			output.write(outline)

	return

