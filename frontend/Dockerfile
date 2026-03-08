FROM ghcr.io/cirruslabs/flutter:stable AS dev

WORKDIR /app

COPY pubspec.yaml pubspec.lock* ./
RUN flutter pub get

COPY . .

EXPOSE 5173

CMD ["flutter", "run", "-d", "web-server", "--web-port=5173", "--web-hostname=0.0.0.0"]

FROM dev AS build
RUN flutter build web --release

FROM nginx:alpine AS prod
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 80
