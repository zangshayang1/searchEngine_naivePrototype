#! bin/bash/python

import sys
import time



class Reducer(object):
    """
    this class implements 2-way external mergeSort, while counting the shared tokens

    @ input: two opened readables, containing <token, occurrence> sorted by token
    @        some threshold_length that limits List<token> to grow further before the merged results get dumped.
    @ output: a merged file
    @ return: number of shared tokens
    """
    def __init__(self, readable1, readable2, threshold_length = 2 ** 20):
        self.readable1 = readable1
        self.readable2 = readable2
        self.threshold_length = threshold_length

    def _pass_token_check(self, tk):
        return len(tk) == 2

    def pass_line_check(self, line):
        tk = line.split(', ')
        return self._pass_token_check(tk)


    def _output(self, mergedlist, writable):
        # assert writable mode = 'a'
        print "IO"
        writable.write(''.join(mergedlist))
        return ;

    def merge_to(self, writable, count_same_token = False):
        num_of_same_token = 0
        mergedlist = []

        f1 = self.readable1
        f2 = self.readable2
        line1, line2 = f1.readline(), f2.readline()

        while line1 and line2:

            if not self.pass_line_check(line1):
                print "Wrong Input Detected. Skip."
                line1 = f1.readline()
                continue
            if not self.pass_line_check(line2):
                print "Wrong Input Detected. Skip."
                line2 = f2.readline()
                continue

            tk1, tk2 = line1.split(', '), line2.split(', ')

            if tk1[0] < tk2[0]:
                mergedlist.append(line1)
                line1 = f1.readline()
            elif tk1[0] > tk2[0]:
                mergedlist.append(line2)
                line2 = f2.readline()
            else:
                num_of_same_token += 1
                k = tk1[0]
                v = int(tk1[1].rstrip()) + int(tk2[1].rstrip())
                mergedlist.append(k + ', ' + str(v) + '\n')
                line1, line2 = f1.readline(), f2.readline()

            if len(mergedlist) > self.threshold_length:
                self._output(mergedlist, writable)
                mergedlist.clear()

        if count_same_token:
            return num_of_same_token

        while line1:
            if not self.pass_line_check(line1):
                print "Wrong Input Detected. Skip."
                line1 = f1.readline()
                continue
            mergedlist.append(line1)
            line1 = f1.readline()
            if len(mergedlist) > self.threshold_length:
                self._output(mergedlist, writable)
                mergedlist.clear()

        while line2:
            if not self.pass_line_check(line2):
                print "Wrong Input Detected. Skip."
                line2 = f2.readline()
                continue
            mergedlist.append(line2)
            line2 = f2.readline()
            if len(mergedlist) > self.threshold_length:
                self._output(mergedlist, writable)
                mergedlist.clear()

        # output the rest
        self._output(mergedlist, writable)
        return num_of_same_token



def main(ofile_name):

    ofile = open(ofile_name, 'a')
    f1, f2 = open(sys.argv[1], 'r'), open(sys.argv[2], 'r')

    r = Reducer(f1, f2)
    r.merge_to(ofile)

    f1.close()
    f2.close()
    ofile.close()

    print "done."
    return 0


if __name__ == '__main__':
    main("reducer_test_result.txt")
