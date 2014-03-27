#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import os, sys, getopt
import termios as libtermios
try:
    from termcolor import colored
except:
    def colored(text, color=None, on_color=None, attrs=None):
        return text

registry = {}

def register_bitor(*args, **kwargs):
    def decorator(func):
        def wrapper(*fargs, **fkwargs):
            return func(*fargs, **fkwargs)
        wrapper.func_name = func.func_name
        wrapper.__doc__ == func.__doc__
        for k in args:
            registry[wrapper.func_name + '.' + k] = wrapper
    return decorator

@register_bitor('iflags', 'oflags', 'cflags', 'lflags')
def termios(number, key):
    flags = {
        'iflags': 'IGNBRK BRKINT IGNPAR PARMRK INPCK ISTRIP INLCR IGNCR ICRNL IUCLC IXON IXANY IXOFF IMAXBEL IUTF8'.split(' '),
        'oflags': 'OPOST OLCUC ONLCR OCRNL ONOCR ONLRET OFILL OFDEL NLDLY CRDLY TABDLY BSDLY VTDLY FFDLY'.split(' '),
        'cflags': 'CBAUD CBAUDEX CSIZE CSTOPB CREAD PARENB PARODD HUPCL CLOCAL LOBLK CIBAUD CMSPAR CRTSCTS'.split(' '),
        'lflags': 'ISIG ICANON XCASE ECHO ECHOE ECHOK ECHONL ECHOCTL ECHOPRT ECHOKE DEFECHO FLUSHO NOFLSH TOSTOP PENDIN IEXTEN'.split(' '),
    }
    if key not in flags: return None
    ret = []
    for opt in flags[key]:
        try:
            if getattr(libtermios, opt) & number:
                ret.append(opt)
        except BaseException, ex:
            pass
    return ret

def FIND(key, hint): return key.lower().find(hint.lower()) > -1

def magic(number, hints, mode = FIND):
    ret = {}
    for keyword in registry:
        for hint in hints:
            if not mode(keyword, hint):
                break
        else:
            rs = registry[keyword](number, keyword.split('.', 1)[1])
            if rs:
                ret[keyword] = rs
    return ret

def usage():
    print """
usage:
    $ magic.py number [keyword | [keyword] ...]

examples:
    $ magic.py 10240 iflags
"""
    
def main():
    number = 0
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    if sys.argv[1].startswith('0x'):
        try:
            number = int(sys.argv[1], 16)
        except:
            usage()
            sys.exit(10)
    else:
        try:
            number = int(sys.argv[1], 10)
        except:
            usage()
            sys.exit(11)
    rs = magic(int(sys.argv[1]), sys.argv[2:])
    for k in rs:
        w = rs[k]
        sys.stdout.write(colored(k, 'yellow') + '\r\n')
        sys.stdout.write('    ' + colored(isinstance(w, list) and ' | '.join(w) or w, 'cyan') + '\r\n')
        sys.stdout.flush()

if __name__ == '__main__':
    main()

