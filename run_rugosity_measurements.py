try:
    import numpy as np 
    import matplotlib.pyplot as plt
    from tqdm import tqdm
    import os
    import math
    import time
    from art import *
except:
    print("Error: Please install the required libraries")
    print("numpy, matplotlib, tqdm, os, math, time, art")
    print("This can be done by running \"pip install numpy matplotlib tqdm os art time math\"")
    exit()

try:
    from backend_code_files import convert_dem_to_npy as txt2npy
    from backend_code_files import calc_site_surface_complexity as calc_sc
    from backend_code_files import sample_rugosity as sample_rugosity
except Exception as e:
    print("Error: Could not find backend_code_files")
    print("Please make sure this folder is not missing!")
    print("Python Error: ", e)
    exit()

def intro():
    tprint("Rugosity  Calculator")
    print("------------------------------------------------------------------------------")
    print("| This program will present several methods to measure the rugosity of a DEM |")
    print("| Press \"Ctrl C\" to exit the program at any time                             |")
    print("| Author: Derek Benham, Dept. of Computer Engineering, BYU, 2022             |")
    print("------------------------------------------------------------------------------")
    print("\n")
'''
This function loads a DEM file. If it's a .txt file, it will convert it to a .npz file
for faster loading in the future (greater than 10x faster)
Inputs:
    None. It will prompt the user for a filepath
Outputs:
    dem: the DEM as a numpy array
    cell_size: the cell size of the DEM
    name: the name of the DEM
'''
def load_file():
    print("Before running any experiments, please load a file \n \
        An example would be \"\DEMS\\area1.txt\" \n \
                         or \"\DEMS\\area1.npz\" \n ")

    filepath = input("Filepath to the DEM: ")
    print("")
    try:
        if filepath.endswith(".txt"):
            print("Saving DEM as numpy file")
            print("This will allow for faster loading in the future")
            try:
                dem, cell_size = txt2npy.dem_txt_to_npy(filepath)
            except Exception as e:
                print("Error: Could not save numpy file. Maybe try doing this on a bigger computer?")
                print("Please try again \n")
                print("Error from Python: ", e)
                load_file()
        elif filepath.endswith(".npz"):
            data_npz = np.load(filepath)
            cell_size = data_npz['name1']
            dem = data_npz['name2']
        else:
            print("Error: File must be a .txt or .npz file")
            load_file()
    except Exception as e:
        print("File not found")
        print("Python Error: ", e)
        load_file()
    
    name = filepath.split("\\")[-1]
    name = filepath.split("\/")[-1]
    name = name.split(".")[0]
    print("")
    return dem, cell_size, name

'''
This function presents the user with the options menu
Outputs:
    choice: the user's choice
'''
def choose_option():
    choice = input("What would you like to do? \n \
    1) Plot DEM \n \
    2) Measure surface complexity over entire DEM \n \
    3) Measure random rugosity samples across entire DEM \n \
    4) Get more info about each choice \n \
    5) Tips and tricks \n \
    Q) Quit \n \
    Choice: ")
    print("")

    # 4) Measure specific rugosity points

    if choice == "4":
        print("1) Measure surface complexityrugosity of DEM\n \
        This will measure the entire 3D surface area by its 2D space of the DEM \n\
        Instead of a \'chain\' think of this as laying a carpet on the reef \n\
        This will take a while and return a single value \n")
        print("2) Measure random rugosity samples across entire DEM \n \
        This will measure the rugosity of random samples across the DEM \n \
        User can select number of samples, length and orientation of samples \n \
        Or can select a range of length and oreintation of samples that will be randomly selected\n")
        choose_option()

    if choice == "5":
        print("\nTips and tricks: \n \
        Make sure you have enough RAM to load the DEM.txt file, \n\
        you might need a bigger computer to convert it \n\n \
        Make sure to trim the DEM in Agisoft Metashape before computing\n \
        Around the edges of the DEM there will be a lot of error and it needs to be trimmed\n \
        This can be done by using the polygon tool in Agisoft\n")
        choose_option()
    
    return choice

'''
This function calculates the surface complexity of the entire DEM
It compares the 3D surface area to the 2D projection area
Inputs:
    dem: 2D numpy array of the DEM
    cell_size: the size of each cell in the DEM
    filename: the name of the DEM
Outputs:
    None
'''
def calc_surface_complexity(dem, cell_size, filename):
    print("This will measure the surface complexity over the entire DEM")
    print("This will take a while, please wait...")
    sc = calc_sc.calculate_site_surface_complexity(dem, cell_size)
    print("Surface complexity (3D/2D) of", filename, "is", sc)

    return

'''
This function calculates the rugosity of random samples across the entire DEM
It will prompt the user for various parameters and then calculate the rugosity
Inputs:
    dem: 2D numpy array of the DEM
    cell_size: the size of each cell in the DEM
    filename: the name of the DEM
Outputs:
    None
'''
def random_sample_rugosity(dem, cell_size, filename):
    sample_rugosity.sample_rugosity(dem, cell_size, filename)
    return

def quit_program():
    print("Exiting program...")
    print("Goodbye!")
    exit()

try:
    intro() # Print out the intro text
    dem, cell_size, filename = load_file()

    while True:
        option_choice = choose_option()

        if option_choice == "1":
            print("You'll need to close the plot to continue")
            plt.imshow(dem)
            plt.colorbar()
            plt.show()
        elif option_choice == "2":
            calc_surface_complexity(dem, cell_size, filename)
        elif option_choice == "3":
            random_sample_rugosity(dem, cell_size, filename)
        elif option_choice == "Q" or option_choice == "q":
            quit_program()
        else:
            print("Error: Invalid choice")
            print("Please try again")
        print("\n")
# If the user presses Ctrl + C, exit the program
except KeyboardInterrupt:
    quit_program()

except Exception as e:
    print("There was an error.")
    print("Error: ", e)
    quit_program()
