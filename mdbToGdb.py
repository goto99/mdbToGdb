# -*- coding: utf-8 -*-
import arcpy
import os
import re

# Set input and output directories here
outws = r'E:\DLG\gdb1'
inws = r'E:\DLG\mdb1'
pattern_mdb = re.compile(".mdb$")
pattern_gdb = re.compile(".gdb$")

# helper functions
def locate_file(pattern, root= "."):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.
    
    Modified based on http://code.activestate.com/recipes/499305-locating-files-throughout-a-directory-tree/
    '''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for file in files:
            if re.search(pattern, file):
                yield os.path.join(path, file)
                
def locate_dir(pattern, root= "."):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.
    
    Modified based on http://code.activestate.com/recipes/499305-locating-files-throughout-a-directory-tree/
    '''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for d in dirs:
            if re.search(pattern, d):
                yield os.path.join(path, d)


mdbs = [] # store all mdb files' absolut path.
for m in locate_file(pattern_mdb, root=inws):
    mdbs.append(m)

# The following codes from https://gis.stackexchange.com/questions/156708/copying-feature-classes-from-personal-geodatabase-to-file-geodatabase-using-arcp
count = 0
for m in mdbs:
    # Define output FGDB name
    fgdb_name = os.path.basename(m).split(".")[0] + ".gdb"
    # print("New file geodatabase:", fgdb_name)

    # Create a new FGDB, make sure this file geodatabase dosn't exist when running this script.
    arcpy.CreateFileGDB_management(outws, fgdb_name)

    # Copy any FCs that are directly in personal geodatabase, without a dataset in between.
    arcpy.env.workspace = os.path.join(inws, m)
    #print("Workspace directly in personal geodatabase: ", arcpy.env.workspace)
    
    fcs = arcpy.ListFeatureClasses()
    for fc in fcs:
        arcpy.CopyFeatures_management(fc, os.path.join(outws, fgdb_name, fc))
        # print("Feature class directly in personal geodatabase: ", fc)

    # Report on processing status
    print "%s of %s personal databases converted to FGDB" % (count, len(mdbs))
    count += 1

    # List the feature dataset, directly in personal geodatabase
    arcpy.env.workspace = os.path.join(inws, m)
    fds = arcpy.ListDatasets()
    for f in fds:
        # print("Dataset: ", f)
        # Reset the working space to personal geodatabase, which maybe changed to last dataset in last loop.
        arcpy.env.workspace = os.path.join(inws, m) 
        # Determine FDS spatial reference
        desc = arcpy.Describe(f)
        sr = desc.spatialReference
        # print("Spatial reference: ", sr)

        # Copy FDS to FGDB, create dataset in file geodataset with the same spatial reference
        arcpy.CreateFeatureDataset_management(os.path.join(outws, fgdb_name), f, spatial_reference = sr)

        # Copy the FCs to new FDS
        arcpy.env.workspace = os.path.join(inws, m, f) # set workspace to the dataset in input personal geodatabase
        # print("Workspace directly in dataset: ", arcpy.env.workspace)
        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:
            arcpy.CopyFeatures_management(fc, os.path.join(outws, fgdb_name, f, fc))
            # print("Feature class: ", fc)

# test if the personal geodatabases and the file geodatabases have the same set of files.
mdbs_s = set()
gdbs_s = set()
for m in mdbs:
    mdbs_s.add(m.split("\\")[-1][:-4]) # get the filename of mdbs without extensions.
for g in locate_dir(pattern_gdb, root=outws):
    gdbs_s.add(g.split("\\")[-1][:-4]) # get the filename of gdbs without extensions.
print(mdbs_s == gdbs_s)