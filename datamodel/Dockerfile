FROM openjdk:8u121-jdk-alpine

WORKDIR /app

RUN apk --update --no-cache add graphviz ttf-dejavu && \
    apk --update --no-cache add git tree

COPY . .

ENTRYPOINT [ "ash", "entrypoint.sh" ]
