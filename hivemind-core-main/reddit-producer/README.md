# reddit-producer

This part of the project gets comments from Reddit and adds them to a Mongo database
to be processed later.

## Local Usage

Rename the docker-compose .env so docker-compose will pick it up:

```sh
  cp .env.example .env
```

Fill in the `<fill in>` sections with the appropriate values.

[Install docker](https://docs.docker.com/get-docker/) and run:

```sh
docker-compose up
```

## Cloud Usage

A `cloudbuild.yaml` and `producer.yaml` is included for running this with Google Cloud.
