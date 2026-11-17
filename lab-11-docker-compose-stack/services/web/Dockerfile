FROM nginx:1.27-alpine

# Nginx ayarı: index.html'i sunar, /api/ isteklerini api servisine iletir
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
