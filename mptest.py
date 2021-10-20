import timeit, bpy, mathutils, sys
from multiprocessing import Pool
from concurrent import futures

def a():
    bpy.ops.particle.particle_edit_toggle()
    eobj = bpy.context.active_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
    psys = eobj.particle_systems["hair1"]
    for i in range(psys.settings.count):
        for j in range(psys.settings.hair_step+1):
            psys.particles[i].hair_keys[j].co = mathutils.Vector((0,0,0))
            
def b():
    bpy.ops.particle.particle_edit_toggle()
    eobj = bpy.context.active_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
    psys = eobj.particle_systems["hair1"]
    for p in psys.particles:
        for h in p.hair_keys:
            h.co = mathutils.Vector((0,0,0))
            
def c():
    bpy.ops.particle.particle_edit_toggle()
    eobj = bpy.context.active_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
    psys = eobj.particle_systems["hair1"]
    initial_num_list = list(range(10000))
#    with Pool(processes=4) as p:
#        p.map(func=d, iterable=initial_num_list)
    
    sys.path = ["C:/Program Files (x86)/Intel/iCLS Client/","C:/Program Files/Intel/iCLS Client/","C:/Windows/system32","C:/Windows","C:/Windows/System32/Wbem","C:/Windows/System32/WindowsPowerShell/v1.0/","C:/Program Files (x86)/Intel/Intel(R) Management Engine Components/DAL","C:/Program Files/Intel/Intel(R) Management Engine Components/DAL","C:/Program Files (x86)/Intel/Intel(R) Management Engine Components/IPT","C:/Program Files/Intel/Intel(R) Management Engine Components/IPT","C:/Program Files (x86)/NVIDIA Corporation/PhysX/Common","C:/WINDOWS/system32","C:/WINDOWS","C:/WINDOWS/System32/Wbem","C:/WINDOWS/System32/WindowsPowerShell/v1.0/","C:/Program Files (x86)/GtkSharp/2.12/bin","C:/Program Files (x86)/SoftKinetic/DepthSenseSDK/bin","C:/Program Files/SoftKinetic/DepthSenseSDK/bin","C:/Program Files/Common Files/Autodesk Shared/","C:/Program Files (x86)/Autodesk/Backburner/","C:/Users/tentomizuguchi/.dnx/bin","C:/Program Files/Microsoft DNX/Dnvm/","C:/Program Files/Microsoft SQL Server/130/Tools/Binn/","C:/WINDOWS/System32/OpenSSH/","C:/Program Files/NVIDIA Corporation/NVIDIA NvDLISR","C:/Program Files/Git/cmd","C:/Program Files/dotnet/","C:/WINDOWS/system32","C:/WINDOWS","C:/WINDOWS/System32/Wbem","C:/WINDOWS/System32/WindowsPowerShell/v1.0/","C:/WINDOWS/System32/OpenSSH/","C:/Program Files/mingw-w64/x86_64-8.1.0-posix-seh-rt_v6-rev0/mingw64/bin","C:/Program Files/CMake/bin","C:/opencv/build/x64/vc15/bin","C:/Program Files/SlikSvn/bin","C:/Users/omine/Documents/programs/customBlender/build_windows_x64_vc16_Release/bin/Release/3.0/python/bin","C:/Users/omine/Documents/programs/customBlender/build_windows_x64_vc16_Release/bin/Release/3.0/python/Scripts","C:/Users/omine/Documents/programs/customBlender/lib/win64_vc15/python/37/include","C:/Users/omine/.dnx/bin","C:/Users/omine/AppData/Local/Microsoft/WindowsApps","C:/Users/omine/AppData/Local/Programs/Microsoft VS Code/bin"]
    future_list = []
    with futures.ProcessPoolExecutor(max_workers=4) as executor:
        for i in range(10000):
            future = executor.submit(d)
            future_list.append(future)
        _ = futures.as_completed(fs=future_list)
    sys.path = ['C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\startup', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\modules', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\python39.zip', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\python\\DLLs', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\python\\lib', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\python\\bin', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\python', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\python\\lib\\site-packages', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\freestyle\\modules', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\addons\\modules', 'C:\\Users\\omine\\AppData\\Roaming\\Blender Foundation\\Blender\\3.0\\scripts\\addons\\modules', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\addons', 'C:\\Users\\omine\\AppData\\Roaming\\Blender Foundation\\Blender\\3.0\\scripts\\addons', 'C:\\Users\\omine\\Documents\\programs\\customBlender\\build_windows_x64_vc16_Release\\bin\\Release\\3.0\\scripts\\addons_contrib']

def d():
    a = 1+1
#    for j in range(99+1):
##        psys.particles[num].hair_keys[j].co = mathutils.Vector((0,0,0))
#        pass
    
def exe():
    t = timeit.Timer("c()", globals = globals())

    print(t.timeit(1))

