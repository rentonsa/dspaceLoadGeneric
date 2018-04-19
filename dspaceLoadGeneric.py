# Scott Renton, April 2018
# Genericised dspace import structure builder
# Expects XML but can be modified to read from DB

    
from variables import *
import os, shutil, urllib, json, csv

print "Which collection?"
collection = raw_input()
print "Which environment?"
environment = raw_input()
if environment == 'live':
    environment = ''
    webenv = ''
else:
    webenv = environment + "."

newfolder = collection + nfold
for root, dirs, files in os.walk(newfolder):
    for f in files:
        os.unlink(os.path.join(root, f))
    for d in dirs:
        shutil.rmtree(os.path.join(root, d))
        
csvfile2 = open(mapfile, 'rb')
mapping = csv.DictReader(csvfile2, delimiter=':')
maparray = list(mapping)
maplen = len(maparray)
bitstreamdirectory = bitdir
import xml.etree.ElementTree as ET

tree = ET.parse(collection + xmlin)
root = tree.getroot()
from xml.dom import minidom

childno = 0
bitstreamtotal = 0
blankaccs = 0
duplicateaccs = 0
badimagearray = []
badaccnoarray = []
dupaccnoarray = []
disappearedarray = []
# MAIN ITEM LEVEL LOOP
for child in root:
    childno = childno + 1
    import xml.etree.cElementTree as ETOut

    outroot = ETOut.Element(dcheader)
    subfolder = ''
    outfile = ''
    a = 0
    an = 0
    avarray = []
    itemaccno = ''
    outdata = []
    existing = ''
    duplicateacc = falsevar
    systemid = ''
    
    # METADATA PROCESSING
    for object in child:
        #working with each row of data
        tagid = ''
        notetagid = ''
        htpos = ''
        if object.tag == 'id':
            systemid = object.text
        # build array of bitstreams- processed separately
        if object.tag == 'av':
            avarray.append(object.text)
        # accession number will also be folder name- process on its own
        if object.tag == "accession_no":
            j = 0
            existing = falsevar
            itemaccno = object.text
            f = open(collection + "/" + environment + "mapfile.txt")
            for line in f.readlines():
                accno = line.split(' ')[0]
                if itemaccno == accno:
                    existing = truevar
                j = j + 1
            subfolder = newfolder + itemaccno
            if os.path.exists(subfolder):
                duplicateacc = truevar
                duplicateaccs = duplicateaccs + 1
                badaccnoarray.append(systemid)
                dupaccnoarray.append(itemaccno)
                
        # generate metadata array
        m = 0
        while m < maplen:
            if maparray[m]['vernon'] == object.tag:
                mdschema = str(maparray[m]['dc'] + "value")
                mdelement = str(maparray[m]['element'])
                if maparray[m]['qualifier'] == 'noqual':
                    mdqualifier = str('')
                else:
                    mdqualifier = str(maparray[m]['qualifier'])
                dcvalue = ETOut.SubElement(outroot, mdschema)
                dcvalue.set('element', mdelement)
                dcvalue.set('qualifier', mdqualifier)
                dcvalue.text = object.text
            m = m + 1
    #
    print 'Working on this: ' + itemaccno
    if itemaccno == '' or duplicateacc == 'true':
        blankaccs = blankaccs + 1
        badaccnoarray.append(systemid)
    else:
        #generate directory
        os.makedirs(subfolder)
        os.chmod(subfolder, 0o777)
        outfile = subfolder + "/dublin_core.xml"
        contentsfile = subfolder + "/contents"
        cfile = open(contentsfile, "w")
        
        # process bitstreams
        avlen = len(avarray)
        ani = 0
        while ani < avlen:
            pdfpos = avarray[ani].find("pdf")
            if (pdfpos > -1):
                for root, dirs, files in os.walk(bitstreamdirectory):
                    for _file in files:
                        if _file in avarray[ani]:
                            shutil.copy(os.path.abspath(root + '/' + _file), subfolder)
                            cfile.write(_file + "\n")
                            print "Processed bitstream " + _file
                            bitstreamtotal = bitstreamtotal + 1
            ani = ani + 1
        cfile.close()
        
        #write dublin core file
        rough_string = ETOut.tostring(outroot, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="\t")
        file = open(outfile, "w")
        file.write(pretty_string)
        file.close()

#checks        
f = open(collection + "/" + environment + "mapfile.txt")
for accno in f.readlines():
    accno = accno.split(' ')
    found = 0
    try:
        found = os.path.isdir(newfolder + accno[0])
    except ValueError, e:
        print "failure"
    if found == 0:
        disappearedarray.append(accno[0])

f.close()

#output
print 'Processed ' + str(childno) + ' items.'
print 'Processed ' + str(bitstreamtotal) + ' bitstreams.'
print 'Skipped ' + str(blankaccs) + ' records with no accession number.'
print 'Skipped ' + str(duplicateaccs) + ' duplicate accession numbers.'
for badacc in badaccnoarray:
    print "System ID to check: " + badacc
for dupacc in dupaccnoarray:
    print "Dup image: " + dupacc
for badimage in badimagearray:
    print "Image dead: " + badimage
for disappeared in disappearedarray:
    print "Record vanished:" + disappeared
print 'Finished.'


