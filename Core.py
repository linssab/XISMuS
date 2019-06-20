<<<<<<< HEAD
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

if __name__=="__main__":
    import Compounds
    import numpy as np
    import sys, os
    import SpecRead
    import ImgMath
    from PyMca5.PyMcaPhysics import Elements
    import matplotlib.pyplot as plt
    import logging
    
    config = SpecRead.CONFIG

    inputlist = ['-findelement','Core.py','-normalize','-getratios','-dir']
    if '-dir' in sys.argv:
        params = config
        print(params)
        print(SpecRead.dirname)

    elementlist = []
    flag1 = sys.argv[1]
    if flag1 == '-help':
        print("\nUSAGE: '-findelement'; plots a 2D map of elements which are to be set.\
Additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displayed in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    if flag1 == '-findelement':    
        import Mapping
        input_elements = input('Please input which elements are to be mapped: \n')
        input_elements = input_elements.split(' ')
        for arg in range(len(input_elements)):
            if input_elements[arg] in Elements.ElementList:
                elementlist.append(input_elements[arg])
            else: 
                raise Exception("%s not an element!" % input_elements[arg])
                logging.exception("{0} is not a chemical element!".format(input_elements[arg]))
       
        cube_name = SpecRead.DIRECTORY
        print(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+'/'+cube_name+'.cube')
        if os.path.exists(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+'/'+cube_name+'.cube'):

            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,cube_name)
            else:
                Mapping.getpeakmap(elementlist,cube_name)
    
        else:
            
            #CREATES A DATACUBE 
            
            print("Compile is necessary.")
            specbatch = Mapping.datacube(['xrf'])
            specbatch.compile_cube()
            Mapping.pickle_cube(specbatch,cube_name)

            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,cube_name)
            else:
                Mapping.getpeakmap(elementlist,cube_name)
    
    if flag1 == '-plotstack':
        import SpecMath
        energyaxis = SpecMath.energyaxis()
        channels = np.arange(energyaxis.shape[0])
        SpecMath.getstackplot(SpecRead.getfirstfile(),energyaxis)
        SpecMath.getstackplot(SpecRead.getfirstfile(),channels)

    if flag1 == '-plotmap':
        import Mapping
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

=======
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

if __name__=="__main__":
    import Compounds
    import numpy as np
    import sys, os
    import SpecRead
    import ImgMath
    from PyMca5.PyMcaPhysics import Elements
    import matplotlib.pyplot as plt
    import logging
    
    config = SpecRead.CONFIG

    inputlist = ['-findelement','Core.py','-normalize','-getratios','-dir']
    if '-dir' in sys.argv:
        params = config
        print(params)
        print(SpecRead.dirname)

    elementlist = []
    flag1 = sys.argv[1]
    if flag1 == '-help':
        print("\nUSAGE: '-findelement'; plots a 2D map of elements which are to be set.\
Additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displayed in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    if flag1 == '-findelement':    
        import Mapping
        input_elements = input('Please input which elements are to be mapped: \n')
        input_elements = input_elements.split(' ')
        for arg in range(len(input_elements)):
            if input_elements[arg] in Elements.ElementList:
                elementlist.append(input_elements[arg])
            else: 
                raise Exception("%s not an element!" % input_elements[arg])
                logging.exception("{0} is not a chemical element!".format(input_elements[arg]))
       
        cube_name = SpecRead.DIRECTORY
        print(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+'/'+cube_name+'.cube')
        if os.path.exists(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+'/'+cube_name+'.cube'):

            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,cube_name)
            else:
                Mapping.getpeakmap(elementlist,cube_name)
    
        else:
            
            #CREATES A DATACUBE 
            
            print("Compile is necessary.")
            specbatch = Mapping.datacube(['xrf'])
            specbatch.compile_cube()
            Mapping.pickle_cube(specbatch,cube_name)

            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,cube_name)
            else:
                Mapping.getpeakmap(elementlist,cube_name)
    
    if flag1 == '-plotstack':
        import SpecMath
        energyaxis = SpecMath.energyaxis()
        channels = np.arange(energyaxis.shape[0])
        SpecMath.getstackplot(SpecRead.getfirstfile(),energyaxis)
        SpecMath.getstackplot(SpecRead.getfirstfile(),channels)

    if flag1 == '-plotmap':
        import Mapping
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

>>>>>>> 59697a6186041fdacbd0c987cf16c8b588250649
