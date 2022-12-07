import numpy as np 
import matplotlib.pyplot as plt 

def dem_txt_to_npy(filename):
    file_txt = filename
    filename = filename[:-4]
    
    with open(file_txt, 'r') as file:
        header = file.readlines()[0:6]

    ncols = int(header[0][13:-1])
    # nrows = int(file.readlines()[1][14:-1])
    cell_size = float(header[4][13:-1])    
    NODATA_value = float(header[5][13:-1])

    cell_size = np.array(cell_size)
    print("Cell size is", cell_size, "meters per side")
    data = np.genfromtxt(file_txt, skip_header=6, usecols=np.arange(0,ncols), invalid_raise = False)
    print("Loaded data")
    data[data == NODATA_value] = np.nan

    np.savez(filename, name1=cell_size, name2=data)
    plt.imshow(data)
    plt.show()
    print("Finished Loading")
    return data, cell_size

