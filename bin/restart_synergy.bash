#!/bin/bash
ps -ax | awk '$4 ~ /synergy-service/ {print $1; kill -9 $1}'
