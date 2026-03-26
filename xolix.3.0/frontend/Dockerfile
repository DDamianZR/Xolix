# Etapa 1: Construcción de React con Vite
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Etapa 2: Servidor Nginx
FROM nginx:alpine

# Copiar el build al directorio por defecto de nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar la configuración personalizada de nginx (para proxy y enrutamiento SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
