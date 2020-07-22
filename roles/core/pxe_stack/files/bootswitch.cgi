#!/usr/bin/env python3
# https://github.com/bluebanquise/bluebanquise - MIT license

from shutil import copyfile
import cgi
import cgitb
import os
import sys

cgitb.enable()

arguments = cgi.FieldStorage()
node_name = arguments['node'].value
node_boot = arguments['boot'].value

print('Content-Type: text/html\n\n')

if node_boot == 'disk':
    file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node_name)+'.ipxe','r')
    filebuffer = file.readlines()
    for i in range(len(filebuffer)):
        if 'menu-default' in filebuffer[i]:
            filebuffer[i] = 'set menu-default bootdisk\n'
    file.close
    file = open('/var/www/html/preboot_execution_environment/nodes/'+str(node_name)+'.ipxe','w')
    file.writelines(filebuffer)
    file.close
    print('Boot set to disk')
