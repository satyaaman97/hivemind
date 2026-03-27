# hivemind-web

This is the React front-end part of the project.

## Local Usage

[Install docker](https://docs.docker.com/get-docker/) and build the Docker image:
```sh
sudo docker build . -t hivemind-web
```

Then run the container with:
```sh
sudo docker run -it --rm \
    -v ${PWD}:/src \
    -v /src/node_modules \
    -p 80:3000 \
    -e CHOKIDAR_USEPOLLING=true \
    hivemind-web
```

Visit: http://localhost/

## Cloud Usage

An `app.yaml` is included for running this with Google Cloud.
