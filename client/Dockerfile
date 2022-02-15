FROM node:14-alpine

RUN mkdir -p /home/app
WORKDIR /home/app

COPY package.json yarn.lock ./
RUN yarn install

COPY . .

EXPOSE 8080
CMD ["yarn", "serve"]
