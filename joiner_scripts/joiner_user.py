from joiner import AqGpsJoiner
import getopt
import sys
import os

#Do not use this file
if __name__ == "__main__":
    aq_file = ''
    gps_file = ''
    output_file = ''
    tolerance = 1
    filt = '2.5'
    try:
        opts, args = \
            getopt.getopt(sys.argv[1:], 'ha:g:o:t:f:', ['help', 'aq=', 'gps=', 'out=', 'tolerance=', 'filter='])
    except getopt.GetoptError:
        print 'Expected usage: joiner.py -a <air-quality-file.csv> -g <gps-file.log> -o <output.csv> -t 1 -f 2.5'
        raise
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'joiner.py -a <air-quality-file.csv> -g <gps-file.log> -o <output.csv> -t 1 -f 2.5'
            sys.exit()
        elif opt in ('-a', '--aq'):
            aq_file = arg
        elif opt in ('-g', '--gps'):
            gps_file = arg
        elif opt in ('-o', '--out'):
            output_file = arg
        elif opt in ('-t', '--tolerance'):
            tolerance = int(arg)
        elif opt in ('-f', '--filter'):
            filt = arg
    with open(aq_file, 'r') as a:
        with open(gps_file, 'r') as g:
            with open(output_file, 'wb') as o:
                o.writelines("%s\n" % l for l in AqGpsJoiner(a, g, output_file, tolerance, filt))    