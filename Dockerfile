FROM ubuntu:latest
LABEL authors="djapy"

ENTRYPOINT ["top", "-b"]