#!/usr/bin/env bash

pushd /home/pi/pictures/plantstalk

DATE=$(date +"%Y-%m-%d")

ffmpeg -f image2 -pattern_type glob -i 'plantstalk_*.jpg' -r 10 -c:v libx264 -pix_fmt yuv420p "${DATE}".mp4
if [ $? -ne 0 ]
then
  echo "Could not create Plantstalk timelapse video"
  exit 1
fi

python3 /home/pi/repos/plantstalk/video-uploader.py \
  --file /tmp/plantstalk/${DATE}.mp4 \
  --title ${DATE} \
  --description "Plantstalk Nachtsicht mit Raspberry Kamera -- ${DATE}"
if [ $? -ne 0 ]
then
  echo "Could not upload video to YouTube"
  exit 2
fi

rm -rf /home/pi/pictures/plantstalk/*

popd
