#!/bin/bash

# change domain for script.js user

sed -i '1d' ../admin/script.js && sed -i "1 i\var domain='$1'" ../admin/script.js
sed -i '1d' ../main_site/script.js && sed -i "1 i\var domain='$1'" ../main_site/script.js

# change domain for script.js admin
# launch other scripts on seperate tabs with adr parameter
xterm -e "./api.sh $1" &
sleep 10
xterm -e "./socket.sh $1" &
xterm -e "./user.sh" &
xterm -e "./admin.sh" &

