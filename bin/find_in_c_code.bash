#!/bin/bash
find . -type f -name "*.cpp" -or -name "*.h" -or -name "*.cc" | xargs grep -n "$@"