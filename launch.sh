#!/bin/bash
ACTION='\033[1;90m  '
FINISHED='\033[1;96m  '
READY='\033[1;92m  '
NOCOLOR='\033[0m  ' # No Color
ERROR='\033[0;31m  '

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
pip -q install -r requirements.txt

echo -e ${ACTION} "Checking if .env exists..."
if [ ! -e .env ]
then
  echo -e ${ERROR} # transition to error mode
  read -p " .env doesn't exist! Do you want to create it? (Y/N) " var
  if [ ${var,,} == "y" ]
  then
    echo -e ${ACTION} "Creating template .env file..."
    echo -e "#Put your token bruh...\nDISCORD_TOKEN=put your token here" > .env
    nano .env 2>/dev/null
    echo -e ${ACTION} "Token added to environemnt config."
  fi
fi

echo -e ${FINISHED} "Everything is updated.\n"${READY} "Ready to run! Running..."

python main.py
