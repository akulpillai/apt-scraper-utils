##########################################################################
#
# This script will download all the C/C++ package tar sources to a local 
# folder -> extract, build and install the tar sources -> extract the .bc 
# files from the installed archives using wllvm
# 
# invoke this script with sudo, so that packages can be installed
#
##########################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library
import os
import subprocess
import sys
import re

source_file_to_read_packages_from = "/mnt/disks/workdisk/randogcc/debian_packages/Sources"
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"
local_download_folder_for_sources = "/mnt/disks/workdisk/randogcc/debian_packages/downloads/"
extracted_tar_sources = '/mnt/disks/workdisk/randogcc/debian_packages/extracted_tar_sources/'
afl_fuzzing_sources = '/mnt/disks/workdisk/randogcc/debian_packages/afl_sources/'
ALL_OPTIONS_PATH="/mnt/disks/workdisk/randogcc/RandoLLvM/gcc_all_options.txt"
CURR_OPTIONS_PATH="/mnt/disks/workdisk/randogcc/RandoLLvM/empty.txt" #point to an empty file

if not os.path.isdir(local_download_folder_for_sources):
    cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(afl_fuzzing_sources):
    cmd = "(" + "mkdir " + afl_fuzzing_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(extracted_tar_sources):
    cmd = "(" + "mkdir " + extracted_tar_sources + ")"
    subprocess.call(cmd, shell=True)


p = PackageManager(source_file_to_read_packages_from, mirror_url)
p.build_pkg_entries()

p.dump_to_pickled_json("dummp.picked.json")
p2 = PackageManager.from_picked_json("dummp.picked.json")


packages_available = p.all_pkg_entries

#for making package installation noninterative
cmd = "(" + "export DEBIAN_FRONTEND=noninteractive" + ")"
subprocess.call(cmd, shell=True)

pks = ["acct","acpid","augeas","bash","bind9","bsdmainutils","dbus","desktop-file-utils","devio","e2fsprogs","enchant","gettext","gf-complete","gobject-introspection","libcap-ng","libcdio","libdatrie","libeot","libjpeg-turbo","libraw1394","libsamplerate","lxc","m17n-lib","min12xxw","mlocate","mtdev","mutt","nettle","patchutils","pkg-config","procps","psmisc","slang2","sysvinit","t1utils","util-linux","valgrind","xmlsec1"]

#for pkgs in pks:
#    reverse_dependencies = []
#    dependency_list = p.dependency_map[pkgs]
#    for dependencies in dependency_list:
#        # install all reverse dependencies might be too slow (not necessary), uncomment if needed
#        #for reverse_deps in p.reverse_dependency_map[dependencies]:
#        #    subprocess.call(['sudo apt -yq install', str(reverse_deps)], shell=True)        
#        subprocess.call(['sudo apt -yq install', str(dependencies)], shell=True)
#        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
#    
#    for lib in reverse_dependencies:
#        if (find_library(lib) != None):
#            print()
#            print("...")
#            print("DOWNLOADING "+ str(pkgs) + "from the mirror...")
#            print("...")
#            p.download_package_source(pkgs, local_download_folder_for_sources)
#            break

cmd = "cd " + local_download_folder_for_sources 
subprocess.call(cmd, shell=True)
os.chdir(local_download_folder_for_sources)
#Extract the tar sources, build them and install and put them in another folder
for subdir, dirs, files in os.walk(local_download_folder_for_sources):
    
    for File in files:
        if "orig" in str(File):

            #extract the archive
            cmd =  "tar -xvf " + str(File) 
            subprocess.call(cmd, shell=True)

            archive_parts = File.split(".orig")
            underscore_split = archive_parts[0].split("_")
            directory_name = str(underscore_split[0]) + "-" + str(underscore_split[1])

            configure_path = local_download_folder_for_sources + "/" + directory_name + "/" + "configure"
            #check if a configure script exists in the directory
            if( os.path.exists(configure_path) == True ):
                print(File)
                #now cd into the archive
                cmd = "cd " +  directory_name + " ; " + "export COPA_COMPILER=gcc; export COPA_CXX_COMPILER=g++; export COPA_ALL_OPTIMIZATION_FLAGS_FILE=" + ALL_OPTIONS_PATH + "; export COPA_CURR_OPTIMIZATION_FLAGS_FILE=" + CURR_OPTIONS_PATH + ";" +  "CC=wllvmcopa CXX=wllvmcopa++ ./configure" +  " ; " + "make" + " ; " + "make install DESTDIR=" + extracted_tar_sources + "/" + directory_name 
                subprocess.call(cmd, shell=True)

#run extract-bc to get the bit-code files form the binaries
#for subdir, dirs, files in os.walk(extracted_tar_sources):
#
#    if subdir.endswith("/bin"):
#
#        for File in files:
#            cmd = "(" + "cd " + subdir + " && " + "extract-bc " + File + " && " + "mv " + File + ".bc " + afl_fuzzing_sources + ")"
#            subprocess.call(cmd, shell=True)
#


