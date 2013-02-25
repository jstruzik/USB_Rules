#!/usr/bin/env python

"""
File: usb_rules.py
Date: 2012-04-15

A script to quickly scan for new USB drives and add a custom symlink to each one using udev rules.
"""

import re, subprocess, fileinput
from optparse import OptionParser

rules_name = '/etc/udev/rules.d/65-usb.rules'

class usbRules:
    def __init__(self):
        try:
            self.rules_file = open(rules_name,'r')
        except IOError:
            print "I could not find your file! Ahhhhhh! I'll just create one for you ;)"
            self.rules_file = open(rules_name, 'a+')
        self.count = ""
        self.symlink_name = ''
        for s in self.rules_file.readline().strip():
            if s.isdigit():
                self.count += s
                
        self.content = ''.join(self.rules_file.readlines())
        
        if self.content == '':
            self.count = 0
    def add(self, usb_serial):
        match = re.findall('\\b'+usb_serial+'\\b',self.content)
        if match:
            print "You've already have this serial number!"
            return
        command = str("\nSUBSYSTEMS==\"usb\", KERNEL==\"sd?1\", ATTRS{serial}==\""+usb_serial+"\", SYMLINK=\""+self.symlink_name+""+str(self.count)+"part1\"\"\n")
        command2 = str("SUBSYSTEMS==\"usb\", KERNEL==\"sd?2\", ATTRS{serial}==\""+usb_serial+"\", SYMLINK=\""+self.symlink_name+""+str(self.count)+"part2\"")
        commands = [command,command2]
        self.content += ''.join(commands)
        self.count = int(self.count)+1
        self.rules_file.close()
        self.rules_file = open(rules_name, 'w')       
        self.rules_file.writelines(self.content)
        self.rules_file.close()
        print "successfully added " + usb_serial + "!"
    def delete(self, usb_serial):
        if self.content.find(usb_serial) != -1:
            input = raw_input("Found it! You sure you wanna delete? (Y/N)")
            while True:
                if input not in ['y','Y','n','N']:
                    print "Please enter a valid input"
                    continue
                if input == 'y' or input == 'Y':
                    self.count = int(self.count)-1
                    self.contents = ''.split(self.content)
                    for item in self.contents:
                        if usb_serial in item:
                            self.contents.remove(item)
                    self.contents = ('#'+str(self.count)) + '\n' + ''.join(self.contents) 
                    self.rules_file.close()
                    self.rules_file = open(rules_name, 'w')       
                    self.rules_file.writelines(self.contents)
                    self.rules_file.close()
                if input == 'n' or input =='N':
                    return
        else:
            "Serial number not found!"
    def scan(self):
        # Grab output from command "blkid" and split it up by device
        blkid = subprocess.Popen("sudo blkid -t TYPE=\"vfat\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        blkid = blkid.split("\n")
        blkid = [item.split() for item in blkid]
    
        # Last element of blkid is empty or unnecessary, so strip it out
        blkid = blkid[:len(blkid)-1]
        
        
        partitions = []
        for element in blkid:
            partitions.append({})
            for info in element:
                if '/dev/' in info:
                    partitions[len(partitions)-1]= info[:len(info)-1]           
        for item in partitions:
            print item
            get_serial = subprocess.Popen("udevadm info --name="+str(item)+" --query=all | grep SERIAL_SHORT | cut -d= -f2", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            get_serial = get_serial.strip()
            print get_serial
            if self.content.find(get_serial) != -1:
                    print "You've already have this serial number!"
            else:
				header = '#' + str(self.count) + '\n'
                command = str("\nSUBSYSTEMS==\"usb\", KERNEL==\"sd?1\", ATTRS{serial}==\""+get_serial+"\", SYMLINK=\""+self.symlink_name+""+str(self.count)+"part1\"\n")
                command2 = str("SUBSYSTEMS==\"usb\", KERNEL==\"sd?2\", ATTRS{serial}==\""+get_serial+"\", SYMLINK=\""+self.symlink_name+""+str(self.count)+"part2\"")
                commands = [header,command,command2]
                self.content += ''.join(commands)
                print "Adding USB"+str(self.count)
                self.count = int(self.count)+1
                
        self.content = ('#'+str(self.count)) + '\n' + self.content 
        self.rules_file.close()
        self.rules_file = open(rules_name, 'w')       
        self.rules_file.writelines(self.content)
        self.rules_file.close()
if __name__=="__main__":
        main = usbRules()
        parser = OptionParser(
        usage = "usage: %prog [options]",
        
        parser.add_option("-a",
                "--add",
                dest = "add",
                default = '',
                help = "Adds a new USB serial number.")
        parser.add_option("-d",
                "--delete",
                dest = "delete",
                default = '',
                help = "Removes a serial number.")
        parser.add_option("-s",
                "--scan",
                action = "store_true",
                dest = "scan",
                default = False,
                help = "Scans for new drives in the hub and adds them.")
        
        (options, args) = parser.parse_args()
        
        if options.add != '':
            main.add(options.add)
        if options.delete != '':
            main.delete(options.delete)
        if options.scan == True:
            main.scan()
        
