FROM node:14-alpine
RUN apk add g++ make py3-pip
# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install app dependencies
COPY package.json /usr/src/app/
RUN npm install --prod

# Bundle app source
COPY . /usr/src/app

EXPOSE 5000
CMD [ "sh", "-c", "npm install && npm run start" ]
