import numpy as np
import os
import multiprocessing as mp
import memmap_extraction as me
import datetime
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
out_sample_file = '/nobackupp6/nexprojects/CMS-ALOS/maxent/swd/v6/afr/afr_train_v6.swd.csv'
out_background_file = '/nobackupp6/nexprojects/CMS-ALOS/maxent/swd/v6/afr/afr_background_0.002.swd.csv'

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

#print(train_samples.shape[0])
#print(train_samples.ndim)

#print(xcoord)
#print(ycoord)
#print(classname)

extract_cols = ((xcoord-ulmapx)/pixsize).astype(np.int32)
extract_rows = ((ulmapy-ycoord)/pixsize).astype(np.int32)

#----Create input list to run memmap_extraction in parallel using multiprocessing Pools
mmap_args = []
for i in range(nlayers):
	mmap_args.append((
	layer_dir+'/'+layer_files[i],
	layer_datatypes[i],
	i,
	xdim,
	ydim,
	extract_rows,
	extract_cols,
	extract_arrays))
	

def mp_worker(inFileName, data_type, list_index, in_dim_x, in_dim_y, extract_rows, extract_columns, extract_arrays):
	print('Extracting from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	out_vals = me.memmap_extraction(inFileName, data_type, in_dim_x, in_dim_y, extract_rows, extract_columns)
	#insert extracted values into list
	print(extract_arrays)	
	extract_arrays[list_index] = out_vals
	print(extract_arrays)	
	print('Finished extracting from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

#Spawn the threads and perform extraction
if __name__ == '__main__':
	print("Run mp_handler for extraction of samples.")
	p = mp.Pool(nlayers)
	extract_arrays = p.starmap(mp_worker, mmap_args)

#Write result to output file
#print("Writing output to ", out_sample_file)
#print(mmap_args)
writeswd.writeswd(out_sample_file, train_samples, layer_names, extract_arrays)



#Generate random background indices
extract_cols = np.random.choice(xdim,n_background_pts)
extract_rows = np.random.choice(ydim,n_background_pts)

#output array
background_arrays = []
for i in range(nlayers):
	extract_arrays.append(i)


#create input list
mmap_args = []
for i in range(nlayers):
	mmap_args.append((
	layer_dir+'/'+layer_files[i],
	layer_datatypes[i],
	i,
	xdim,
	ydim,
	extract_rows,
	extract_cols,
	extract_arrays))



def bg_mp_worker(inFileName, data_type, list_index, in_dim_x, in_dim_y, extract_rows, extract_columns,extract_arrays):
	print('Extracting background points from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	out_vals = me.memmap_extraction(inFileName, data_type, in_dim_x, in_dim_y, extract_rows, extract_columns)
	#insert extracted values into list
	extract_arrays[list_index] = out_vals
	print('Finished extracting background points from',inFileName,'...','Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))


#Spawn the threads and perform extraction
if __name__ == '__main__':
	#p = mp.Pool(nlayers)
	#extract_arrays = p.starmap(bg_mp_worker, mmap_args)
	print("Run bg_mp_handler")
