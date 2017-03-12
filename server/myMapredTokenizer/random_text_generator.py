#! bin/bash/python

import numpy as np
import time
import sys



def generate_random_char():
    r = np.random.rand()
    v = int(abs(r) * 128)
    nextchar = chr(v)
    return nextchar

def output_stringJoin(size, ofile_name):
    output = [None for _ in xrange(size)]
    counter = 0
    while counter < size:
        # 1 char == 1 Byte
        nextchar = generate_random_char()
        output[counter] = nextchar
        counter += 1

    ofile = open(ofile_name, 'w')
    ofile.write(''.join(output))
    ofile.close()

    return counter


def generate_random_token(length):
    """
    @ return string
    """
    randomInt_array = np.random.randint(97, 123, (length))
    tk = [chr(num) for num in randomInt_array]
    tk = "".join(tk)
    return tk


def generate_random_text(size, ofile_name):

    s = time.time()

    num_of_chars = output_stringJoin(size, ofile_name)

    print time.time() - s
    print "number of chars: ", num_of_chars
    return ;

def generate_sorted_tokens(size, token_length, ofile_name):
    ofile = open(ofile_name, 'w')

    output = [None for _ in xrange(size / token_length + 1)]
    l = len(output)
    counter = 0
    while counter < l:
        tk = generate_random_token(token_length)
        output[counter] = tk + ', ' + str(np.random.randint(1, 5)) + '\n'
        counter += 1

    output = sorted(output, key = lambda x : x[0])
    ofile.write(''.join(output))
    ofile.close()

    return counter

print "start..."
generate_random_text(1 * 1024 ** 2, "random_text1.txt")
print "half..."
generate_random_text(1 * 1024 ** 2, "random_text2.txt")
print "done."
