#!/bin/bash
ps -ax | awk '$4 ~ /synergy-service/ {print $1}' | xargs kill -9
