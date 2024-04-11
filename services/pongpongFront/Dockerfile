FROM node:14


WORKDIR /app
COPY package*.json ./

RUN npm install

COPY . .
COPY .env ./

EXPOSE 3000
CMD ["node", "app.js"]