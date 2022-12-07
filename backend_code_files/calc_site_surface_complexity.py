import numpy as np
from tqdm import tqdm

def calc_single_area(grid, cell_size):
    def calc_tri_area(a, b, c):
            # Calc line segments
        ab = np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)
        bc = np.sqrt((b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2)
        ac = np.sqrt((a[0]-c[0])**2 + (a[1]-c[1])**2 + (a[2]-c[2])**2)
        # Using Heron's formula
        s = (ab+bc+ac)/2
        area = np.sqrt(s*(s-ab)*(s-bc)*(s-ac))
        return area
    cs = cell_size
    # calc square area
    a1 = calc_tri_area((0, 0, grid[0][0]),
                       (0, cs, grid[0][1]), (cs, cs, grid[1][1]))
    a2 = calc_tri_area((0, 0, grid[0][0]),
                       (cs, 0, grid[1][0]), (cs, cs, grid[1][1]))
    return a1+a2


def calculate_site_surface_complexity(data, cell_size):
    area_3d = 0
    area_2d = 0
    
    print("Calculating Entire Site Surface Complexity")
    for i in tqdm(range(data.shape[0]-1)):
        for j in range(data.shape[1]-1):
            if (np.isnan(data[i, j]) or np.isnan(data[i+1, j]) or np.isnan(data[i, j+1]) or np.isnan(data[i+1, j+1])):
                continue
            else:
                grid = data[i:i+2, j:j+2]
                area_3d += calc_single_area(grid, cell_size)
                area_2d += cell_size**2
    return area_3d/area_2d
