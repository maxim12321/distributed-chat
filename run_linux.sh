# $1 - BACK port, $2 - UI port

trap 'pkill -9 -f "python3 flask_main.py"' SIGINT

python3 flask_main.py "$1" "$2" &

cd mainapp-ui
echo "REACT_APP_BACKEND_PORT = $1" >".env.port$1"
BACK_PORT=".env.port$1" PORT="$2" BROWSER=none yarn start_linux
