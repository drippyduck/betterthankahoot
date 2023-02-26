#!/bin/bash

# change domain for script.js user

# change domain for script.js admin
# launch other scripts on seperate tabs with adr parameter
xterm -e "./api.sh $1" &
sleep 10
xterm -e "./socket.sh $1" &
xterm -e "./user.sh $1" &
xterm -e "./admin.sh $1" &

