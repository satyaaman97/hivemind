from node:12-alpine

WORKDIR /src

COPY package.json /src/
COPY package-lock.json /src/

RUN npm install

ADD . /src

EXPOSE 3000

CMD npm start
