sed -i '1d' ../admin/script.js && sed -i "1 i\var domain='$1'" ../admin/script.js
cd ../admin/ && python3 -m http.server 8888
