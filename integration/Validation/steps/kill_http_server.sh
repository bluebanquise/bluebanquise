kill -9 $(ps -ax | grep 'http.server 8000' | sed -n 1p | awk -F ' ' '{print $1}')
