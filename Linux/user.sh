sed -i '1d' ../main_site/script.js && sed -i "1 i\var domain='$1'" ../main_site/script.js
cd ../main_site/ && sudo python3 -m http.server 80
