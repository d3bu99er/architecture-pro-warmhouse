#!/bin/bash

# Exit on any error
set -e

echo "Запускаю Smart Home Sensor API, Temperature API, API Gateway and Device Service..."
sleep 2
echo "Собираю и запускаю лучшие контейнеры в мире..."
sleep 2
docker compose up --build -d

echo "Все контейнеры подняты, сервисы на них запущены!"
echo "http://localhost:8000 for API-GATEWAY"
echo "http://localhost:8080 for MONOLIT-API"
echo "http://localhost:8081 for TEMPERATURE-API"
echo "http://localhost:8082 for DEVICE-SERVICE"
echo "http://localhost:2181 for ZOOKEEPER"
echo "http://localhost:9092 for KAFKA"
echo ""
echo ""
echo "Для проверки api-gateway используйте: curl -f http://localhost:8000/health"
echo "Для проверки smarthome-app используйте: curl -f http://localhost:8080/health"
echo "Для проверки temperature-api используйте: curl http://localhost:8081/health"
echo "Для проверки temperature-api используйте: curl http://localhost:8081/health"
echo "Для проверки device-service используйте: curl http://localhost:8081/health/ready"
echo ""
echo "Команда для просмотра логов: docker compose logs -f"
echo "Команда для остановки сервиса контейнеров: docker-compose down"
echo "Команда для переcборки контейнеров: docker compose down -v && docker compose up --build -d"
