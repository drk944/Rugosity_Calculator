import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt
from tqdm import tqdm
import math
import time
import os
'''
Function to calculate what the height and width of the test site should be
This information is passed into "Find_valid_test_sites"
INPUTS:
    site_length_m: Length of the test site in meters
    angle_deg: Angle of the test site in degrees
'''
def calc_site_height_width(site_length_m, angle_deg):
    angle_deg = np.abs(90 - angle_deg)
    angle = (angle_deg) * np.pi/180 #(90 - )
    # FIXME: Might need to switch the sign
    if angle_deg < 45: 
        site_height = site_length_m + abs(site_length_m * np.sin(angle))/1.3
        site_width = site_length_m * np.cos(angle)
        site_width /= 1.1

    # elif angle_deg > 90 and angle_deg < 135:
    #     site_height = site_length_m * np.cos(angle)
    #     site_width = site_length_m + site_length_m * np.sin(angle) 
    else:
        site_height = site_length_m * np.sin(angle)
        site_width = site_length_m + abs(site_length_m * np.cos(angle))/1.3
        site_height /= 1.3
    return site_height, site_width


'''
Function to find valid test sites for the experiment
It needs to find a valid area that when testing will not go out of bounds
INPUTS:
    grid: The grid to find the test sites in
    site_hight_m: The height of the test site in meters
    site_width_m: The width of the test site in meters
    cell_size: The size of the grid cells in meters
    num_sites: The number of test sites to find
OUTPUTS:
    valid_sites: A list of valid test sites
'''
def find_valid_test_sites(grid, site_hight_m, site_width_m, cell_size, num_sites):
    seed = np.random.randint(0, 10000+1)
    # seed = 5 # DELETE ME
    rng = np.random.default_rng(seed)
    valid_sites = []
    height, width = grid.shape
    num_cells_w = int(site_width_m/cell_size)/2
    num_cells_h = int(site_hight_m/cell_size)/2
    num_iter = 0
    while len(valid_sites) < num_sites:
        num_iter += 1
        if num_iter % 10000 == 0:
            num_sites -= 1
            print("Decreasing number of sites to", num_sites)
        x = rng.integers(1, width)
        y = rng.integers(1, height)
        if np.isnan(grid[y][x]):
            continue
        if y-num_cells_h < 0 or y+num_cells_h > height or x-num_cells_w < 0 or x+num_cells_w > width:
            continue
        else:
            sub_grid = grid[int(y-num_cells_h):int(y+num_cells_h),
                            int(x-num_cells_w):int(x+num_cells_w)]
            if(np.isnan(sub_grid).any()):
                continue
            else:
                similar_site = False
                for site in valid_sites:
                    site_x = site[1]
                    site_y = site[0]
                    if site_x < x+num_cells_w*2 and site_x > x-num_cells_w*2 and  \
                            site_y < y+num_cells_h*2 and site_y > y-num_cells_h*2:
                        similar_site = True
                if similar_site == False:
                    valid_sites.append((y, x))
    return valid_sites

'''
Function to get which grid points the simulated chain will pass over
INPUTS:
    start: The starting point of the chain
    angle_deg: The angle of the chain in degrees
    length_cells: The length of the chain in grid cells
OUTPUTS:
    points: A list of the points the chain will pass over
    u_points: The unique points the chain will pass over
'''
def get_grid_points_rotation(start, angle_deg, length_cells):
    def removeDuplicates_list(mylist):
        # set that keeps track of what elements have been added
        seen = set()
        no_dups = []
        for lst in mylist:
            # convert to hashable type
            current = tuple(lst)
            # If element not in seen, add it to both
            if current not in seen:
                no_dups.append(lst)
                seen.add(current)
        # print(no_dups)
        return no_dups

    x = start[0]
    y = start[1]
    points = []
    points.append([x, y])
    u_points = []
    u_points_r = []

    angle = angle_deg * np.pi/180
    reverse_angle = angle + np.pi
    step_size = 0.33
    # First, go backwards
    while np.sqrt((x-start[0])**2+(y-start[1])**2) < length_cells/3:
        x += math.cos(reverse_angle)*step_size
        y += math.sin(reverse_angle)*step_size
        # Might need to re-implement this
        # if x >= grid_size-1 or y >= grid_size-1 or x < 0 or y < 0:
        #     break
        points.append([x, y])
        x_plot = int(round(x, 0))
        y_plot = int(round(y, 0))
        u_points_r.append([x_plot, y_plot])

    x = start[0]
    y = start[1]
    # Then, go forwards
    while np.sqrt((x-start[0])**2+(y-start[1])**2) < length_cells/2:
        x += math.cos(angle)*step_size
        y += math.sin(angle)*step_size
        # if x >= grid_size-1 or y >= grid_size-1:
        # break
        points.append([x, y])
        # u_points.add((x,y))
        x_plot = int(round(x, 0))
        y_plot = int(round(y, 0))
        u_points.append([x_plot, y_plot])
        # grid[x_plot, y_plot] = 1

    points = np.array(points)
    # u_point_list = removeDuplicates_list(u_points)
    u_points = removeDuplicates_list(u_points)
    u_points_r = removeDuplicates_list(u_points_r)
    u_points_r = np.flip(u_points_r, axis=0)
    u_points = np.array(u_points)
    u_points = np.concatenate((u_points_r, u_points), axis=0)
    # u_points = np.concatenate((u_points_r, u_points), axis=0)

    return points, u_points


