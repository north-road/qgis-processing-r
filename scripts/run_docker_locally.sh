DOCKER_IMAGE=qgis/qgis
DOCKER_IMAGE_TAG=latest
CONTAINER_NAME=qgis-testing-environment
PYTHON_SETUP="PYTHONPATH=/usr/share/qgis/python/:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages/qgis:/usr/share/qgis/python/qgis:/tests_directory"


if [ ! "$(docker ps -a | grep $CONTAINER_NAME)" ]; then
    echo "CONTAINER NOT FOUND CREATING!"

    docker pull "$DOCKER_IMAGE":$DOCKER_IMAGE_TAG
    docker run -d --name $CONTAINER_NAME -v .:/tests_directory -e DISPLAY=:99 "$DOCKER_IMAGE":$DOCKER_IMAGE_TAG

    docker exec $CONTAINER_NAME sh -c "pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt"
    docker exec $CONTAINER_NAME sh -c "apt-get update"
    docker exec $CONTAINER_NAME sh -c "apt-get install -y r-base"
else
    echo "CONTAINER FOUND, STARTING"
    docker start $CONTAINER_NAME
fi

docker exec $CONTAINER_NAME sh -c "$PYTHON_SETUP && cd tests_directory && pytest tests --cov=processing_r --cov-report=term-missing:skip-covered -rP -vv -s"

docker stop $CONTAINER_NAME
echo "CONTAINER STOPPED"