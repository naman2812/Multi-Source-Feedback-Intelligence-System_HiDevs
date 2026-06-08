FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run the dev server. In a true prod env, we would build and serve via Nginx, 
# but for the dev docker-compose setup, we run Vite.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
