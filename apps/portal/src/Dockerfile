FROM hugomods/hugo:reg-0.147.0 AS builder
WORKDIR /site
COPY . .
RUN hugo --minify

FROM nginx:alpine
COPY --from=builder /site/public /usr/share/nginx/html