'''
This function drops N chains on the grid and calculates the rugosity of each chain.
input:
    grid: 2D numpy array of elevations
    start_point: (y,x) tuple of the starting point of the chain
    length_cells: number of cells in the chain
    num_chains: number of chains to drop (defaulted to 1)
    start_angle: angle of the first chain
    max_angle: max angle between chains (unused)
    cell_size: size of each cell in meters
    chain_length_m: length of each chain in meters
    plotting: boolean to plot the chains
output:
    rugosities: list of rugosities of each chain
'''
def drop_chains_rotation(grid, start_point, length_cells, num_chains, start_angle, cell_size, chain_length_m, plotting):
    angle = start_angle
    rugosities = []
    for i in range(num_chains):
        _, u_points = get_grid_points_rotation(
            start_point, angle, length_cells)
        chain_start = u_points[0]
        chain_dist_calculated = 0
        total_real_world_distance = 0
        j = 0
        # Iterate until chain is correct length
        try:
            while chain_dist_calculated < chain_length_m:
                # Diff between neighboring cells
                elevation_change = grid[u_points[j, 0], u_points[j, 1]] \
                    - grid[u_points[j+1, 0], u_points[j+1, 1]]
                if np.isnan(elevation_change):
                    print("Nan elevation change at points:", u_points[j+1])
                    break

                # 2D distance between neighboring cells
                physical_dist = np.sqrt(
                    (u_points[j, 0]-u_points[j+1, 0])**2 + (u_points[j, 1]-u_points[j+1, 1])**2)
                physical_dist *= cell_size  # Convert to meters
                total_real_world_distance += physical_dist
                # Chain length traveled between 2 points
                chain_dist_calculated += np.sqrt(elevation_change **
                                                2 + physical_dist**2)
                j += 1
        except IndexError:
            pass
            # print("IndexError at:", u_points[j], "chain dist_calc:", chain_dist_calculated)
            
        # Calc real world distance between points
        real_world_dist = np.sqrt(
            (chain_start[0]-u_points[j, 0])**2 + (chain_start[1]-u_points[j, 1])**2)*cell_size
        # Add rugosity of line
        try:
            rugosities.append(chain_dist_calculated/total_real_world_distance) #real_world_dist)
        except ZeroDivisionError:
            continue

        if plotting:
            # This case is used for adjusting the case where a line is graphed too long
            # This occurs because of the new way I calculate the real world distance which accounts
            # for the manhattan distance instead of the euclidean distance
            if abs(real_world_dist - total_real_world_distance)/total_real_world_distance < 0.05:
                curr_avg = sum(rugosities)/len(rugosities)
                y, x = [chain_start[0], u_points[int(j/curr_avg), 0]], [
                    chain_start[1], u_points[int(j/curr_avg), 1]]
            else:
                y, x = [chain_start[0], u_points[j, 0]], [
                    chain_start[1], u_points[j, 1]]
            plt.plot(x, y, color='b')
            # plt.show(block=False) # Remove this line to plot all chains at once
            # plt.pause(0.01)
            # plt.show(block=False)
        # plot_grid(grid, points, u_points, grid_size)
    return rugosities

