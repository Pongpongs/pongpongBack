FROM nginx:latest

WORKDIR /app

COPY nginx.conf /etc/nginx/nginx.conf

COPY ./certs ./certs

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
