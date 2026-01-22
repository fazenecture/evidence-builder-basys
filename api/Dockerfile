FROM node:20-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY tsconfig.json ./
COPY src ./src

# Build TypeScript → JS
RUN yarn build

ENV NODE_ENV=production

CMD ["yarn", "start"]