'''
This function takes in the User input from "sample_rugosity" and interfaces with 
the other functions to get the desired measurements
'''
def get_rugosity(grid, cell_size, site_length_m, orientation, plotting):
    length_cells = int(site_length_m/cell_size)

    site_height_m, site_width_m = calc_site_height_width(site_length_m, orientation)

    # print("Finding Valid Test Sites... (If program hangs, choose less sites or shorter lengths)")
    test_sites = find_valid_test_sites(grid, site_height_m, site_width_m, cell_size, 1)
    # print("Found", len(test_sites), "valid test sites")
    site_height_c = int(site_height_m/cell_size)
    site_width_c = int(site_width_m/cell_size)

    rugosities = drop_chains_rotation(
        grid, test_sites[0], length_cells, 1, orientation, cell_size, site_length_m, plotting)
    # print(np.mean(rugosities))
    # print(np.var(rugosities))
    # plt.plot(rugosities, color='b')

    # plt.show()
    # plt.pause(0.1)
    # plt.close()

    return rugosities[0]

'''
Function called from user side to get the Rugosity. It prompts the user for several setting
inputs to get the desired result. Can save results to a file.
input:
    dem: Digital Elevation Model
    cell_size: size of each cell in the DEM
    filename: name of the file to be saved
output:
    None
'''
def sample_rugosity(dem, cell_size, filename):
    random_length = False
    random_orientation = False
    num_samples = int(input("How many random samples would you like to measure? "))
    print("")
    # Getting chain length
    length = input("What length in meters would you like the virtual chains to be? Enter R for random\n \
    Length: ")
    print("")
    if length == "R" or length == "r":
        random_length = True
        min_length = int(input("What is the minimum chain length (m)?: "))
        max_length = int(input("What is the maximum chain length (m)?: "))
        print("You have chosen a random chain length between", min_length, "and", max_length, "meters.\n")
    else:
        length = int(length)
        print("You have chosen a chain length of", length, "meters\n")
    # Getting chain orientation
    orientation = input("What orientation would you like the virtual chains to be? \n\
    Enter a value between 0 and 179 degrees, R for random\n\
    Orientation is measured in degrees CCW from North \nOrientation: ")
    print("")
    if orientation == "R" or orientation == "r":
        random_orientation = True
        print("You have chosen a random chain orientation, chains will be randomly sampled from 0 to 179 degrees\n")
    
    else:
        orientation = int(orientation)
        print("You have chosen a chain orientation of", orientation, "degrees\n")

    # File output
    gen_file = False
    new_file_name = ""
    response = input("Would you like to save the results to a CSV? Y/N: ")
    print("")
    if response == "Y" or response == "y":
        gen_file = True
        print("You have chosen to save the results to a file. Results will be saved in the OUTPUT folder")
        new_file_name = input("What would you like to name the CSV?: ")
        print("")
        # check if new_file_name ends in .csv
        if new_file_name[-4:] != ".csv":
            new_file_name += ".csv"
        # put file in OUTPUT directory with OS independent path
        new_file_name = os.path.join("OUTPUT", new_file_name)
        print("The file will be saved as", new_file_name)
        confirm = input("Is this correct? Y/N: ")
        if confirm == "N" or confirm == "n":
            print("\n----------------------------------------\n")
            sample_rugosity(dem, cell_size, filename)

    else:
        print("You have chosen not to save the results to a file")
        print("Results will be printed to the console\n")

    plotting = False
    response = input("\nWould you like to plot the virtual chains? (Only works if you selected <100 samples)\n\
    Y/N: ")
    print("")
    if (response == "Y" or response == "y") and num_samples <= 100:
        plotting = True
        print("You have chosen to plot the virtual chains\n")
    
    # Getting rugosity
    rugosity_vals = []
    if plotting:
        plt.imshow(dem)
        plt.colorbar()
    
    for i in tqdm(range(num_samples)):
        if random_length or random_orientation:
            seed = np.random.randint(0, 10000+1)
            rng = np.random.default_rng(seed)
        if random_length:
            length = rng.integers(min_length, max_length)
        if random_orientation:
            orientation = rng.integers(0, 180)
        rugosity = get_rugosity(dem, cell_size, length, orientation, plotting)
        rugosity_vals.append(rugosity)
    
    rugosity_vals = np.array(rugosity_vals)
    site_mean = np.mean(rugosity_vals)
    print("\nAt site", filename, "the rugosity mean of", num_samples, "is", site_mean)
    if gen_file:
        np.savetxt(new_file_name, rugosity_vals, delimiter=",")
    else:
        print("\nValues:\n", rugosity_vals)

    if plotting:
        print("\nYou'll need to close the plot to continue")
        plt.show()
    
    return
