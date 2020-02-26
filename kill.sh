$PORT = $1
echo "Looking for a container on port: ${PORT}"

ID=$(\

docker container ls --format="{{.ID}}\t{{.Ports}}" |\
grep ${PORT} |\
awk '{print $1}')
echo "Found Container ID: ${ID}"
echo "Stopping and removing it"
docker container stop ${ID} && docker container rm ${ID}
