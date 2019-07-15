#################################################################
#                                                               #
#          CORE 	                                        #
#                        version: null                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

def plot(image,color):
    image_color = ImgMath.colorize(image,color)
    fig, ax = plt.subplots()
    plt.imshow(image_color)
    plt.show()
    return 0

def convert_bytes(num):
    """
    Obtained from https://stackoverflow.com/questions/210408
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

if __name__=="__main__":
    import Compounds
    import numpy as np
    import sys, os, pickle
    import SpecRead
    import SpecMath
    import ImgMath
    import Mapping
    from PyMca5.PyMcaPhysics import Elements
    import matplotlib.pyplot as plt
    import logging
    
    config = SpecRead.CONFIG
    cube_path = SpecRead.cube_path
    elementlist = []
    flag1 = sys.argv[1]

    inputlist = ['-findelement','Core.py','-normalize','-getratios','-dir']
    if '-dir' in sys.argv:
        params = config
        print(params)
        print(SpecRead.dirname)
        if os.path.exists(cube_path):
            cube_stats = os.stat(cube_path)
            cube_size = convert_bytes(cube_stats.st_size)
            print("Datacube is compiled. Cube size: {0}".format(cube_size))
            print("Verifying packed elements...")
            import pickle
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close() 
            packed_elements = datacube.check_packed_elements()
            if len(packed_elements) == 0: print("None found.")
            print("Done.")
        else: print("Datacube not compiled. Please run -compilecube command.")

    if flag1 == '-help':
        print("\nUSAGE: '-findelement'; plots a 2D map of elements which are to be set.\
Additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displayed in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    
    if flag1 == '-compilecube':
        if os.path.exists(cube_path):
            print("Datacube is already compiled.")
        else:
            specbatch = SpecMath.datacube(['xrf'],config)
            specbatch.compile_cube()

    if flag1 == '-findelement':    
        input_elements = input('Please input which elements are to be mapped: \n')
        input_elements = input_elements.split(' ')
        for arg in range(len(input_elements)):
            if input_elements[arg] in Elements.ElementList:
                elementlist.append(input_elements[arg])
            else: 
                raise Exception("%s not an element!" % input_elements[arg])
                logging.exception("{0} is not a chemical element!".format(input_elements[arg]))
       
        print(cube_path)
        if os.path.exists(cube_path):
        
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close() 
            
            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,datacube)
            else:
                Mapping.getpeakmap(elementlist,datacube)
    
        else:
            print("Compile is necessary.")
            print("Please run 'python Core.py -compilecube' and try again.")

    if flag1 == '-plotstack':
        cube_name = SpecRead.DIRECTORY
        try: flag2 = sys.argv[2]
        except: flag2 = None
        try: flag3 = sys.argv[3]
        except: flag3 = None
        import SpecMath
        import pickle
        if os.path.exists(cube_path):
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            energyaxis = SpecMath.energyaxis()
            SpecMath.getstackplot(datacube,flag2,flag3)
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

    if flag1 == '-plotmap':
        import Mapping
        # FIX FOR RECEIVEING THE DATACUBE
        print("Fetching density map...")
        Mapping.getdensitymap()
    
    if flag1 == '-getratios':
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in Elements.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
        
        try: 
            ratiofile = SpecRead.workpath + '/output/{1}_ratio_{0}.txt'\
                .format(elementlist[0],SpecRead.DIRECTORY)
            ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        except: raise FileNotFoundError("ratio file for {0} not found.".format(elementlist))

        compound = Compounds.compound()
        compound.set_compound('PbWhite')
        compound.set_attenuation(elementlist[0])

        #######################################
        #  MOST ABUNDANT ELEMENT IN COMPOUND  #
        #######################################

        unpacked = []
        abundance = 0
        for key in compound.weight:
            unpacked.append(key)
            if compound.weight[key] > abundance: mae, abundance = key, compound.weight[key]

        print("Most abundant element in compound: {}".format(mae))
        
        #######################################

        try:
            maps = []
            mae_file = SpecRead.workpath + '/output/{1}_ratio_{0}.txt'\
                .format(mae,SpecRead.DIRECTORY)
            mae_matrix = SpecRead.RatioMatrixReadFile(mae_file)
            fig, ax = plt.subplots(1,2,sharey=True)
            maps.append(ax[0].imshow(ratiomatrix))
            ax[0].set_title('{} ratio map'.format(elementlist[0]))
            maps.append(ax[1].imshow(mae_matrix))
            ax[1].set_title('{} ratio map'.format(mae))
            ImgMath.colorbar(maps[0])
            ImgMath.colorbar(maps[1])
            plt.show()
            plt.cla()
            plt.clf()
            plt.close()
        except: raise FileNotFoundError("{0} ratio file not found!".format(mae))
        
        heightmap = ImgMath.getheightmap(ratiomatrix,mae_matrix,\
                config.get('thickratio'),compound)
        fig, ax = plt.subplots()
        cbar = ax.imshow(heightmap,cmap='gray')
        ax.set_title('heightmap')
        ImgMath.colorbar(cbar)
        plt.show()
        plt.cla()
        plt.clf()
        plt.close()
        ImgMath.plot3D(heightmap)

