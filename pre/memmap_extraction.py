import numpy as np

def memmap_extraction(inFileName, data_type, in_dim_x, in_dim_y, extract_rows, extract_columns):
	image_data = np.memmap(inFileName, dtype = data_type, mode = 'r', shape=(in_dim_y,in_dim_x))


	#check for out of bounds points
	xcond1 = (extract_columns >= 0)
	xcond2 = (extract_columns < in_dim_x)
	ycond1 = (extract_rows >= 0)
	ycond2 = (extract_rows < in_dim_y)

	xcond = np.logical_and(xcond1, xcond2)
	ycond = np.logical_and(ycond1, ycond2)

	inbound_mask = np.logical_and(xcond,ycond)

	out_val = np.empty_like(extract_rows, dtype=np.int16)
	out_val[:] = -1   #use -1 as missing value (out of bounds)

	out_val[inbound_mask] = image_data[extract_rows[inbound_mask], extract_columns[inbound_mask]]
	return out_val
