
pythonPath = {'python-2.7':'/usr/bin/python', 'python-3.4': '/usr/bin/python3'}

in_file = open("runtime.txt","r")
text = in_file.readline().strip()
in_file.close()

pathPy = pythonPath.get(text)
if  pathPy != None:
    print pathPy
else:
    print 'no'
