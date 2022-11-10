import numpy as np
import math
import h5py
from PIL import Image, ImageOps
import glob, os, os.path, shutil
from os import listdir
from os.path import isfile, join
import plotly.express as px

def traverse_datasets(hdf_file):

    def h5py_dataset_iterator(g, prefix=''):
        for key in g.keys():
            item = g[key]
            path = f'{prefix}/{key}'
            if isinstance(item, h5py.Dataset): # test for dataset
                yield (path, item)
            elif isinstance(item, h5py.Group): # test for group (go down)
                yield from h5py_dataset_iterator(item, path)

    for path, _ in h5py_dataset_iterator(hdf_file):
        yield path
        
def percentage_diff(num1, num2):
    a = abs(num1-num2)
    b = (num1+num2) / 2
    c = (a/b) * 100
    return c

runagain = 1

while runagain == 1:

    datasetarray = []
    folderorfile = input("Do you want to run a folder or just one file (folder/file)\n")
    if folderorfile == "folder":
        path = input("Folder name?\n")
        for file in os.listdir(path):
            if file.endswith(".hdf5"):
                print(os.path.join(path,file))
                datasetarray.append(os.path.join(path,file))
    elif folderorfile == "file":
        filename = input("What is the name of the file? (include .hdf5)\n")
        datasetarray.append(filename)
    else:
        print("Invalid input")
        exit
                  
    ## -------------------------- Extract Images and Steering Data -----------------------
    for file in datasetarray:
        steeringdata = []
        i = 0
        foundImg = 0
        foundSteering = 0
        dict = {}
        if (os.path.isdir(file[:-5]) == False):
            os.mkdir(file[:-5])
        else:
            shutil.rmtree(file[:-5])
            os.mkdir(file[:-5])
        with h5py.File(file, 'r') as f:
            for dset in traverse_datasets(f):
                if f[dset].shape==(240, 320, 3):
                    j = np.array(f[dset][:])
                    array = np.reshape(j, (240, 320,3))
                    im = Image.fromarray(array)
                    im = ImageOps.flip(im)
                    file_name = str(i)
                    file_name = file_name.zfill(5)
                    file_name = file[:-5] + "/" + file_name + ".jpg"
                    im.save(file_name)
                    i = i+1
                    foundImg = 1
                if 'steering' in dset:
                    steeringdata.append(np.array(f[dset]))
                    dict[i-1] = np.array(f[dset])
                    foundSteering = 1
                if (foundImg == 1 and foundSteering == 1):
                    foundImg = 0
                    foundSteering = 0

                ## ----------------------------------- Find the Landmarks -----------------------------
                    
            values = np.array(steeringdata)
            initialvaluearray = np.where(np.logical_and(values>=(max(steeringdata) - (0.015*max(steeringdata))), values<=(max(steeringdata) + (0.015*max(steeringdata)))))[0]
            iz = np.where(values == min(steeringdata))[0]


            if ((max(steeringdata) - steeringdata[0]) - (steeringdata[0] - min(steeringdata))) > 0:
                if ((max(steeringdata) - steeringdata[0]) - (steeringdata[0] - min(steeringdata))) < 50:
                    initialvaluearray = np.concatenate((initialvaluearray,iz))
                else:
                    initialvaluearray = initialvaluearray
            elif ((max(steeringdata) - steeringdata[0]) - (steeringdata[0] - min(steeringdata))) < 0:
                if abs(((max(steeringdata) - steeringdata[0]) - (steeringdata[0] - min(steeringdata)))) < 50:
                    initialvaluearray = np.concatentate((initialvaluearray,iz))
                else:
                    initialvaluearray = iz

            landmarkarray = []
            landmarkarray.append(initialvaluearray[0])
            n = 0
            for increment1 in initialvaluearray:
                if n >= len(initialvaluearray)-1:
                    n = len(initialvaluearray)-1
                else:
                    n = n+1
                    
                if initialvaluearray[n] - increment1 != 1:
                    landmarkarray.append(increment1)
                    landmarkarray.append(initialvaluearray[n])
            landmarkarray.pop()

            if folderorfile == "folder":
                landmarkwindow = 15
            else:
                landmarkwindow = input("How many images previous to the landmark?\n")

            for v in landmarkarray:
                if landmarkarray.index(v) % 2 == 0:
                    landmarkarray[landmarkarray.index(v)] = v-3
                else:
                     landmarkarray[landmarkarray.index(v)] = v

                ## ------------------------------------ DEFAULTS ----------------------------------
            falsepos = False
            zz = []
            if folderorfile == "folder":
                defaults = 'y'
            else:
                defaults = input("all defaults? (y/n)\n")
                
            if defaults == 'y':
                window = 5
                floor = 100*math.floor(steeringdata[0]/100)
                ceil = 100*math.ceil(steeringdata[0]/100)
                tooclose = 10
                numimgs = 200
            else:
                window = input("How many frames around landmarks should the window be (d for default)(odd number)\n")
                if window == 'd':
                    window = 5
                floor = input("The current floor is " + str(100*math.floor(steeringdata[0]/100)) + ". press d to continue with this, otherwise input floor\n")
                if floor == 'd':
                    floor = 100*math.floor(steeringdata[0]/100)
                ceil = input("The current ceiling is " + str(100*math.ceil(steeringdata[0]/100)) + ". press d to continue with this, otherwise input ceiling\n")
                if ceil == 'd':
                    ceil = 100*math.ceil(steeringdata[0]/100)
                tooclose = input("two landmarks cannot be closer than x frames. x=? (d for default)\n")
                if tooclose == 'd':
                    tooclose = 10
                amtofimages = input("How many images in the negative folders? (default = 200, all, or input your own")
                if amtofimages == 'all':
                    numofimg = 'n'
                elif amtofimages == 'default':
                    numofimg = 200
                else:
                    numofimg = int(amtofimages)

            ## ----------------------------------- Removing False Positives -----------------------------
            for vi in landmarkarray:
                falsepos = False
                if math.isclose(percentage_diff(steeringdata[vi], steeringdata[vi+1]),percentage_diff(steeringdata[vi], steeringdata[vi+2]), abs_tol = 1):
                    if abs(percentage_diff(steeringdata[vi], steeringdata[vi+10]) - percentage_diff(steeringdata[vi], steeringdata[vi+1])) > 1.5:
                        if abs(percentage_diff(steeringdata[vi], steeringdata[vi+15])) > 10:
                            falsepos = False
                        elif abs(percentage_diff(steeringdata[vi], steeringdata[vi+20])) > 20:
                            falsepos = False
                        else:
                            falsepos = True
                    else:
                        falsepos = True
                if falsepos == True:
                    zz.append(landmarkarray.index(vi))                

            for vii in sorted(zz, reverse=True):
                del landmarkarray[vii]

            roc = []
            roc = landmarkarray.copy()
            
            for aaa in range(len(roc)):
                for bbb in range(1,int(window)+1):
                    roc.append(roc[aaa] - bbb)
                    roc.append(roc[aaa] + bbb)

            roc.sort()            
            ## ------------------- Ceiling and floor to move landmark closer to middle value -----------------------
            indexofroc = 0
            countldmrks = 0
            while(indexofroc!=len(roc)):
                landmark = landmarkarray[countldmrks]
                rocarray = []
                rocarrayframes = []
                changeldmrk = 0
                newldmrk = 0
                change = False
            
                for elem in range(0,(2*int(window))+1):
                    if elem != 2*(int(window))+1:
                        rocarrayframes.append(roc[elem + indexofroc])
                isCenter = False
                if countldmrks %2 == 0:
                    while(isCenter == False):
                        isCenter = False
                        for frames in rocarrayframes:
                            if (int(ceil) > steeringdata[frames] > int(floor)):
                                isCenter = True
                        if isCenter == False:
                            for frame in range(0,len(rocarrayframes)):
                                rocarrayframes[frame] = rocarrayframes[frame] - int(window)
                ## ----------------------------------- RATE OF CHANGE CORRECTION -----------------------------
                                
                for elem in range(0,len(rocarrayframes)):
                    if elem != len(rocarrayframes)-1:
                        rocarray.append(abs((steeringdata[rocarrayframes[elem+1]] - steeringdata[rocarrayframes[elem]]) / 2.0))

                maxindex = rocarrayframes[rocarray.index(max(rocarray))] + 1
                if rocarray.index(max(rocarray))+1 == 1:
                    rocarray = rocarray[::-1]
                    rocarrayframes = rocarrayframes[::-1]
                    maxindex = maxindex + 2
                fixldmrk = range(0,rocarray.index(max(rocarray))+1)
                fixldmrk = fixldmrk[::-1]
                for elements in fixldmrk:
                    if elements + 1 < rocarray.index(max(rocarray))+1:
                        if rocarray[elements] < rocarray[elements + 1] or rocarray[elements+1] >= 10:
                            changeldmrk = changeldmrk + 1
                            if elements - 1 >= 0:
                                if rocarray[elements] < 10 and rocarray[elements - 1] > 10:
                                    changeldmrk = changeldmrk + 1
                                if rocarray[elements] < 10 and rocarray[elements - 1] < 10:
                                    landmarkarray[countldmrks] = maxindex-changeldmrk
                                    change = True
                                    break
                            else:
                                if rocarray[elements] < 10:
                                    landmarkarray[countldmrks] = maxindex-changeldmrk
                                    change = True
                                    break

                if changeldmrk > 0 and change == False:
                    landmarkarray[countldmrks] = maxindex - changeldmrk
                    print("Warning: Landmark at frame " + str(landmarkarray[countldmrks]) + " is inaccurate, increase window!")
                                
                
                indexofroc = indexofroc+(2*(int(window)))+1
                countldmrks = countldmrks + 1

                ## ----------------------------------- CHECK IF LDMRKS ARE TOO CLOSE TOGETHER -------------------------------
            index1 = 0
            index2 = 1

            while index1 < len(landmarkarray):
                pair1 = landmarkarray[index1]
                if index2 >= len(landmarkarray):
                    pair2 = 0
                else:
                    pair2 = landmarkarray[index2]
                if pair2 != 0 and pair2 - pair1 < tooclose:
                    print("Warning: Landmark at " + str(pair1) + " is too close (within " + str(tooclose) + " frames) to landmark at " + str(pair2) + "! Deleting both...\n")
                    landmarkarray.pop(index2)
                    landmarkarray.pop(index1)

                if index2+1 < len(landmarkarray) and landmarkarray[index2+1] - pair2 < tooclose:
                    print("Warning: landmark pair ending at " + str(pair2) + " is too close to next landmark pair!\n")
                    
                index1 = index1 + 2
                index2 = index2 + 2
                
            for ldmarks in landmarkarray:
                if landmarkarray.index(ldmarks)-1 >= 0 and landmarkarray.index(ldmarks)-1 < len(landmarkarray):
                    zzz = landmarkarray[landmarkarray.index(ldmarks)-1]
                else:
                    zzz = 0
                if ldmarks - zzz < tooclose:
                    landmarkarray.pop(landmarkarray.index(ldmarks))
                    landmarkarray.pop(landmarkarray.index(zzz))


            ## ----------------------------------- DISPLAY FIGURE -----------------------------
                    
            figure = px.line(x=range(i), y = steeringdata)
            for y in landmarkarray:
                figure.add_vline(x = y, line_color = 'red')
                figure.add_vline(x = y - int(landmarkwindow), line_color = 'green')
            if folderorfile == 'file':
                figure.show()

            ## ----------------------------------- MANUALLY ADD/CHANGE/DEL LANDMARKS -----------------------------

            change = 0
            while (change != 'no' and folderorfile == "file"):
                change = input("Do you want to change/delete landmarks or add landmarks? (cd/a/no)\n")
                if change == 'no':
                    break
                elif change == 'cd':
                    for yy in landmarkarray:
                        zoomed = px.line(x = range(yy-int(landmarkwindow), yy+int(landmarkwindow)+1), y = [steeringdata[find] for find in range(yy-int(landmarkwindow), yy+int(landmarkwindow)+1)])
                        zoomed.add_vline(x = yy, line_color = 'red')
                        zoomed.update_xaxes(nticks=2*int(landmarkwindow))
                        zoomed.show()
                        action = input("What action would you like to take about this landmark? (n = N/A, d = del, c = change, exit)\n")
                        if action == 'n':
                            print("No change")
                        elif action == 'd':
                            landmarkarray.pop(landmarkarray.index(yy))
                            print(landmarkarray)
                        elif action == 'c':
                            landmarkarray[landmarkarray.index(yy)] = int(input("What is the correct landmark frame?\n"))
                            print(landmarkarray)
                        elif action == 'exit':
                            break
                elif change == 'a':
                    addldmrk = input("What landmark would you like to add?\n")
                    zoomed = px.line(x = range(addldmrk-int(landmarkwindow), addldmrk+int(landmarkwindow)+1), y = [steeringdata[find] for find in range(addldmrk-int(landmarkwindow), addldmrk+int(landmarkwindow)+1)])
                    zoomed.add_vline(x = addldmrk, line_color = 'red')
                    zoomed.update_xaxes(nticks=2*int(landmarkwindow))
                    zoomed.show()
                    addldmrk = input("What landmark would you like to add? (input frame of landmark again to confirm)\n")
                    landmarkarray.append(int(addldmrk))
                    landmarkarray.sort()
                    print("Added landmark at " + str(addldmrk) + "\n")


            finalfigure = px.line(x=range(i), y = steeringdata)
            for y in landmarkarray:
                finalfigure.add_vline(x = y, line_color = 'red')
                finalfigure.add_vline(x = y - int(landmarkwindow), line_color = 'green')

            landmarkimages = []
            vii = []
            landmarkarray[:] = [landmarkarray + 1 for landmarkarray in landmarkarray]
            landmarkimages[:] = [landmarkarray - int(landmarkwindow) for landmarkarray in landmarkarray]
            landmarkimages = landmarkarray + landmarkimages
            landmarkimages.sort()
            vii[:] = landmarkimages[:]
            landmarkimages[:] = [str(landmarkimages) for landmarkimages in landmarkimages]
            landmarkimages[:] = [landmarkimages.zfill(5) + ".jpg" for landmarkimages in landmarkimages]

        ## ----------------------------------- Moving Images into Folders -----------------------------

            folder_path = file[:-5]
            images = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
            landmarkimages.append(images[-1])
            
            counter = 0
            negpos_array = ['negative', 'positive']
            negpos = negpos_array[0]
            foldercounter = 0
            straightorno = False
            for image in images:
                if landmarkimages[counter] == image:
                    counter = counter + 1
                    if (counter % 2) == 0:
                        negpos = negpos_array[0]
                        if counter != len(landmarkimages):
                            foldercounter = foldercounter + 1
                    elif counter == len(landmarkimages):
                        negpos = negpos_array[0]
                    else:
                        negpos = negpos_array[1]
                        if straightorno == False:
                            straightorno = not straightorno
                            turndir1 = vii[counter]
                            turndir2 = vii[counter - 1]
                            turndir1 = turndir1 + 3
                            difference = steeringdata[turndir1] - steeringdata[turndir2]
                            if difference < 0:
                                negpos = "left"
                            elif difference > 0:
                                negpos = "right"
                        else:
                            negpos = "straight"
                            straightorno = not straightorno
                        

                folder_name = (str(foldercounter)).zfill(2) + "-" + negpos

                new_path = os.path.join(folder_path, folder_name)

                if not os.path.exists(new_path):
                    os.makedirs(new_path)

                old_image_path = os.path.join(folder_path, image)
                new_image_path = os.path.join(new_path, image)
                shutil.move(old_image_path, new_image_path)

            p = os.listdir(file[:-5])
            if len(p)%2 != 0:
                src = file[:-5] + '/' + p[len(p)-1] + '/'
                dest = file[:-5] + '/00-negative/'
                allfiles = os.listdir(src)
                for negimage in allfiles:
                    shutil.move(src+negimage, dest+negimage)
                os.rmdir(src)

            ## ----------------------------------- CERTAIN AMT OF IMAGES IN NEGATIVE FOLDERS -----------------------------

            if numimgs != 'n':
                for folders in os.listdir(file[:-5]):
                    if len(folders) > 8 and folders[-8:] == 'negative':
                        filepathdel = []
                        if len(os.listdir(file[:-5] + "/" + folders)) > numimgs:
                            x = len(os.listdir(file[:-5] + "/" + folders)) - numimgs
                            for deleting in range(0, x):
                                imgname = os.listdir(file[:-5] + "/" + folders)[deleting]
                                filepath = file[:-5] + "/" + folders + "/" + imgname
                                filepathdel.append(filepath)
                            for delete in filepathdel:
                                os.remove(delete)
            
            ## ----------------------------------- USED TO ANALYZE LANDMARKS LATER -----------------------------
            if (os.path.isdir(file[:-5] + "/Analysis") == False):
                os.mkdir(file[:-5] + "/Analysis")
            else:
                shutil.rmtree(file[:-5] + "/Analysis")
                os.mkdir(file[:-5] + "/Analysis")
                
            with open(file[:-5] + '/Analysis/landmarks.txt','w') as filehandle:
                for listitem in landmarkarray:
                    filehandle.write('%s\n' % listitem)
            with open(file[:-5] + '/Analysis/steeringdata.txt','w') as filehandles:
                for listitems in steeringdata:
                    filehandles.write('%s\n' % listitems)
            
            titletext = str("Final Graph: " + file[:-5])
            finalfigure.update_layout(title_text=titletext)
            finalfigure.write_html(file[:-5] + '/plot.html')
            finalfigure.write_json(file[:-5] + '/plot.json')
            

            
            if folderorfile == "folder":
                if file == datasetarray[-1]:
                    again = 0
                    print("Finished!")
                    break
                else:
                    print("Beginning next dataset... ")
            else:
                finalfigure.show()
                asdj = input("Run another dataset? (y/n)\n")
                if asdj == 'n':
                    runagain = 0



