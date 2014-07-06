#!/usr/bin/env bash

# Simple script to retrieve all TODOs in the application and gather them in TODO.txt
grep -rn TODO . | sed 's/  */ /' | grep -v jquery-ui | grep -v $0 | tee TODO.txt
