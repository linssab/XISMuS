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
    import Mapping_NOGUI as Mapping
    import EnergyLib
    import matplotlib.pyplot as plt
    import logging
   
   # SpecRead.conditional_setup(name='politoc47')
    SpecRead.setup()
    config = SpecRead.CONFIG
    cube_name = SpecRead.DIRECTORY
    cube_path = SpecRead.cube_path
    elementlist = []
    inputlist = ['-findelement','Core.py','./Core.py','-normalize','-getratios','-stat','-threshold','-lowpass','-listsamples']
    commands = ['-findelement Ti Ca Fe ...', '-getratios Ti','-listsamples', '-stat\t /this print the current configuration embedded in config.cfg', '-threshold Ti (value from 0 4096)', '-lowpass Ti (value from 0 to 4096)','-compilecube','-plotmap','-plotstack -semilog -bg','ATTENTION: Ti, Ca and Fe are used as examples. In any case the input elements MUST be written according to their acronyms']
    try: flag1 = sys.argv[1]
    except: 
        print("\nUsage:")
        for command in commands:
            print(command)
        flag1 = None
    
    if flag1 == '-help':
        print("\nUSAGE: '-findelement'; plots a 2D map of elements which are to be set.\
Additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displayed in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    
    if '-stat' in sys.argv:
        sys.stdout.flush()
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
            if len(packed_elements) == 0: 
                print("None found.")
            else: 
                for element in packed_elements: print("Found a map for: "+element)
            print("Done.")
            #print("Configuration compiled into cube: {}".format(datacube.config))
            #print("Configuration from config.cfg: {}".format(config))
            print("Configuration embedded:\nKEY\t\tCUBE.CONFIG\tCONFIG.CFG")
            values_cube, values_cfg, values_keys = [],[],[]
            for key in datacube.config:
                values_cube.append(str(datacube.config[key]))
                values_cfg.append(str(config[key]))
                values_keys.append(str(key))
            for item in range(len(values_cube)):
                if len(values_cube[item]) <= 7: values_cube[item] = values_cube[item]+'\t'
                if len(values_cfg[item]) <= 7: values_cfg[item] = values_cfg[item]+'\t'
                if len(values_keys[item]) <= 7: values_keys[item] = values_keys[item]+'\t'
                print("{0}\t|{1}\t|{2}".format(values_keys[item],values_cube[item],values_cfg[item]))
            #print(values_cube,values_cfg,values_keys)
            
        else: 
            print("Datacube not compiled. Please run -compilecube command.")
            for key in config:
                if len(key) >= 8: print("{0}\t|{1}".format(key,config[key]))
                else: print("{0}\t\t|{1}".format(key,config[key]))

    if flag1 == '-compilecube':
        if os.path.exists(cube_path):
            print("Datacube is already compiled.")
        else:
            specbatch = SpecMath.datacube(['xrf'],config)
            specbatch.compile_cube()
    
    if flag1 == '-listsamples':
        print("FOLDER\t\t|MCA PREFIX")
        samples = [name for name in os.listdir(SpecRead.samples_folder) \
                if os.path.isdir(SpecRead.samples_folder+name)]
        samples_database = {}
        for folder in samples:
            if len(folder) >= 8: print("{0}\t".format(folder), end='|')
            else: print("{0}\t\t".format(folder), end='|')
            files = [name for name in os.listdir(SpecRead.samples_folder+folder)]
            for item in range(len(files)): 
                try:
                    files[item] = files[item].split("_",1)[0]
                except: pass
            counter = dict((x,files.count(x)) for x in files)
            mca_prefix_count = 0
            for counts in counter:
                if counter[counts] > mca_prefix_count:
                    mca_prefix = counts
                    mca_prefix_count = counter[counts]
            samples_database[folder] = mca_prefix
            print(mca_prefix)

    if flag1 == '-threshold':
        print(cube_path)
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        try: 
            element = sys.argv[2]
            if sys.argv[3].isdigit(): t = int(sys.argv[3])
            if element not in EnergyLib.ElementList:
                raise ValueError("{0} not an element!".format(element))
        except:
            raise ValueError("No threshold input.")
        
        element_matrix = datacube.unpack_element(element,"a") 
        element_matrix = ImgMath.threshold(element_matrix,t)
        
        fig, ax = plt.subplots()
        image = ax.imshow(element_matrix,cmap='gray')
        ImgMath.colorbar(image)
        ax.set_title("{0} map. Threshold {1}".format(element,t))
        plt.show()
    
    if flag1 == '-lowpass':
        
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        try: 
            element = sys.argv[2]
            if sys.argv[3].isdigit(): t = int(sys.argv[3])
            if element not in EnergyLib.ElementList:
                raise ValueError("{0} not an element!".format(element))
        except:
            raise ValueError("No threshold input.")
        element_matrix = datacube.unpack_element(element) 
        element_matrix = ImgMath.low_pass(element_matrix,t)
        
        fig, ax = plt.subplots()
        image = ax.imshow(element_matrix,cmap='gray')
        ImgMath.colorbar(image)
        ax.set_title("{0} map. Cutting signals above {1}".format(element,t))
        plt.show()

    if flag1 == '-smooth':

        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        try: 
            element = sys.argv[2]
            if sys.argv[3].isdigit(): t = int(sys.argv[3])
            if element not in EnergyLib.ElementList:
                raise ValueError("{0} not an element!".format(element))
        except:
            raise ValueError("No threshold input.")
        element_matrix = datacube.unpack_element(element) 
        element_matrix = ImgMath.iteractive_median(element_matrix,t)
        
        fig, ax = plt.subplots()
        image = ax.imshow(element_matrix,cmap='gray')
        ImgMath.colorbar(image)
        ax.set_title("{0} map. Cutting signals above {1}".format(element,t))
        plt.show()

    if flag1 == '-findelement':    
        input_elements = input('Please input which elements are to be mapped: \n')
        input_elements = input_elements.split(' ')
        for arg in range(len(input_elements)):
            if input_elements[arg] in EnergyLib.ElementList:
                elementlist.append(input_elements[arg])
            else: 
                raise Exception("%s not an element!" % input_elements[arg])
                logging.exception("{0} is not a chemical element!".format(input_elements[arg]))
       
        print("Loading {0}".format(cube_path))
        sys.stdout.flush()
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
        import SpecMath
        import pickle
        print("Loading {0}".format(cube_path))
        sys.stdout.flush()
        if os.path.exists(cube_path):
            
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            strip = SpecMath.peakstrip(datacube.sum,24,7)
            plt.semilogy(strip, label="strip")
            plt.semilogy(datacube.sum, label="sum")
            plt.legend()
            plt.show()
            #SpecMath.getstackplot(datacube,mode="combined")
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

    if flag1 == '-plotmap':
        print("Loading {0}".format(cube_path))
        sys.stdout.flush()
        if os.path.exists(cube_path):
            
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            
            density_map = Mapping.getdensitymap(datacube)

            fig, ax = plt.subplots()
            mapimage = ax.imshow(density_map,cmap='jet',label='Dense Map')
            ax.set_title('Counts/pixel')
            ImgMath.colorbar(mapimage)
            plt.savefig(SpecRead.output_path+'\{0}_{1}_densitymap.png'.format(SpecRead.DIRECTORY,\
                    datacube.config.get('bgstrip')),dpi=150,transparent=False) 
            plt.show()
        else:
            print("Compile is necessary.")
            print("Please run 'python Core.py -compilecube' and try again.")

    if flag1 == '-getratios':
        
        #######################################################################
        # Calculates the thickness of a given layer by using the attenuation  #
        # of the input element. The input element must be from the underlying #
        # layer. Ex.: '-getratios Pb' will calculate the thickness of the pre #
        # defined outer layer (reffered as compound) by using the Pb lines    #
        # attenuation                                                         #
        #######################################################################
        
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in EnergyLib.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
        
        try: 
            ratiofile = SpecRead.output_path + '{1}_ratio_{0}.txt'\
                    .format(elementlist[0],SpecRead.DIRECTORY)
            ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        except: raise FileNotFoundError("ratio file for {0} not found.".format(elementlist))
        
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))
        
        """
        compound = Compounds.compound()
        compound.set_compound([0.13,0.77,0.10],['S','O','Cu'],ctype='custom',mode='by_weight')
        compound.identity = 'S'
        compound.set_attenuation(elementlist[0])
        """
        
        compound = Compounds.compound()
        compound.set_compound("FibulaGold")
        air = Compounds.compound()
        air.set_compound("Air")
        
        # identity creates the mask to restrain the region where the heightmap will be calculated
        compound = compound.mix([12,88],[air])
        compound.set_attenuation(elementlist[0])
        compound.identity = 'Au'
        
        for key in compound.__dict__:
            print(key,compound.__dict__[key])

        #############################
        # COMPOUND IDENTITY ELEMENT #
        #############################
        
        # abundance element method is deprecated
        # preference is given for the identy element from database. nonetheless,
        # if identity element does not exist (for custom or mixture compounds) abundance
        # element is used
        
        mask_threshold = int(ImgMath.LEVELS/3)
        mask = ImgMath.mask(datacube,compound,mask_threshold)
        #mask = ImgMath.threshold(mask,0)
        mae = compound.identity

        print("Most abundant element in compound: {}".format(mae))
        #######################################
        
        custom_mask = np.zeros([datacube.dimension[0],datacube.dimension[1]])
        counter = 0
        
        #creates a ROI mask to calculate thickness values (fibula2 sample)
        for x in range(1,6):
            for y in range(26,34):
                custom_mask[x][y] = 1
                counter += 1
        for x in range(11,15):
            for y in range(30,34):
                custom_mask[x][y] = 1
                counter += 1
        for x in range(6,11):
            for y in range(4,11):
                custom_mask[x][y] = 1
                counter += 1
         
        #creates a ROI mask to calculate thickness values (gilded wood sample)
        """
        for x in range(0,26):
            for y in range(34,65):
                custom_mask[x][y] = 1
                counter += 1
        for x in range(0,34):
            for y in range(74,82):
                custom_mask[x][y] = 1
                counter += 1
        """

        mask = custom_mask
        #####################################################################
        # plots the ratio map of element used as contrast and the mask used #
        #####################################################################

        try:
            maps = []
            fig, ax = plt.subplots(1,2,sharey=True)
            maps.append(ax[0].imshow(ratiomatrix))
            ax[0].set_title('{0} ratio map Matrix={1}'.format(elementlist[0],config.get('thickratio')))
            maps.append(ax[1].imshow(mask))
            ax[1].set_title('{} mask'.format(compound.identity))
            ImgMath.colorbar(maps[0])
            ImgMath.colorbar(maps[1])
            plt.show()
            plt.cla()
            plt.clf()
            plt.close()
        except: raise FileNotFoundError("{0} ratio file not found!".format(mae))
        
        ####################################################################
       
        """
        maximum_porosity = 40
        x_axis = np.arange(0,maximum_porosity,1) 
        average = np.empty(maximum_porosity)
        average[:] = np.nan
        std = np.zeros([maximum_porosity])
        mask = custom_mask
        
        ansii_plot_file = open(os.getcwd()+"\\output\\{}\\".format(config.get('directory'))+"porosity_plot.txt","w+")
        ansii_plot_file.write("Air %\tMean\tStandard Deviation\n")
        for span in range(0,maximum_porosity,2):
            compound = Compounds.compound()
            compound.set_compound("FibulaGold")
            compound = compound.mix([span,100-span],[air])
            compound.set_attenuation(elementlist[0])
            heightmap,average[span],std[span] = ImgMath.getheightmap(ratiomatrix,mask,\
                    config.get('thickratio'),compound)
            ansii_plot_file.write("{}\t{}\t{}\n".format(span,average[span],std[span]))
        
        ansii_plot_file.close()
        print(counter)
        plt.subplot(111)
        plt.errorbar(x_axis,average,yerr=std,barsabove=True,capsize=3,fmt="P")
        plt.ylabel("Thickness (um)")
        plt.xlabel("Simulated porosity (%)")
        plt.show()
        """

        average,std = 0,0
        heightmap, average,std = ImgMath.getheightmap(ratiomatrix,mask,\
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

