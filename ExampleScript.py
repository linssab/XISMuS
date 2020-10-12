#################################################################
#                                                               #
#          Template for custom scripts                          #
#                        version: 1.3.0 - Oct - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

if __name__.endswith('__main__'):         
    import sys
    try: mode = sys.argv[1]
    except: 
        mode = "-help"

    #############
    # HELP MODE #    
    #############
    if mode == "-help":
        print("\npython .\\ExampleScript.py [mode] [cube name] [agr1] [arg2] [arg3]")
        print("\nIn \"-multiply\" mode arg1, arg2 and arg3 are element1 element2 and color mode. If element1 == element2, the method will be applied in maps a and b of the element.\n")
        sys.exit(0)
    #############

    print("Starting up module...")
    print("Importing libraries...",end=" ")
    import SpecRead
    import SpecMath
    import ImgMath
    import Constants
    import os, copy
    import pickle
    import matplotlib.pyplot as plt
    import numpy as np
    print("Done.")
    print("Setting up environment...", end=" ")
    SpecRead.samples_folder = os.getcwd()
    SpecRead.conditional_setup()
    print("Done.")

    ###############
    # CUSTOM MODE #
    ###############
    if mode == "-mycommand":
        print("My command runs here.")
    ###############

    ########################
    # MULTIPLY IMAGES MODE # 
    ########################
    if mode == "-multiply":
        name = sys.argv[2]
        el1, el2 = sys.argv[3], sys.argv[4]
        try: 
            Constants.COLORMAP = sys.argv[5]
        except: 
            print("Using default {} color to save image.".format(Constants.COLORMAP))

        ####################################################################
        # THIS LOOP UNPICKLES THE DATACUBE INTO A SpecMath.Datacube OBJECT #
        ####################################################################
        print("Opening cube file...", end=" ")
        try:
            cube = os.path.join(
                    SpecRead.__PERSONAL__,"output",name,"{}.cube".format(name))
            cube_file = open(cube,'rb')
            CUBE = pickle.load(cube_file)
            cube_file.close()
        except:
            print("Failed to load cube. Exiting...")
            sys.exit(1)
        print("Done.")
        ####################################################################

        print("Loading {} and {} maps from cube {}".format(el1,el2,cube))
        if el1 == el2: 
            line1, line2 = "a","b"
        else: 
            line1, line2 = "a","a"
        try:
            map1 = CUBE.unpack_element(el1,line1)
            map2 = CUBE.unpack_element(el2,line2)
        except KeyError as exception:
            print(exception.__class__.__name__,": Failed to load map from cube.")
            sys.exit(1)
        image = map1*map2

        path_ = os.path.join(SpecRead.__PERSONAL__,"Transformed Images")
        try: 
            os.mkdir(path_)
        except OSError as exception:
            print(exception.__class__.__name__,": Transformed Images folder already exists!")
        image=ImgMath.write_image(image,1024,os.path.join(path_,name+".png"),save=False)
        plt.imsave(os.path.join(path_,name+".png"),image,cmap=Constants.COLORMAP)
        plt.imshow(image,cmap=Constants.COLORMAP)
        plt.show()
        print("Image saved at: ",path_)
        sys.exit(0)
    ########################
