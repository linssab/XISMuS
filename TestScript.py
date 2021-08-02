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
    import sys, os, inspect
    original_path = os.getcwd()
    a = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
    sys.path.insert(1, os.path.realpath(os.path.pardir))

    from Elements import Compounds
    from Elements import EnergyLib
    import numpy as np
    import pickle
    import logging
    import matplotlib.pyplot as plt
    from Engine import SpecRead
    from Engine import SpecMath
    from Engine import ImgMath
    os.chdir(a)
   
    elementlist = []
    inputlist = ['-findelement','Core.py','./Core.py','core.py','-normalize','-getratios','-stat','-threshold','-lowpass','-listsamples']
    commands = [" "]
    try: flag1 = sys.argv[1]
    except: 
        print("\nUsage:")
        for command in commands:
            print(command)
        flag1 = None
    if "-h" in sys.argv:
        print("-getratios [-n] datacube [-e] element [-t] mask-threshold [-m] matrix-ratio")
        print("-cubes [-n] datacube - CHAMA ESSA AQUI")
        sys.exit(0)
    
    if flag1 == '-help':
        print("\nUSAGE: '-findelement'; plots a 2D map of elements which are to be set.\
Additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displayed in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")

    if "-cubes" in sys.argv:
        from Engine import CubeEditor as ED
        import Constants

        ################
        # CHECKS INPUT #
        ################
        name = ""
        for arg in range(len(sys.argv)):
            if "-n" in sys.argv[arg] or "-name" in sys.argv[arg]:
                try: name = sys.argv[arg+1]
                except IndexError:
                    print("No name input after keyword!")
                    sys.exit(1)
        if name == "": raise Exception("No datacube input!")
        ################

        SpecRead.conditional_setup(name=name)
        cube_name = Constants.DIRECTORY
        cube_path = SpecRead.cube_path

        if os.path.exists(cube_path):
            print(f"Loading {cube_path} ...")
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print(f"Cube {cube_name} not found. Aborting...")
            sys.exit(1)
        
        original = datacube.densitymap
        out = ED.un_phase(datacube,1,datacube.dimension[1],1,5)
        fig, ax = plt.subplots(2,2)
        ax[0,0].imshow(original)
        ax[0,1].imshow(out)
        ax[0,0].set_title("Original")
        ax[0,1].set_title("Modified")
        plt.show()

        sys.exit(0)
    
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
            print(np.where(datacube.matrix == datacube.matrix.max()))
            
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
        _path = os.getcwd()+"\\output\\"
        cube_dict, maps = {}, {}
        import cv2
        sys.stdout.flush()
        """ list all packed cubes """
        cube_folders = [name for name in os.listdir(_path) \
                    if os.path.isdir(_path+name)]
        for folder in cube_folders:
            for name in os.listdir(_path+folder):
                if name.lower().endswith('.cube'): cube_dict[folder] = name
        print("Cubes compiled / Maximum counts:")
        for cube in cube_dict: 
            cube_file = open(_path+cube+"\\"+cube_dict[cube],'rb')
            datacube = pickle.load(cube_file)
            print("{}\t{}".format(cube, datacube.densitymap.max()))
            cube_file.close()
            maps[cube] = datacube.densitymap
        
        """ get the absolute maximum from all cubes
        this is applicable to SETS OF DATA that have a 
        relation between themselves, for example, when
        working with a larger sample that is composed of several
        datacubes """
        upper_limit = 0
        for image in maps:
            if upper_limit < maps[image].max() and maps[image].max() < 45000:
                # 45000 limit is to cutoff the error in FORNARINA data 1
                upper_limit = maps[image].max()
        
        for image in maps:
            norm_map = maps[image]/upper_limit*255
            cv2.imwrite(_path+"densemaps\\{}.png".format(image),norm_map)

        """        
        if os.path.exists(cube_path):
            
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            
            density_map = Mapping.getdensitymap(datacube)

            fig, ax = plt.subplots()
            mapimage = ax.imshow(density_map,cmap='jet',label='Dense Map')
            ax.set_title('Counts/pixel')
            ImgMath.colorbar(mapimage)
            plt.savefig(SpecRead.output_path+'\{0}_{1}_densitymap.png'.format(
            Constants.DIRECTORY,
            datacube.config.get('bgstrip')),dpi=150,transparent=False) 
            plt.show()
        else:
            print("Compile is necessary.")
            print("Please run 'python Core.py -compilecube' and try again.")
        """

    if flag1 == '-getratios':
        
        #######################################################################
        # Calculates the thickness of a given layer by using the attenuation  #
        # of the input element. The input element must be from the underlying #
        # layer. Ex.: '-getratios Pb' will calculate the thickness of the pre #
        # defined outer layer (reffered as compound) by using the Pb lines    #
        # attenuation                                                         #
        #######################################################################

        def second_smallest(numbers):
            m1, m2 = float("inf"), float("inf")
            for x in numbers:
                if x <= m1:
                    m1, m2 = x, m1
                elif x < m2:
                    m2 = x
            return m2
                
        ################
        # CHECKS INPUT #
        ################
        name = ""
        thickr = 0.0
        for arg in range(len(sys.argv)):
            if "-e" in sys.argv[arg]: 
                try: 
                    if sys.argv[arg+1] in EnergyLib.ElementList:
                        elementlist.append(sys.argv[arg+1])
                    else: raise Exception("%s not an element!" % sys.argv[arg+1])
                except IndexError:
                    print("No element input after keyword!")
                    sys.exit(1)
            if "-n" in sys.argv[arg] or "-name" in sys.argv[arg]:
                try: name = sys.argv[arg+1]
                except IndexError: 
                    print("No name input after keyword!")
                    sys.exit(1)
            if "-m" in sys.argv[arg]:
                try: thickr = float(sys.argv[arg+1])
                except IndexError:
                    print("No matrix ratio input after keyword!")
                except TypeError:
                    print("Wrong input type!")
            if "-t" in sys.argv[arg]:
                try: mask_threshold = int(sys.argv[arg+1])
                except IndexError:
                    print("No mask threshold input after keyword!")

        if name == "": raise Exception("No datacube input!")
        if sys.argv[-1].isdigit():
            z_lim = int(sys.argv[-1])
        else: z_lim = None

        import Constants
        SpecRead.conditional_setup(name=name)
        cube_name = Constants.DIRECTORY
        cube_path = SpecRead.cube_path

        try: 
            ratiofile = os.path.join(SpecRead.output_path,"{1}_ratio_{0}.txt".format(
                    elementlist[0],Constants.DIRECTORY))
            ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        except: raise FileNotFoundError(
                f"ratio file for {elementlist} not found in {SpecRead.output_path}")
        ################
        
        if os.path.exists(cube_path):
            print(f"Loading {cube_path} ...")
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            
            # manually set thickratio
            if thickr == "0":
                print("Using matrix ratio value euqal to 1.31.")
                datacube.config["thickratio"] = 1.31
            else:
                datacube.config["thickratio"] = thickr
            cube_file.close()
        else:
            print(f"Cube {cube_name} not found. Aborting...")
            sys.exit(1)
        
        ###################
        # DEFINE COMPOUND #
        ###################

        compound = Compounds.compound()
        compound.set_compound("FibulaGold")
        air = Compounds.compound()
        air.set_compound("Air")
        
        compound = compound.mix([12,88],[air])
        compound.set_attenuation(elementlist[0])
        compound.identity = 'Au'
        
        # used fot gildedwood sample
        """
        compound = Compounds.compound()
        compound.set_compound("Au24")
        compound.set_attenuation(elementlist[0])
        compound.identity = 'Au'
        """
        
        print("#"*5," Compound: ","#"*5)
        for key in compound.__dict__:
            print(key,compound.__dict__[key])
        print("#"*22)

        #############################
        # COMPOUND IDENTITY ELEMENT #
        #############################
        
        # abundance element method is deprecated
        # preference is given for the identy element from database. nonetheless,
        # if identity element does not exist (for custom or mixture compounds) abundance
        # element is used
        
        #---------------------------------------------
        # The LEVELS can vary according to input, so the ImgMath variable is used instead.
        # It is usually set to 255 unless changed in the code itself.
        # Threshold can, therefore, be any value from 0 to LEVELS.

        if mask_threshold == 0:  #NOTE: 116 #used for la fornarina gold
            print("No threshold mask input!")
        mask = ImgMath.mask(datacube,compound,mask_threshold)

        #---------------------------------------------

        print(f"Most abundant element in compound: {compound.identity}")
        #######################################
        
        """
        #custom_mask = np.zeros([datacube.dimension[0],datacube.dimension[1]])
        counter = 0

        #creates a ROI mask to calculate thickness values (fibula2 sample)
        for x in range(1,6):
            for y in range(26,34):
                custom_mask[x][y] = 1
                counter += 1
        for y in range(11,15):
            for x in range(30,34):
                custom_mask[y][x] = 1
                counter += 1
        for y in range(6,11):
            for x in range(4,11):
                custom_mask[y][x] = 1
                counter += 1

        #creates a ROI mask to calculate thickness values (gilded wood sample)
        for y in range(0,26):
            for x in range(34,65):
                custom_mask[y][x] = 1
                counter += 1
        for y in range(0,34):
            for x in range(74,82):
                custom_mask[y][x] = 1
                counter += 1
        """

        #####################################################################
        # plots the ratio map of element used as contrast and the mask used #
        #####################################################################

        try:
            if ratiomatrix.min() == 0:
                vmin = second_smallest(set(ratiomatrix.ravel()))
                print(f"This is the 2nd smallest value in Ratio Matrix (for plotting purposes): {vmin}")
            else: vmin = ratiomatrix.min()
            maps = []
            fig, ax = plt.subplots(1,2,sharey=True)
            maps.append(ax[0].imshow(ratiomatrix, vmax=ratiomatrix.max(), vmin=vmin))
            ax[0].set_title("{0} ratio map Matrix={1}".format(
                elementlist[0],datacube.config["thickratio"]))
            maps.append(ax[1].imshow(mask))
            ax[1].set_title('{} mask'.format(compound.identity))
            ImgMath.colorbar(maps[0])
            ImgMath.colorbar(maps[1])
            ax[0].axis("off")
            ax[1].axis("off")
            plt.show()
            plt.cla()
            plt.clf()
            plt.close()
        except: raise FileNotFoundError(f"{compound.identity} ratio file not found!")
        
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
                    datacube.config["thickratio"],compound)
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
        heightmap, average, std = ImgMath.getheightmap(
                ratiomatrix,
                mask,
                datacube.config["thickratio"],compound)
        fig, ax = plt.subplots()
        cbar = ax.imshow(heightmap,cmap='gray')
        ax.set_title("heightmap")
        ax.axis("off")
        ImgMath.colorbar(cbar)
        plt.show()
        plt.cla()
        plt.clf()
        plt.close()

        fig, ax = ImgMath.plot3D(heightmap,z_lim)
        ax.elev = 24
        def update_view(angle, angles, fig):
            #for angle in range(0, 360):
            ax.view_init(30, angle)
            #plt.draw()
            #plt.pause(.001)
            return fig,

        import matplotlib.animation as animation
        fig1 = plt.figure()
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800)
        angles = np.arange(0,360)
        line_ani = animation.FuncAnimation(fig, update_view, 360, fargs=(angles, fig),
                                   interval=360, blit=True)
        path = os.path.join(os.getcwd(),"animaiton.mp4")
        line_ani.save(path, writer=writer)
        print("Saved!")
        print(path)
        
