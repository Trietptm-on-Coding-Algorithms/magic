#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import os, sys, getopt
import termios
import signal
try:
    from termcolor import colored
except:
    def colored(text, color=None, on_color=None, attrs=None):
        return text

TYPE_EQUAL = 'equal'
TYPE_BITOR = 'bitor'

py_magic = {
    'os': {
        'open': {
            'flags': 'O_APPEND O_ASYNC O_CREAT O_DIRECTORY O_DSYNC O_EXCL O_EXLOCK O_NDELAY O_NOCTTY O_NOFOLLOW O_NONBLOCK O_RDONLY O_RDWR O_SHLOCK O_SYNC O_TRUNC O_WRONLY'.split(' '),
            'type': TYPE_BITOR
        },
        'seek': {
            'flags': 'SEEK_SET SEEK_CUR SEEK_END'.split(' '),
            'type': TYPE_EQUAL
        }
    },
    'termios': {
        'iflags': {
            'flags': 'IGNBRK BRKINT IGNPAR PARMRK INPCK ISTRIP INLCR IGNCR ICRNL IUCLC IXON IXANY IXOFF IMAXBEL IUTF8'.split(' '),
            'type': TYPE_BITOR
        },
        'oflags': {
            'flags': 'OPOST OLCUC ONLCR OCRNL ONOCR ONLRET OFILL OFDEL NLDLY CRDLY TABDLY BSDLY VTDLY FFDLY'.split(' '),
            'type': TYPE_BITOR,
        },
        'cflags': {
            'flags': 'CBAUD CBAUDEX CSIZE CSTOPB CREAD PARENB PARODD HUPCL CLOCAL LOBLK CIBAUD CMSPAR CRTSCTS'.split(' '),
            'type': TYPE_BITOR,
        },
        'lflags': {
            'flags': 'ISIG ICANON XCASE ECHO ECHOE ECHOK ECHONL ECHOCTL ECHOPRT ECHOKE DEFECHO FLUSHO NOFLSH TOSTOP PENDIN IEXTEN'.split(' '),
            'type': TYPE_BITOR,
        }
    },
    'signal': {
        'flags': 'NSIG SIGABRT SIGALRM SIGBUS SIGCHLD SIGCONT SIGEMT SIGFPE SIGHUP SIGILL SIGINFO SIGINT SIGIO SIGIOT SIGKILL SIGPIPE SIGPROF SIGQUIT SIGSEGV SIGSTOP SIGSYS SIGTERM SIGTRAP SIGTSTP SIGTTIN SIGTTOU SIGURG SIGUSR1 SIGUSR2 SIGVTALRM SIGWINCH SIGXCPU SIGXFSZ SIG_DFL SIG_IGN'.split(' '),
        'type': TYPE_EQUAL
    },
    'mmap': {
        'access': {
            'flags': 'ACCESS_COPY ACCESS_READ ACCESS_WRITE'.split(' '),
            'type': TYPE_BITOR,
        },
        'prot': {
            'flags': 'PROT_EXEC PROT_READ PROT_WRITE'.split(' '),
            'type': TYPE_BITOR,
        },
        'flags': {
            'flags': 'MAP_ANON MAP_ANONYMOUS MAP_DENYWRITE MAP_EXECUTABLE MAP_PRIVATE MAP_SHARED'.split(' '),
            'type': TYPE_BITOR,
        }
    },
    'errno': {
        'flags': 'E2BIG EACCES EADDRINUSE EADDRNOTAVAIL EAFNOSUPPORT EAGAIN EALREADY EAUTH EBADARCH EBADEXEC EBADF EBADMACHO EBADMSG EBADRPC EBUSY ECANCELED ECHILD ECONNABORTED ECONNREFUSED ECONNRESET EDEADLK EDESTADDRREQ EDEVERR EDOM EDQUOT EEXIST EFAULT EFBIG EFTYPE EHOSTDOWN EHOSTUNREACH EIDRM EILSEQ EINPROGRESS EINTR EINVAL EIO EISCONN EISDIR ELOOP EMFILE EMLINK EMSGSIZE EMULTIHOP ENAMETOOLONG ENEEDAUTH ENETDOWN ENETRESET ENETUNREACH ENFILE ENOATTR ENOBUFS ENODATA ENODEV ENOENT ENOEXEC ENOLCK ENOLINK ENOMEM ENOMSG ENOPOLICY ENOPROTOOPT ENOSPC ENOSR ENOSTR ENOSYS ENOTBLK ENOTCONN ENOTDIR ENOTEMPTY ENOTRECOVERABLE ENOTSOCK ENOTSUP ENOTTY ENXIO EOPNOTSUPP EOVERFLOW EOWNERDEAD EPERM EPFNOSUPPORT EPIPE EPROCLIM EPROCUNAVAIL EPROGMISMATCH EPROGUNAVAIL EPROTO EPROTONOSUPPORT EPROTOTYPE EPWROFF ERANGE EREMOTE EROFS ERPCMISMATCH ESHLIBVERS ESHUTDOWN ESOCKTNOSUPPORT ESPIPE ESRCH ESTALE ETIME ETIMEDOUT ETOOMANYREFS ETXTBSY EUSERS EWOULDBLOCK EXDEV'.split(' '),
        'type': TYPE_EQUAL,
    }
}

