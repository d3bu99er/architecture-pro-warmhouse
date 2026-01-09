# Стадия сборки
FROM golang:1.22-alpine AS builder

# Установка рабочей директории
WORKDIR /app

# Копирование файлов go.mod и go.sum
COPY go.mod go.sum ./

# Скачивание зависимостей
RUN go mod download

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN CGO_ENABLED=0 GOOS=linux go build -o smarthome

# Стадия выполнения
FROM alpine:latest

# Установка необходимых зависимостей
RUN apk --no-cache add ca-certificates tzdata

# Установка рабочей директории
WORKDIR /app

# Копирование бинарного файла из стадии сборки
COPY --from=builder /app/smarthome .

# Открытие порта, на котором работает приложение
EXPOSE 8080

# Команда для запуска приложения
CMD ["./smarthome"]