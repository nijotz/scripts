#!/usr/bin/env python
import os
import sys
import json
import subprocess
import re
import pyinotify #WatchManager, Notifier, ProcessEvent, EventsCodes


class FileWatcher(pyinotify.ProcessEvent):
    
    # Inputs a regular expression string
    def __init__(self, mask=None):
        if mask: self._mask = mask
        else: self._mask = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']
        self._wm = pyinotify.WatchManager()
        self._watches = {}

    def addWatch(self, directory, function, fileregex=''):
        self._wm.add_watch(directory, self._mask)
        self._watches[directory] = (re.compile(fileregex), function)
   
    def run(self):
        self._notifier = pyinotify.Notifier(self._wm, self)

        while True:
            try:
                self._notifier.process_events()
                if self._notifier.check_events():
                    self._notifier.read_events()

            except KeyboardInterrupt:
                self._notifier.stop()
                break

    def process_IN_CREATE(self, event):
        (r,f) = self._watches[event.path]  #file regex, function for the path
        if not r.match(event.name): return
        f(event.path, event.name)



def runCommands(path, name):
   
    # Get cmd
    m = re.match('(ifconfig|route)', name)
    cmd = m.group()
    if not cmd: return

    # Get args
    f = open(os.path.join(path, name), 'r')
    args = json.loads(f.read())

    # Run it 
    cmd = [cmd] + args
    print cmd
    if subprocess.call(cmd) != 0: raise Exception('err')


if __name__ == '__main__':
    p = FileWatcher()
    vservers_dir = '/etc/vservers'
    if not (os.path.isdir(vservers_dir)): print 'vservers directory does not exist'; sys.exit(1)
    for directory in os.listdir(vservers_dir):
        vpndir = os.path.join(vservers_dir, directory, 'vdir', 'etc/openvpn/network-cmds')
        if os.path.isdir(vpndir):
            p.addWatch(vpndir, runCommands, '(ifconfig|route)\..+')
            print 'Adding watch for {0}'.format(vpndir)
    p.run()
