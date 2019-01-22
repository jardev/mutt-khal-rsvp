#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import glob
import sys
import psutil
import errno
from pathlib import Path
from getopt import gnu_getopt as getopt


if __name__ == '__main__':
    opts, args = getopt(sys.argv[1:], "d:")

    if len(args) < 1:
        print("Use: pid_account.py -d <pid-files-path> <config-file-name>")
        print("-d - Optional. By default $HOME/.config/mutt/pid_accounts")
        sys.exit(1)

    config = args[0]
    pid_path = os.path.join(str(Path.home()), '.config/mutt/pid_accounts')

    try:
        os.makedirs(pid_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(pid_path):
            pass
        else:
            raise

    for opt, arg in opts:
        if opt == '-d':
            pid_path = arg

    pid = os.getpid()
    mutt_pid = 0
    while pid:
        p = psutil.Process(pid)
        if p.name() == "neomutt" or p.name() == "mutt":
            mutt_pid = pid
            break
        pid = p.ppid()

    if not mutt_pid:
        print("No mutt/neomutt found in the running processes")
        sys.exit(1)

    # Write to PID-file related config
    with open(os.path.join(
        pid_path, "muttcfg_{}".format(mutt_pid)), "w") as f:
        f.write(config)
    # Just in case save one global to start with next time
    with open(os.path.join(pid_path, "muttcfg"), "w") as f:
        f.write(config)

    # Now go through the list of other pid files and clean them
    for fname in glob.glob(os.path.join(pid_path, "muttcfg_*")):
        pid = int(os.path.basename(fname).split("_")[1])
        try:
            p = psutil.Process(pid)
            if p.name() != 'neomutt' and p.name() != 'mutt':
                os.remove(fname)
        except:
            os.remove(fname)
