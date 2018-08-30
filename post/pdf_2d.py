
#Calculate local probability density 

#Probability density for each grid box is determined by the points located within a 5x5 grid centered around the grid box in question

#Parameters

#Parameters -
#
#       input parameters
#		input_file_name:  name of input training file for calculating prior probability
#		domain_def_file_name:  name of def text file that describes the domain of interest
#		min_points: minimum number of points required to calculate prior probability
#
#       output parameters
#       pdf - (n_cats by nx by ny array of unsigned long of number of points in each category)
#                   dimenions are n_cat by nx by ny so that retrieval from memory of pdf for a given x,y is fast
#       
#

import numpy as np
import numexpr
import os
import csv
import math

def pdf_2d(input_file_name, domain_def_file_name, min_points, pdf_out_def, pdf_out_file):

	print("Creating prior probability map...")

	#verify that input_file and domain definition files exist
	if not(os.path.isfile(input_file_name)):
		print("Error: Input File does not exist.")
		return False

	if not(os.path.isfile(domain_def_file_name)):
		print("Error: Domain definition file does not exist.")
		return False

	#--------------------------
	domaindict = {}
	#ingest domain definition file
	with open(domain_def_file_name, 'r') as domainfile:
		for line in domainfile:
			(key, val) = line.split()
			domaindict[key] = float(val)
	print("Domain definition:")
	print(domaindict)
	total_area = domaindict["xdim"] * domaindict["xpixwidth"] * domaindict["ydim"] * domaindict["ypixwidth"]

	print("Total domain area is: ", total_area)

	print("Reading input file...")

	#Ingest input file 
	imported_data = np.loadtxt(input_file_name, dtype={'names': ('xcoord', 'ycoord', 'agb', 'category') , 'formats': ('f4', 'f4', 'f4', 'i2') }, delimiter=',', skiprows=1, usecols=(1,2,3,4))

	total_input_points = len(imported_data)

	print("Total number of input points:", total_input_points)
	categories = imported_data['category']

	category_set = set(categories)
	n_categories = len(category_set)
	print("Number of categories: ", n_categories)
	print(category_set)

	print("Minimum number of points: ", min_points)
	points_per_area = float(total_input_points) / total_area

	min_area = min_points / points_per_area
	pdf_box_width = math.sqrt(min_area)
	min_pdf_xpix = math.ceil(pdf_box_width / domaindict["xpixwidth"])
	min_pdf_ypix = math.ceil(pdf_box_width / domaindict["ypixwidth"])
	output_xdim = math.ceil(domaindict["xdim"] / min_pdf_xpix)
	output_ydim = math.ceil(domaindict["ydim"] / min_pdf_ypix)

	print("Area to get min points per area: ", min_points / points_per_area)
	print("min pdf box x dimension: ", min_pdf_xpix)
	print("min pdf box y dimension: ", min_pdf_ypix)
	print("output pdf x-dimension: ", output_xdim)
	print("output pdf y-dimension: ", output_ydim)

	#Create output numpy array
	original_pdf_count = np.zeros([n_categories,output_ydim,output_xdim],dtype=np.uint32)
	#cycle through all input points
	tl_x_coord = domaindict["xmin"]
	tl_y_coord = domaindict["ymax"]
	
	for i in range(0,total_input_points):
	#for i in range(0,10):
		#print(imported_data['xcoord'][i], imported_data['ycoord'][i], tl_x_coord, domaindict["xpixwidth"])
		#print((imported_data['xcoord'][i]-tl_x_coord)/domaindict["xpixwidth"])
		xpix = int((imported_data['xcoord'][i]-tl_x_coord)/domaindict["xpixwidth"])
		ypix = int((tl_y_coord - imported_data['ycoord'][i])/domaindict["ypixwidth"])

		pdf_x = int(xpix/min_pdf_xpix)
		pdf_y = int(ypix/min_pdf_ypix)

		#print("xpix:", xpix, "ypix:", ypix, "pdf_x:", pdf_x, "pdf_y", pdf_y)
		original_pdf_count[categories[i],pdf_y,pdf_x] += 1

	#Create output pdf counts based on calculating from neighboring areas
	#Use a 11x11 box surrounding each pdf image pixel to get prior for that pixel
	out_pdf_count = np.zeros([n_categories,output_ydim,output_xdim],dtype=np.uint32)
	for j in range(0,output_ydim):
		for i in range(0,output_xdim):
			xindex_min = max(0,i-5)
			xindex_max = min(output_xdim-1,i+5)
			yindex_min = max(0,j-5)
			yindex_max = min(output_ydim-1,j+5)
			for i_cat in range(0,n_categories):
				out_pdf_count[i_cat,j,i] = np.sum(original_pdf_count[i_cat,yindex_min:yindex_max,xindex_min:xindex_max])
			
	
	#Write pdf count to output file
	with open(pdf_out_file, 'wb') as outfile:
		#out_pdf_count[10,:,:].tofile(outfile)	
		out_pdf_count.tofile(outfile)	

	#write pdf definition file
	with open(pdf_out_def, 'w') as outfile:
		outfile.write('xdim\t'+str(output_xdim)+'\n')
		outfile.write('ydim\t'+str(output_ydim))
