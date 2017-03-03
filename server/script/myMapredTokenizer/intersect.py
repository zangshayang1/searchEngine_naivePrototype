#! bin/bash/python

import sys
import os
import subprocess
from wordfreq import WordCount
from reducer import Reducer

def main():
    """
    This main() implements the following process and print out the number of shared tokens from two txt files

    @ outputs sorted tokenized results from txt1
    @ outputs sorted tokenized results from txt2

    @ merges these two sorted results and print out the number of shared tokens
    @ outputs the merged results
    """
    assert not os.path.exists(sys.argv[3]), "ERROR: merged output file already exists!"

    temp1, temp2 = ".f1_temp", ".f2_temp"

    t1, t2 = open(temp1, 'w'), open(temp2, 'w')

    f1, f2 = open(sys.argv[1], 'r'), open(sys.argv[2], 'r')

    wc1, wc2 = WordCount(f1), WordCount(f2)

    wc1.output_to(t1)
    wc2.output_to(t2)

    t1.close()
    t2.close()

    f1.close()
    f2.close()

    t1, t2 = open(temp1, 'r'), open(temp2, 'r')

    ofile = open(sys.argv[3], 'a')

    r = Reducer(t1, t2)

    num_of_same_token = r.merge_to(ofile, count_same_token = True)

    print "# of common tokens: ", num_of_same_token

    t1.close()
    t2.close()
    ofile.close()

    subprocess.call(["rm", ".f1_temp", ".f2_temp"])

    return 0


if __name__ == '__main__':
    main()
