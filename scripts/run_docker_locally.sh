DOCKER_IMAGE=qgis/qgis
DOCKER_IMAGE_TAG=latest
CONTAINER_NAME=qgis-testing-environment
PYTHON_SETUP="PYTHONPATH=/usr/share/qgis/python/:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages/qgis:/usr/share/qgis/python/qgis:/tests_directory"

if [ ! "$(docker ps -a | grep $CONTAINER_NAME)" ]; then
    echo "CONTAINER NOT FOUND CREATING!"

    docker pull "$DOCKER_IMAGE":$DOCKER_IMAGE_TAG
    docker run -d --name $CONTAINER_NAME -v .:/tests_directory -e DISPLAY=:99 "$DOCKER_IMAGE":$DOCKER_IMAGE_TAG

    docker exec $CONTAINER_NAME sh -c "pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt"
    docker exec $CONTAINER_NAME sh -c "apt-get update -qq"
    docker exec $CONTAINER_NAME sh -c "apt-get install --yes --no-install-recommends wget ca-certificates gnupg"

    docker exec $CONTAINER_NAME sh -c "wget -q -O- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc"
    docker exec $CONTAINER_NAME sh -c "echo \"deb [arch=amd64] https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/\" > /etc/apt/sources.list.d/cran_r.list"
    docker exec $CONTAINER_NAME sh -c "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 67C2D66C4B1D4339 51716619E084DAB9"

    docker exec $CONTAINER_NAME sh -c "wget -q -O- https://eddelbuettel.github.io/r2u/assets/dirk_eddelbuettel_key.asc | tee -a /etc/apt/trusted.gpg.d/cranapt_key.asc"
    docker exec $CONTAINER_NAME sh -c "echo \"deb [arch=amd64] https://r2u.stat.illinois.edu/ubuntu jammy main\" > /etc/apt/sources.list.d/cranapt.list"
    
    docker exec $CONTAINER_NAME sh -c "apt update -qq"

    docker exec $CONTAINER_NAME sh -c "apt-get install -y r-base r-cran-sf r-cran-raster"
else
    echo "CONTAINER FOUND, STARTING"
    docker start $CONTAINER_NAME
fi

docker exec $CONTAINER_NAME sh -c "$PYTHON_SETUP && cd tests_directory && pytest tests --cov=processing_r --cov-report=term-missing:skip-covered -rP -vv -s"

docker stop $CONTAINER_NAME
echo "CONTAINER STOPPED"
