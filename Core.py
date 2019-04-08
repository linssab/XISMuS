
import sys
import Mapping
import SpecRead
import ImgMath
from PyMca5.PyMcaPhysics import Elements
import matplotlib.pyplot as plt
import logging

def plot(image):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(image, vmin=0, vmax=255)
    fig.colorbar(cax)
    plt.show()
    return 0



if __name__=="__main__":
    inputlist = ['-findelement','Core.py','-normalize','-getratios'] 
    elementlist = []
    flag1 = sys.argv[1]
    if flag1 == '-help':
        print("\nUSAGE: '-findelement x y'; plots a 2D map of elements 'x' and/or 'y'\
additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displeyd in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    if flag1 == '-findelement':    
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in Elements.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
                    logging.exception("{0} is not a chemical element!".format(sys.argv[arg]))
            if '-normalize' in sys.argv:
                pass
        if '-normalize' in sys.argv:
            for element in elementlist:
                image = Mapping.getpeakmap(element)
                plot(image)
        else:
            for element in elementlist:
                image = Mapping.getpeakmap(element)
                plot(image)
        logging.exception("No element input!")
    
    if flag1 == '-plotmap':
        print("Fetching density map...")
        Mapping.plotdensitymap()
    if flag1 == '-plotstack':
        if len(sys.argv) >= 3:
            flag2 = sys.argv[2]
        else:
            flag2 = None
        SpecMath.getstackplot(SpecRead.getfirstfile(),SpecMath.energyaxis())
    if flag1 == '-getratios':
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in Elements.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
        ratiofile = SpecRead.workpath + '/output/ratio_{0}.txt'.format(elementlist[0])
        ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        ratiomatrix = SpecRead.RatioMatrixTransform(ratiomatrix)
        plt.imshow(ratiomatrix,cmap='gray')
        plt.show()
