#!/usr/bin/env python3
import os
import sys
import datetime
import argparse

def get_cmd_param():
    parser = argparse.ArgumentParser()
    parser.add_argument("proj_name", type=str)
    return parser.parse_args()


def main():
    opts = get_cmd_param()
    cur_dir = os.getcwd()
    this_year = datetime.datetime.now().year
    proj_home = os.path.abspath(os.path.join(os.path.expanduser("~"), "Projects"))
    proj_home = os.path.join(proj_home, str(this_year))
    if not os.path.exists(proj_home):
        os.mkdir(proj_home)
    target_dir = os.path.join(proj_home, opts.proj_name)
    if os.path.exists(target_dir):
        print("target %s already exists" % opts.proj_name)
        return
    os.mkdir(target_dir)
    slink_target = os.path.join(cur_dir, opts.proj_name)
    if os.path.exists(slink_target):
        print("can't create symbol link, target already exists")
        return
    os.symlink(target_dir, slink_target)


if __name__ == "__main__":
    main()

