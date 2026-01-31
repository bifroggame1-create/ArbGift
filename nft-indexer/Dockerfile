FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./
COPY tsconfig.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходники
COPY src ./src

# Билд TypeScript
RUN npm run build

# Expose API port
EXPOSE 3001

# Start command
CMD ["npm", "start"]
