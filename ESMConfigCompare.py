__author__ = 'Vosteen'
__version__ = "0.1"
__updated__ = "11.1.2015"
__date__ = "11.1.2015"

import ESMConfigCompareCommon
import ESMExportReader
import sys
import logging
import os
import clientdb

# import misc modules
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

ESMConfigCompareCommon.ClientConfig('ESMConfigCompareScript')
logger = logging.getLogger('ESMConfigCompareScript')
logger.info("Started ESM Config Compare")

def GetArgs(arglist):
    """
    parse and validate the arguments passed to the function, using the argparser
    input:  arglist
    output: namespace containing parsed arguments
    """
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_shortdesc = "ESM Config Compare Script"
    program_license = '''%s

  Created by Rick Vosteen on %s.
  Copyright 2015 Microsoft, Inc. All rights reserved.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE: ESMConfigCompare.py [-h] [-V] [-c|--comments COMMENTS_FOR_IMPORT_JOB] [--d|--debug DEBUG|INFO|WARNING|ERROR|FATAL] [-m|--mode IMPORT|TEST] -i INSTANCE_LABEL_NAME -f IMPORT_FILE
''' % (program_shortdesc, str(__date__))
    program_name = os.path.basename(arglist[0])
    program_version_message = '%s %s (%s)' % (program_name, program_version, program_build_date)
    del arglist[0]
    try:
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter, prog=program_name)
        parser.add_argument('-c', '--comments', dest="importComments", help="analyst comments to include in the shift log", default='no analyst comment specified', nargs='?', const='no analyst comment entered', required=False)
        parser.add_argument('-d', '--debug', dest="debug", default="INFO", help="debug messaging level: DEBUG, INFO, ERROR, FATAL", choices=['DEBUG','INFO','ERROR','FATAL'], nargs='?', const='INFO', required=False)
        parser.add_argument('-m', '--mode', dest='mode', default="TEST", help="mode in which to run: TEST or IMPORT, defaults to TEST.  IMPORT imports it into a SQLite DB", choices=['TEST','IMPORT'], nargs='?', const='TEST', required=False)
        parser.add_argument('-V', '--version', action='version', version=program_version_message, help="display program version message")
        parser.add_argument('-i',  dest='esmInstance', help="ESM Instance.  If instance isn't one of the ones configured in the database, a new entry will be created.",  nargs='?', required=True)
        parser.add_argument('-f', dest='fileImport', help="file that will be read in.  You should rename the arb file to a zip, extract the xml and point to this file",  nargs='?', required=False)
        args = parser.parse_args(arglist)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception, e:
        logger.exception('fatal error parsing arguments, error=' + repr(e) + ". for help please user --help")
        raise

    arglist = []

    return args

def main(argv=None):
    import xml.etree.ElementTree as ET
    print "start!"
    """ main routine, takes no parameters"""

    # get the arguments, put into dictionary
    parsedArgs = GetArgs(sys.argv)

    # set the overall logging level baed on debug argument
    debugDict = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR, 'FATAL': logging.FATAL}
    logger.setLevel(debugDict[parsedArgs.debug])

    # enumerate passed parameters
    for attr, value in parsedArgs.__dict__.iteritems():
        logger.debug(" Arguments passed: value specified or defaulted: " + attr + ": " + repr(value))

    print parsedArgs.esmInstance
    print parsedArgs.fileImport
    ESMFile = ESMExportReader.arcsightXMLParser()


    DBCon = clientdb.ClientDb()

    # Get Instance Id
    InstanceId = DBCon.LookupESMInstanceID(parsedArgs.esmInstance)

    print "InstanceId: " + str(InstanceId)
    # Create Import List Record
    DBCon.insertImportList(InstanceId)
    ImportId = DBCon.LookupImportID()
    NewCleanFileName = ESMFile.CleanFileofListsNote(parsedArgs.fileImport)

    try:
        tree = ET.parse(NewCleanFileName)
    except:
        sys.exit("Could not open XML file1: " + NewCleanFileName)

    root = tree.getroot()

    ESMFile.ReadResource(root, NewCleanFileName, 'Field', ImportId, InstanceId)

    print "Done processing Global Variables... "

    ESMFile.ReadResource(root, NewCleanFileName, 'Rule', ImportId, InstanceId)
    print "Done processing Rules... "

    ESMFile.ReadResource(root, NewCleanFileName, 'Group', ImportId, InstanceId)

    print "Done processing Groups... "

    ESMFile.ReadResource(root, NewCleanFileName, 'Filter', ImportId, InstanceId)

    print "Done processing Filters... "




#priming object
if __name__ == "__main__":
    mainrc = main()
    print "ESMConfigCompare.py ended, rc=" + str(mainrc)
    sys.exit(mainrc)
