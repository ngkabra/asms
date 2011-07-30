import socket
import android
try:
    droid = android.Android(addr=('localhost', '12345'))
except socket.gaierror:
    from subprocess import call
    if call('alink'):
        print 'You need to re-start sl4a server and run alink perhaps?'
        exit(1)
    else:
        droid = android.Android(addr=('localhost', '12345'))

