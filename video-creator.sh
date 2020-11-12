#!/usr/bin/env bash

pushd /home/pi/pictures/plantstalk

DATE=$(date +"%Y-%m-%d")

echo "Deleting old video..."
ls -la /home/pi/pictures/plantstalk/*.mp4
rm -rf /home/pi/pictures/plantstalk/*.mp4

ffmpeg -f image2 -pattern_type glob -i 'plantstalk_*.jpg' -r 10 -c:v libx264 -pix_fmt yuv420p "${DATE}".mp4
if [ $? -ne 0 ]
then
  echo "Could not create Plantstalk timelapse video"
  exit 1
fi

python3 /home/pi/repos/plantstalk/video-uploader.py \
  --file ./${DATE}.mp4 \
  --title ${DATE} \
  --description "Plantstalk Nachtsicht mit Raspberry Kamera -- ${DATE}" \
  --privacyStatus "public"
if [ $? -ne 0 ]
then
  echo "Could not upload video to YouTube"
  exit 2
fi

echo "Deleting pictures..."
ls -la /home/pi/pictures/plantstalk/*.jpg | wc -l
rm -rf /home/pi/pictures/plantstalk/*.jpg

popd
