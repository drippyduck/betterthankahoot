#!/bin/bash

sed -i '1d' ../main_site/script.js
sed -i "1 i\var domain='$1'" ../main_site/script.js
