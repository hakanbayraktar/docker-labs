FROM nginx:1.27-alpine

# Derleme sırasında verilen sürüm numarası sayfaya yazılır
ARG APP_VERSION=1.0.0

COPY index.html /usr/share/nginx/html/index.html
RUN sed -i "s/__VERSION__/${APP_VERSION}/" /usr/share/nginx/html/index.html
