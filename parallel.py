# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 16:09:29 2019

@author: Nathan
"""

from zlib import crc32
from array import array
from tqdm import tqdm

import multiprocessing as mp
import argparse
import time

"""
Default global arg values.
"""
SUFFIX_LENGTH = 4   # word length worker computes permutations of per job
PROCESS_COUNT = 4   # how many processes
PROCESS_TIME = 10.  # how long to process
MIN_CHAR = 97       # ascii a
MAX_CHAR = 122      # ascii z

def iterate(chars):
    """
    Arguments (bytes-like object): Modifies object in-place to next
                                   lexicographic permutation.
    """
    for i, char in enumerate(chars):
        if char is MAX_CHAR:
            chars[i] = MIN_CHAR
        else:
            chars[i] = char + 1
            return
    chars.append(MIN_CHAR)

def worker(prefix, res, needle):
    """
    Arguments:
        prefix (list): The prefix for the words it hashes.
        res: (list): A list to put collision words into.
        needle (ulong): The crc32 hash to compute collision words for.
    """
    
    while True:
        prefix_copy = ''.join(map(chr, prefix))
        base = crc32(prefix_copy.encode())
        iterate(prefix)
        chars = array('b', [MIN_CHAR]*SUFFIX_LENGTH)
        
        for _ in range(26**SUFFIX_LENGTH):
            if crc32(chars, base) == needle:
                res.append(prefix_copy + chars.tobytes().decode())
                iterate(chars)
            else:
                iterate(chars)

def find_hash(needle):
    """
    Arguments:
        needle (ulong): A crc32 hash of a word.
    Returns:
        list: A list of crc32 colliding words with needle found within time.
                These are also printed along with a progress bar showing time.
    """
    
    # progress bar variables
    count = 0
    start = time.time()
    pbar = tqdm(total=PROCESS_TIME, bar_format=\
                '{desc}: {percentage:.2f}%|{bar}| {n:.1f}/{total_fmt}')
    
    # server variables
    manager = mp.Manager()
    res = manager.list()
    prefix = manager.list()
    
    # serially test all strings between 0 and SUFFIX_LENGTH chars
    chars = array('b')
    for j in range(sum(26**i for i in range(SUFFIX_LENGTH))):
        if crc32(chars) == needle:
            found = chars.tobytes().decode()
            pbar.write(found)
            res.append(found)
            count += 1
        if j % 100000 is 0:
            pbar.n = time.time() - start
            pbar.refresh()
        iterate(chars)
    
    # spawn processes
    pool = list()
    for _ in range(PROCESS_COUNT):
        p = mp.Process(target=worker, args=(prefix, res, needle))
        pool.append(p)
        p.start()
    
    # update progress bar and colliding words
    while pbar.n < PROCESS_TIME:
        pbar.n = min(time.time() - start, PROCESS_TIME)
        pbar.refresh()
        for found in res[count:]:
            count += 1
            pbar.write(found)
        time.sleep(0.1)
    
    # end processes
    for p in pool:
        p.terminate()
        p.join()
    
    return res

if __name__ == '__main__':
    """
    Parses cmd args for settings
    Sets the global setting varibles
    Calls the find hash function for the string
    """
    
    # argument parsing
    parser = argparse.ArgumentParser(description=('Compute crc32 collisions '
                                                  'for a word.'))
    parser.add_argument('string', metavar='string', type=str,
                        help='string to compute collisions for')
    parser.add_argument('--suffix_length', '-s', default=SUFFIX_LENGTH, 
                        type=int, help = 'job chunk size for process')
    parser.add_argument('--process_count', '-p', default=PROCESS_COUNT, 
                        type=int, help = 'number of processes')
    parser.add_argument('--process_time', '-t', default=PROCESS_TIME, 
                        type=float, help = 'time to compute for in seconds')
    parser.add_argument('--min_char', '-l', default=MIN_CHAR, 
                        type=int, help = 'ascii lower bound for search')
    parser.add_argument('--max_char', '-u', default=MAX_CHAR, 
                        type=int, help = 'ascii upper bound for search')
    
    # set global default variables unless specified otherwise
    args = parser.parse_args()
    SUFFIX_LENGTH = args.suffix_length
    PROCESS_COUNT = args.process_count
    PROCESS_TIME = args.process_time
    MIN_CHAR = args.min_char
    MAX_CHAR = args.max_char
    
    # call hashing function
    find_hash(crc32(args.string.encode()))
