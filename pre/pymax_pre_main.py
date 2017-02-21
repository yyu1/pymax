import numpy as np
import os
import multiprocessing as mp
import memmap_extraction
import datetime
import random
import writeswd

#-----------Settings-----------------
#in_sample_file = '/nobackup/yyu1/samples/agb_train_v6/maxent_train_agb_v6_afr_train.csv'
in_sample_file = 'sample_train.csv'

layer_dir = '/nobackupp6/nexprojects/CMS-ALOS/maxent/layers/binary/afr'
layer_files = [
	'alos_2007_global_3sec_hh_cut_afr.int',
	'alos_2007_global_3sec_hv_cut_afr.int',
	'alos_2007_global_3sec_mask_cut_afr.byt',
	'global_srtm3_aster_dem_modgrid100m_afr.int',
	'global_srtm3_aster_stdev_modgrid100m_afr.int',
	'tm2015_nir_modgrid100m_afr.byt',
	'tm2015_swirb5_modgrid100m_afr.byt',
	'tm2015_swirb7_modgrid100m_afr.byt']
nlayers = len(layer_files)

xdim = np.uint64(108000)
ydim = np.uint64(96000)

ulmapx = np.float64(-3335805.2275283337)
ulmapy = np.float64(4447755.7471283330)
pixsize = np.float64(92.66254333332)

layer_datatypes = [np.int16, np.int16, np.uint8, np.int16, np.int16, np.uint8, np.uint8, np.uint8]

missings_vals = [-999, -999, 0, -999, 0, 0, 0]

n_background_pts = np.uint32(5000000)
out_sample_file = '/nobackupp6/nexprojects/CMS-ALOS/maxent/swd/v6/afr/afr_train_v6.swd'
out_background_file = '/nobackupp6/nexprojects/CMS-ALOS/maxent/swd/v6/afr/afr_background_0.002.swd'

#------------------------------------


#-------- Construct Layer Names
layer_names = []
for this_file in layer_files:
	layer_names.append(os.path.splitext(this_file)[0])


#-------Read input training sample file and convert coordinates to columns and rows
#NOTE: coordinates must be in the same units as those given in ulmapx, ulmapy, and pixsize.

train_samples = np.genfromtxt(in_sample_file, delimiter=',', skip_header=1,dtype=[('classname','S10'),('xcoord',np.float64),('ycoord',np.float64),('agb',np.float32),('category',np.int8)])
#train_samples = np.genfromtxt(in_sample_file, delimiter=',', skip_header=1)
xcoord = train_samples['xcoord']
ycoord = train_samples['ycoord']
classname = train_samples['classname']

print(train_samples.shape[0])
print(train_samples.ndim)

#print(xcoord)
#print(ycoord)
#print(classname)

extract_cols = ((xcoord-ulmapx)/pixsize).astype(np.int32)
extract_rows = ((ulmapy-ycoord)/pixsize).astype(np.int32)

#---create list to hold output of extraction
extract_arrays = []
for i in range(nlayers):
	extract_arrays.append(i)

#----Create input tuple of lists to run memmap_extraction in parallel using multiprocessing Pools
mmap_args = tuple(
	[layer_dir+'/'+layer_files[i],
	layer_datatypes[i],
	i,
	xdim,
	ydim,
	extract_rows,
	extract_cols,
	extract_arrays]
	for i in range(nlayers)
)

	

def mp_worker(inFileName, data_type, list_index, in_dim_x, in_dim_y, extract_rows, extract_columns, extract_arrays):
	print('Extracting from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	out_vals = memmap_extraction(inFileName, data_type, in_dim_x, in_dim_y, extract_rows, extract_columns)
	#insert extracted values into list
	extract_arrays[list_index] = out_vals
	print('Finished extracting from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

def mp_hander():
	p = mp.Pool(nlayers)
	p.map(mp_worker, mmap_args)


#Spawn the threads and perform extraction
if __name__ == '__main__':
#	mp_handler()
	print("Run mp_handler")

#Write result to output file
print("Writing output to ", out_sample_file)
writeswd.writeswd(out_sample_file, train_samples, layer_names, extract_arrays)




#Generate random background indices
extract_cols = random.choices(range(xdim),k=n_background_pts)
extract_rows = random.choices(range(ydim),k=n_background_pts)

#output array
background_arrays = []
for i in range(nlayers):
	extract_arrays.append(i)


#create input tuple
mmap_args = tuple(
	[layer_dir+'/'+layer_files[i],
	layer_datatypes[i],
	i,
	xdim,
	ydim,
	extract_rows,
	extract_cols]
	for i in range(nlayers)
)



def bg_mp_worker(inFileName, data_type, list_index, in_dim_x, in_dim_y, extract_rows, extract_columns,extract_arrays):
	print('Extracting background points from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	out_vals = memmap_extraction(inFileName, data_type, in_dim_x, in_dim_y, extract_rows, extract_columns)
	#insert extracted values into list
	extract_arrays[list_index] = out_vals
	print('Finished extracting background points from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

def bg_mp_hander():
	p = mp.Pool(nlayers)
	p.map(bg_mp_worker, mmap_args)


#Spawn the threads and perform extraction
if __name__ == '__main__':
#	bg_mp_handler()
	print("Run bg_mp_handler")
