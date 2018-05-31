
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

def pdf_2d(input_file_name, domain_def_file_name, min_points, pdf_out_file):

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
	print("Number of categories: ", len(category_set))
	print(category_set)

	print("Minimum number of points: ", min_points)
	points_per_area = float(total_input_points) / total_area

	min_area = min_points * 10 / points_per_area
	pdf_box_width = math.sqrt(min_area)
	min_pdf_xpix = math.ceil(pdf_box_width / domaindict["xpixwidth"])
	min_pdf_ypix = math.ceil(pdf_box_width / domaindict["ypixwidth"])

	print("Area to get 10x min points per area: ", min_points * 10 / points_per_area)
	print("min pdf box x dimension: ", min_pdf_xpix)
	print("min pdf box y dimension: ", min_pdf_ypix)

