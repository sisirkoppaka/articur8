#!/bin/bash
#Updates local code from git by pulling, and fab kickrestarts

git pull
fab kickrestart:debug=True