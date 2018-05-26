#!/bin/bash
ps -ax | awk '$4 ~ /synergy-service/ {kill $1}'