magics = {
    'ascii': {
        'flags': [(0, 'nul'), (1, 'soh'), (2, 'stx'), (3, 'etx'), (4, 'eot'), (5, 'enq'), (6, 'ack'), (7, 'bel'), (8, 'bs'), (9, 'ht'), (10, 'nl'), (11, 'vt'), (12, 'np'), (13, 'carriage return'), (14, 'so'), (15, 'si'), (16, 'dle'), (17, 'dc1'), (18, 'dc2'), (19, 'dc3'), (20, 'dc4'), (21, 'nak'), (22, 'syn'), (23, 'etb'), (24, 'can'), (25, 'em'), (26, 'sub'), (27, 'esc'), (28, 'fs'), (29, 'gs'), (30, 'rs'), (31, 'us'), (32, 'space'), (127, 'delete')] + [(x, chr(x)) for x in range(33, 127)],
        'type': TYPE_EQUAL
    },
    'prctl': {
        'flags': [(23, 'PR_CAPBSET_READ'),  (24, 'PR_CAPBSET_DROP'),  (36, 'PR_SET_CHILD_SUBREAPER'),  (37, 'PR_GET_CHILD_SUBREAPER'),  (4, 'PR_SET_DUMPABLE'),  (3, 'PR_GET_DUMPABLE'),  (20, 'PR_SET_ENDIAN'),  (19, 'PR_GET_ENDIAN'),  (10, 'PR_SET_FPEMU'),  (9, 'PR_GET_FPEMU'),  (12, 'PR_SET_FPEXC'),  (11, 'PR_GET_FPEXC'),  (8, 'PR_SET_KEEPCAPS'),  (7, 'PR_GET_KEEPCAPS'),  (15, 'PR_SET_NAME'),  (16, 'PR_GET_NAME'),  (38, 'PR_SET_NO_NEW_PRIVS'),  (39, 'PR_GET_NO_NEW_PRIVS'),  (1, 'PR_SET_PDEATHSIG'),  (2, 'PR_GET_PDEATHSIG'),  (1499557217, 'PR_SET_PTRACER'),  (22, 'PR_SET_SECCOMP'),  (21, 'PR_GET_SECCOMP'),  (28, 'PR_SET_SECUREBITS'),  (27, 'PR_GET_SECUREBITS'),  (40, 'PR_GET_TID_ADDRESS'),  (29, 'PR_SET_TIMERSLACK'),  (30, 'PR_GET_TIMERSLACK'),  (14, 'PR_SET_TIMING'),  (13, 'PR_GET_TIMING'),  (31, 'PR_TASK_PERF_EVENTS_DISABLE'),  (32, 'PR_TASK_PERF_EVENTS_ENABLE'),  (26, 'PR_SET_TSC'),  (25, 'PR_GET_TSC'),  (6, 'PR_SET_UNALIGN'),  (5, 'PR_GET_UNALIGN'),  (33, 'PR_MCE_KILL'),  (34, 'PR_MCE_KILL_GET'),  (35, 'PR_SET_MM')],
        'type': TYPE_EQUAL
    },
    'ptrace': {
        'flags': [(0, 'PTRACE_TRACEME'), (1, 'PTRACE_PEEKTEXT'), (2, 'PTRACE_PEEKDATA'), (3, 'PTRACE_PEEKUSER'), (4, 'PTRACE_POKETEXT'), (5, 'PTRACE_POKEDATA'), (6, 'PTRACE_POKEUSER'), (12, 'PTRACE_GETREGS'), (14, 'PTRACE_GETFPREGS'), (16900, 'PTRACE_GETREGSET'), (16898, 'PTRACE_GETSIGINFO'), (13, 'PTRACE_SETREGS'), (15, 'PTRACE_SETFPREGS'), (16901, 'PTRACE_SETREGSET'), (16899, 'PTRACE_SETSIGINFO'), (16896, 'PTRACE_SETOPTIONS'), (1048576, 'PTRACE_O_EXITKILL'), (8, 'PTRACE_O_TRACECLONE'), (16, 'PTRACE_O_TRACEEXEC'), (64, 'PTRACE_O_TRACEEXIT'), (2, 'PTRACE_O_TRACEFORK'), (1, 'PTRACE_O_TRACESYSGOOD'), (4, 'PTRACE_O_TRACEVFORK'), (32, 'PTRACE_O_TRACEVFORKDONE'), (16897, 'PTRACE_GETEVENTMSG'), (7, 'PTRACE_CONT'), (24, 'PTRACE_SYSCALL'), (9, 'PTRACE_SINGLESTEP'), (16904, 'PTRACE_LISTEN'), (8, 'PTRACE_KILL'), (16903, 'PTRACE_INTERRUPT'), (16, 'PTRACE_ATTACH'), (16902, 'PTRACE_SEIZE'), (17, 'PTRACE_DETACH'), (31, 'PTRACE_SYSEMU'), (32, 'PTRACE_SYSEMU_SINGLESTEP')],
        'type': TYPE_EQUAL
    }
}

