__author__ = 'clyde'

from subprocess import check_output, CalledProcessError
import re
import io
import os
from math import ceil

""" USAGE:
    1- from TextRemapper import TextRemapper
    2- instantiate the TextRemapper object with the full pathname and the target and replacement strings:
    tr = TextRemapper(<full_pathname>, <target string>, <replacement string>)
    3- call the instance:
    tr()
    """
class TextRemapper():
    """TextRemapper is meant for string replacement in large text files.
        It replaces a target string with a replacement string block-wise
        without reading the entire file into memory. The operation is
        extremely fast."""

    def __init__(self, filename, str1, str2, block_size=4096, file_size=0):
        self.filename = filename
        self.str1 = str1
        self.str2 = str2
        self.block_size = block_size
        self.file_size = file_size

    def __call__(self, *args, **kwargs):
        try:
            fo = open(self.filename)
            fo.close()
        except IOError, e:
            print 'Could not execute TextRemapper object.', e
            return 0
        self.__process_blocks()

    def __get_block_size(self):
        """not tested on Windows"""
        try:
            s = check_output(['stat', self.filename])
        except CalledProcessError:
            return 4096
        b = re.search(r'IO Block\d*: (\d+)', s)
        return int(b.groups()[0]) if int(b.groups()[0]) else 4096

    def __calc_blocks(self):
        self.file_size = os.stat(self.filename).st_size
        blocks = int(ceil(float(self.file_size)/self.block_size))
        last_block = self.file_size%self.block_size
        return blocks, last_block

    def __last_block(self, lastblock, file_obj):
        chunk = file_obj.read(lastblock)
        chunk_new = chunk.replace(self.str1, self.str2)
        file_obj.seek(-1*lastblock, 1)
        file_obj.write(chunk_new)
        file_obj.flush()
        return True

    def __process_blocks(self):
        try:
            blocks, lastblock = self.__calc_blocks()
        except OSError, e:
            print e
            return 0
        print 'number of blocks: ', blocks
        fo = io.open(self.filename, 'r+b')
        file_obj = io.BufferedRandom(fo)
        if blocks == 1:
            self.__last_block(lastblock, file_obj)
            file_obj.truncate(lastblock)
            file_obj.close()
            print 'Success'
            return 1
        elif blocks > 1:
            for i in xrange(blocks-1):
                chunk = file_obj.read(self.block_size)
                new_chunk = chunk.replace(self.str1, self.str2)
                file_obj.seek(-1*self.block_size, 1)
                file_obj.write(new_chunk)
                file_obj.flush()
            self.__last_block(lastblock, file_obj)
            file_obj.truncate(self.file_size)
            file_obj.close()
            print 'Success'
            return 1

