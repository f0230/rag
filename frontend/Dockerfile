FROM node:18-alpine

WORKDIR /app

# Copiar los archivos de package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# (Opcional) Instalar Next.js globalmente
RUN npm install -g next

# Copiar el resto de archivos
COPY . .

# Exponer el puerto
EXPOSE 3000

# Ejecutar la aplicación
CMD ["npx", "next", "dev"]