registry = {}

def register(*args, **kwargs):
    def decorator(func):
        def wrapper(*fargs, **fkwargs):
            return func(*fargs, **fkwargs)
        wrapper.func_name = func.func_name
        wrapper.__doc__ == func.__doc__
        if not args:
            registry[wrapper.func_name] = wrapper
        else:
            for k in args:
                registry[wrapper.func_name + '.' + k] = wrapper
    return decorator

def FIND(key, hint): return key.lower().find(hint.lower()) > -1

def magic(query, hints, match = FIND):
    ret = {}

    def match_all(keyword):
        if isinstance(hints, basestring):
            return match(keyword, hints)
        for hint in hints:
            if not match(keyword, hint):
                return False
        return True

    name = None
    number = None

    if isinstance(query, basestring):
        if query.startswith('0x'):
            try:
                number = int(query, 16)
            except:
                raise ValueError('bad magic number in hex')
        elif query.startswith('0b'):
            try:
                number = int(sys.argv[1], 2)
            except:
                raise ValueError('bad magic number in bin')
        else:
            try:
                number = int(query, 10)
            except:
                number = None
                name = query
    elif isinstance(query, (int, long)):
        number = query
    else:
        raise ValueError('query should be type number or string')

    # py magics
    modules = {}
    for module in py_magic:
        if module not in modules:
            modules[module] = __import__(module, globals())

        def visit(obj, path):
            if 'flags' in obj and 'type' in obj:
                if not match_all(path): return
                if obj['type'] == TYPE_EQUAL:
                    bits = {}
                    for f in obj['flags']:
                        try:
                            value = getattr(modules[module], f)
                            if name:
                                if match(f, name):
                                    bits[f] = value
                            elif value == number:
                                bits[f] = number
                        except: pass
                    if bits:
                        ret[path] = bits
                elif obj['type'] == TYPE_BITOR:
                    bits = {}
                    for f in obj['flags']:
                        try:
                            value = getattr(modules[module], f)
                            if name:
                                if match(f, name):
                                    bits[f] = value
                            elif value & number:
                                bits[f] = value
                        except: pass
                    if bits:
                        # bits.sort()
                        ret[path] = bits
            else:
                for k in obj:
                    visit(obj[k], path + '.' + k)
        
        visit(py_magic[module], module)

    # magics

    for key in magics:
        if not match_all(key):
            continue
        if magics[key]['type'] == TYPE_EQUAL:
            bits = {}
            for n, s in magics[key]['flags']:
                if name:
                    if match(s, name):
                        bits[s] = n
                elif n == number:
                    bits[s] = n
            if bits:
                ret[key] = bits
        elif magics[key]['type'] == TYPE_BITOR:
            bits = {}
            for n, s in magics[key]['flags']:
                if name:
                    if match(s, name):
                        bits[s] = n
                elif n & number:
                    bits[s] = n
            if bits:
                # bits.sort()
                ret[key] = bits
                
    return ret

def usage():
    print """
usage:
    $ magic.py (number|name) [keyword | [keyword] ...]

examples:
    $ magic.py 11 open
    $ magic.py 15 signal
    $ magic.py 10240 iflags
    $ magic.py SIGTERM signal
    $ magic.py creat open
"""
    
def main():
    number = 0
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    try:
        rs = magic(sys.argv[1], sys.argv[2:])
    except BaseException, ex:
        usage()
        sys.exit(10)
    if not rs:
        print '0ops, magic number not found :('
        return 0
    for k in rs:
        w = rs[k]
        sys.stdout.write(colored(k, 'yellow') + '\r\n')
        sys.stdout.write('    ' + colored(isinstance(w, (list, dict)) and ' | '.join(['%s = %d(0x%s)' % (k, w[k], format(w[k], 'x')) for k in w.keys()]) or ', '.join(w), 'cyan') + '\r\n')
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main())

