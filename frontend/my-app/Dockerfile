# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install project dependencies
RUN yarn install

# Bundle app source
COPY . .

# Build the React app
RUN yarn build

# Install serve to run the application
RUN yarn global add serve

# Serve the app on port 3000
CMD ["serve", "-s", "build", "-l", "3000", "--single"]

# Make port 3000 available to the world outside this container
EXPOSE 3000
