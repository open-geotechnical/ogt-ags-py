#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from ogt import FORMATS
import ogt.ogt_doc
import ogt.ags4
import ogt.utils


## Main Parser
parser = argparse.ArgumentParser(description="Toolkit for geotechnical")

## Subparsers container
sub_parsers = parser.add_subparsers(help="commands", dest="command")
#p_help = sub_parsers.add_parser("help", help="Show help")

#=======================
## Convert Parser
p_convert = sub_parsers.add_parser("convert", help="Convert files")

p_convert.add_argument("-b", "--beside", dest="beside", action="store_true", help="save beside original file and appends `.ext`")

p_convert.add_argument("-e", "--editor", dest="editor", action="store_true", help="outputs denser data, eg descriptions, picklists, etc)")

p_convert.add_argument("-f", "--format", dest="format", default="json", help="output format and ext", choices=FORMATS)

p_convert.add_argument("-m", "--minify", dest="minify", action="store_true", help="minify the output by removing whitespace")

p_convert.add_argument("-o", "--overwrite", dest="overwrite", action="store_true", help="overwrite output file if it exists")

p_convert.add_argument("--stats", dest="inc_stats", action="store_true", help="include stats in output (only json/yaml)")
p_convert.add_argument("--source", dest="inc_source", action="store_true", help="include source text and cells")

p_convert.add_argument("-w", "--write_file", dest="write_file",  help="output file to write")

p_convert.add_argument("-z", "--zip", dest="zip", action="store_true", help="output as a zip file containing original and converted file")

#p_convert.add_argument("-v", "--validate", dest="validate", action="store_false", help="validates ags file")
p_convert.add_argument("source_file", type=str, help="AGS4 file to convert")


#=======================
## Validator parser
p_validate = sub_parsers.add_parser("validate", help="Validate files")
p_validate.add_argument("-p",   action="store_false",  dest="printable", help="Human print output")
p_validate.add_argument("-r", "--rules", type=int, dest="rules",  nargs='+', default=[], help="Rules to check")
p_validate.add_argument("-t", "--tests", action="store_true", dest="run_tests", help="Run Tests")
p_validate.add_argument("source_file", type=str, help="AGS4 file to validate")

#=======================
## WWW server
"""
p_server = sub_parsers.add_parser("serve", description="Run the www server")
p_server.add_argument("-a", dest="address", help="eg localhost, 0.0.0.0,  123.12.23.45", default='127.0.0.1')
p_server.add_argument("-p", dest="port", help="Port No, default: 1377", default=1377)
p_server.add_argument("-d", dest="debug", help="Dev mode shows debug and restart on files changed", action="store_true",  default=False)
"""
#=======================
## Update
p_update = sub_parsers.add_parser("update", description="Setup and update")


#=======================
## Add some standard items
x_parsers = [p_convert, p_validate]
for p in x_parsers:
    p.add_argument("--debug", dest="debug", action="store_false", help="debug")


if __name__ == "__main__":

    args = parser.parse_args()

    ## Update comes first
    if args.command == "update":
        err = ogt.ags4.update()
        if err:
            print "Update failed: %s" % err
        else:
            print "Update successful"
        sys.exit(0)

    ## Load agsdata dict etc
    err =  ogt.ags4.initialise()
    if err:
        print err
        print "Have you run `ogt-cli.py update` to download data dict ?"
        sys.exit(0)

    """
    if args.command == "serve":

        import ogtserver.main
        ogtserver.main.start_server(port=args.port, address=args.address, debug=args.debug)
    """

    if args.command == "validate":
        if args.source_file.endswith(".ags"):
            report, err = ogt.ags4.validate_ags4_file(args.source_file, args.rules)

            if err != None:
                print err

            else:
                print "----------------------"
                if args.printable:
                    print ogt.ags4.report_to_string(report)
                else:
                    print report



    elif args.command == "convert":


        if args.source_file.endswith(".json"):
            doc, err = ogt.ogt_doc.create_doc_from_json_file(args.source_file)

        elif args.source_file.endswith(".ags"):
            doc, err = ogt.ogt_doc.create_doc_from_ags4_file(args.source_file)

        if err != None:
            print err

        else:
            doc.minify = args.minify
            doc.edit_mode = args.editor
            doc.include_stats = args.inc_stats,
            doc.include_source = args.inc_source
            mess, err = doc.write(ext=args.format,
                                beside=args.beside, file_path=args.write_file,
                                zip=args.zip, overwrite=args.overwrite)
            if err:
                print err
            else:
                print mess



