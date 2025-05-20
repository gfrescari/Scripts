#!/usr/bin/bash
array=($(inxi -B))
battery=$(echo ${array[6]} | sed "s/[(.%)]//g")
echo ${array[6]}
if [ $(($battery)) -lt  400 ]; 
    then 
        echo "Low Battery" 
        paplay /usr/share/sounds/freedesktop/stereo/complete.oga
        paplay /usr/share/sounds/freedesktop/stereo/complete.oga
        paplay /usr/share/sounds/freedesktop/stereo/complete.oga
    else
        echo "Battery Good or Charging"
fi
