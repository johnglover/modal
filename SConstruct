# Copyright (c) 2010 John Glover, National University of Ireland, Maynooth
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os, sys
import distutils.sysconfig

# location of msys (windows only)
# by default, it installs to C:/msys/1.0
msys_path = "C:/msys/1.0"

def get_platform():
    if sys.platform[:5] == "linux":
        return "linux"
    elif sys.platform[:3] == "win":
        return "win32"
    elif sys.platform[:6] == "darwin":
        return "darwin"
    else:
        return "unsupported"

def get_version():
    return sys.version[:3]

# check that the current platform is supported
if get_platform() == "unsupported":
    print "Error: Cannot build on this platform. "
    print "       Only Linux, Mac OS X and Windows are currently supported."
    exit(1)

# environment
env = Environment(ENV=os.environ)

# set default installation directories
default_install_dir = ""
if get_platform() == "win32":
    default_install_dir = "C:/msys/1.0/local"
    man_prefix = "C:/msys/1.0/local/man/man1"
else:
    default_install_dir = "/usr/local"
    man_prefix = "/usr/share/man/man1"

# command-line options
vars = Variables(["variables.cache"])
vars.AddVariables(
    ("prefix", "Installation directory", default_install_dir),
    ("libpath", "Additional directory to search for libraries", ""),
    ("cpath", "Additional directory to search for C header files", ""),
    BoolVariable("optimise", "Whether or not to compile with optimisation flags set", True)
)
vars.Update(env)
vars.Save("variables.cache", env)
Help(vars.GenerateHelpText(env))

# set library and header directories
if get_platform() == "linux":
    env.Append(LIBPATH=["/usr/local/lib", "/usr/lib"])
    env.Append(CPPPATH=["/usr/local/include", "/usr/include"])
elif get_platform() == "darwin":
    env.Append(LIBPATH=["/opt/local/lib", "/usr/local/lib", "/usr/lib"])
    env.Append(CPPPATH=["/opt/local/include", "/usr/local/include", "/usr/include"])
elif get_platform() == "win32":
    env.Append(LIBPATH=["/usr/local/lib", "/usr/lib", "C:/msys/1.0/local/lib", 
                        "C:/msys/1.0/lib", "C:/Python26/libs"])    
    env.Append(CPPPATH=["/usr/local/include", "/usr/include", "C:/msys/1.0/local/include",
                        "C:/msys/1.0/include", "C:/Python26/include"])

# add paths specified at the command line    
env.Append(LIBPATH = env["libpath"])
env.Append(CPPPATH = env["cpath"])

conf = Configure(env)

# check whether to include optimisation flags or not
if env['optimise']:
    env.Append(CCFLAGS='-O3')

# set python library and include directories
python_lib_path = []
python_inc_path = []
# linux
if get_platform() == "linux":
    python_inc_path = ["/usr/include/python" + get_version()]
# os x
elif get_platform() == "darwin":
    python_inc_path = ["/Library/Frameworks/Python.framework/Headers", 
                       "/System/Library/Frameworks/Python.framework/Headers"]
# windows
elif get_platform() == "win32":
    python_lib = "python%c%c"% (get_version()[0], get_version()[2])
    python_inc_path = ["c:\\Python%c%c\include" % (get_version()[0], get_version()[2])]
    python_lib_path.append("c:\\Python%c%c\libs" % (get_version()[0], get_version()[2]))

# check for python
if not conf.CheckHeader("Python.h", language="C"):
    for i in python_inc_path:
        pythonh = conf.CheckHeader("%s/Python.h" % i, language="C")
        if pythonh:
            break
if not pythonh:
    print "Error: Python headers are missing."
    exit(1)
    
# check for swig
if not "swig" in env["TOOLS"]:
    print "Error: Swig was not found."
    exit(1)
    
# check for numpy
try:
    import numpy
    try:
        numpy_include = numpy.get_include()
    except AttributeError:
        numpy_include = numpy.get_numpy_include()
except ImportError:
    print "Error: Numpy was not found."
    exit(1)
env.Append(CPPPATH = numpy_include)

# check for libmath
if not conf.CheckLibWithHeader('m','math.h','c'):
    print "Error: libmath could not be found."
    exit(1)

# check for fftw
if not conf.CheckHeader("fftw3.h", language="C"):
    print "Error: FFTW3 was not found."
# add the fftw3 library
# should this not be added by the conf.CheckHeader function?
# doesn't seem to be on OS X 10.5, Python 2.6.5
env.Append(LIBS = ["fftw3"])
  
env = conf.Finish()

# get python installation directory
python_install_dir = distutils.sysconfig.get_python_lib()
python_install_dir = os.path.join(python_install_dir, "modal")
env.Alias('install', python_install_dir)

# set source and library paths
env.Append(SWIGFLAGS = ["-python", "-c++"])
for lib_path in python_lib_path:
    env.Append(LIBPATH = lib_path) 
for inc_path in python_inc_path:
    env.Append(CPPPATH = inc_path)

# create the python wrapper using SWIG
python_wrapper = env.SharedObject("detectionfunctions/detectionfunctions.i")
sources = ["detectionfunctions/detectionfunctions.cpp",
           "detectionfunctions/mq.cpp"]
sources.append(python_wrapper) 

# copy the generated .py file to the root directory
Command("pydetectionfunctions.py", "detectionfunctions/pydetectionfunctions.py", Copy("$TARGET", "$SOURCE"))

# build the module
if get_platform() == "win32":
    env.Append(LIBS = [python_lib])
    env.SharedLibrary("pydetectionfunctions", sources, SHLIBPREFIX="_", SHLIBSUFFIX=".pyd")
elif get_platform() == "darwin":
    env.Append(LIBS = ["python" + get_version()])
    env.Prepend(LINKFLAGS=["-framework", "python"])
    env.LoadableModule("_pydetectionfunctions.so", sources)
else: # linux
    env.Append(LIBS = ["python" + get_version()])
    env.SharedLibrary("pydetectionfunctions", sources, SHLIBPREFIX="_") 
        
# Install
if get_platform() == "win32":
   modules = Glob("*.pyd", strings=True)
else:
   modules = Glob("*.so", strings=True)

modules.extend(Glob("*.py", strings=True))
modules.extend(Glob("analysis/*.py", strings=True))
modules.extend(Glob("data/*.py", strings=True))
modules.extend(Glob("results/*.py", strings=True))
modules.extend(Glob("ui/*.py", strings=True))
modules.extend(Glob("utils/*.py", strings=True))

for module in modules:
   env.InstallAs(os.path.join(python_install_dir, module), module)

