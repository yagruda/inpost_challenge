FROM node:22-slim

WORKDIR /app

# Copy package.json and install
COPY package.json package-lock.json* ./
RUN npm install

# Copy application
COPY . .

# Expose port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
