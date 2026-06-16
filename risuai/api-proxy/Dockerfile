# syntax=docker/dockerfile:1

FROM node:26-slim AS deps
WORKDIR /app
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

COPY package.json pnpm-lock.yaml ./
RUN npm install --global pnpm@10.34.1
RUN --mount=type=cache,id=api-proxy-pnpm,target=/pnpm/store pnpm install --frozen-lockfile

FROM deps AS builder
COPY tsconfig.json ./
COPY src ./src
RUN pnpm build && pnpm prune --prod

FROM node:26-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

EXPOSE 8787

CMD ["node", "dist/index.js"]
