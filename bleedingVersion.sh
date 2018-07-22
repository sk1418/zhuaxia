#!/bin/bash

printf "version='r%s.%s'\n" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)" > zhuaxia/zxver.py
