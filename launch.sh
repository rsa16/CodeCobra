#!/bin/bash
ACTION='\033[1;90m'
FINISHED='\033[1;96m'
READY='\033[1;92m'
NOCOLOR='\033[0m' # No Color
ERROR='\033[0;31m'

echo
echo -e Checking Git repo
echo -e =======================
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "main" ]
then
  echo -e ${ERROR}"Not on main branch." ${NOCOLOR}
  echo -e ${ACTION}"Switching to main bran..." ${NOCOLOR}
  git checkout main
fi

echo -e ${ACTION} "Downloading latest commits and branches..." ${NOCOLOR}
git fetch
HEADHASH=$(git rev-parse HEAD)
UPSTREAMHASH=$(git rev-parse main@{upstream})

if [ "$HEADHASH" != "$UPSTREAMHASH" ]
then
  echo -e ${ACTION} "Not up to date. Updating..."
  git pull -q
fi
 
echo -e ${ACTION} "Installing and updating packages..."
pip3 -q install -r requirements.txt

echo -e ${FINISHED} "Everything is updated." ${READY} "Ready to run!"

python main.py
