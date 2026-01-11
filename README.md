# Проект "Тёплый дом"
Это шаблон для решения проектной работы. Структура этого файла повторяет структуру заданий. Я заполняю его по мере работы над решением.

# Задание 1. Анализ и планирование


### 1. Описание функциональности монолитного приложения

**Особенности системы**
- Каждая установка сопровождается выездом специалиста по подключению системы отопления в доме к текущей версии системы.
- Всё синхронно. Никаких асинхронных вызовов, микросервисов и реактивного взаимодействия в системе нет.
- Всё управление идёт от сервера к датчику.
- Самостоятельно подключить свой датчик к системе пользователь не может.

**Управление отоплением:**
- Нынешнее приложение компании позволяет управлять отоплением в доме.
- Данные о температуре получаются через запрос от сервера к датчику.

**Мониторинг температуры:**
- Нынешнее приложение компании позволяет проверять температуру.

### 2. Анализ архитектуры монолитного приложения

- Язык программирования: Go
- База данных: PostgreSQL
- Архитектура: Монолитная, все компоненты системы (обработка запросов, бизнес-логика, работа с данными) находятся в рамках одного приложения.
- Взаимодействие: Синхронное, запросы обрабатываются последовательно.
- Масштабируемость: Ограничена, так как монолит сложно масштабировать по частям.
- Развертывание: Требует остановки всего приложения.

### 3. Определение доменов и границы контекстов

Домен управления устройствами (Device Management)
- Контроль системы отопления (включение и отключение)
- Работа с температурными датчиками
- Взаимодействие с исполнительными реле управления

Домен управления пользователями (User Management)
- Авторизация и аутентифиация пользователей
- Настройка прав доступа к оборудованию
- Связь учетных записей пользователей с конкретными домами и устройствами

Домен мониторинга и аналитики (Monitoring & Analytics)
- Регистрация и хранение показаний температуры
- Отслеживание текущего статуса оборудования
- Предоставление собранных данных для интерфейсов и отчетов

Домен интеграции и коммуникации (Integration & Communications)
- Настройка протоколов обмена данными с устройствами
- Предоставление API для взаимодействия с внешними сервисами
- Обработка входящих команд и формирование ответов устройств

### **4. Проблемы монолитного решения**

- Единая точка отказа
- Невозможность независимого масштабирования компонентов
- Сложность изменений и обслуживания
- Синхронные блокировки
- Сложно добавлять новые устройства

### 5. Визуализация контекста системы — диаграмма С4

[Диаграмма контекста системы "Тёплый дом" в C4 нотации](./schemas/img/1_context_diagram_c4.png)

# Задание 2. Проектирование микросервисной архитектуры

**Диаграмма контейнеров (Containers)**

[Диаграмма контейнеров системы "Тёплый дом" в C4 нотации](./schemas/img/3_container_diagram_c4.png)

**Диаграмма компонентов (Components)**

[Диаграмма компонентов системы "Тёплый дом" в C4 нотации](./schemas/img/4_components_diagram_c4.png)

**Диаграмма кода (Code)**

[Диаграмма кода системы "Тёплый дом" в C4 нотации](./schemas/img/5_code_diagram_c4.png)

# Задание 3. Разработка ER-диаграммы

[ER диаграмма "Тёплый дом"](./schemas/img/6_er_diagramm_all.png)

# Задание 4. Создание и документирование API

### 1. Тип API

**Для синхронного обмена данными микросервисов по протоколам HTTP/HTTPS будет использоваться REST API. Причины:**
- Операции создания, чтения, обновления и удаления для работы с объектами
- Легкость подключения веб-приложений
- Универсальные коды откликов HTTP
- Формат передачи данных JSON

### 2. Документация API

- [Документация API для сервиса smart_home (MONOLIT)](./apps/smart_home/api_doc/swagger.txt)
- [Документация API для сервиса gateway_api](./apps/gateway_api/api_doc/swagger.txt)
- [Документация API для сервиса temperature_api](./apps/temperature_api/api_doc/swagger.txt)
- [Документация API для сервиса device_service](./apps/device_service/api_doc/swagger.txt)

# Задание 5. Работа с docker и docker-compose

- Реализован сервис *temperature_api*
Запускается на порту 8081
```
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8081
CMD ["python", "main.py"]
```
- Сервис добавлен в docker-compose файл
```
temperature-api:
  build: ./temperature_api
  container_name: temperature-api
  ports:
    - "8081:8081"
  depends_on:
    postgres:
      condition: service_healthy
```


# **Задание 6. Разработка MVP**

Необходимо создать новые микросервисы и обеспечить их интеграции с существующим монолитом для плавного перехода к микросервисной архитектуре. 

### **Что было сделано**

1. Созданы новые микросервисы API_GATEWAY (для проксирования запросов к микросевисам) и DEVICE_SERVICE (для управления устройствами) с простейшей логикой.

```
  # API Gateway
  api-gateway:
    build:
      context: ./gateway_api
      dockerfile: Dockerfile
    container_name: api-gateway
    environment:
      - SMART_HOME_URL=http://smarthome-app:8080
      - DEVICE_SERVICE_URL=http://device-service:8082
    depends_on:
      - app
    ports:
      - "8000:8000"
    restart: unless-stopped
    networks:
      - smarthome-network

  # Device Service
  device-service:
    build:
      context: ./device_service
      dockerfile: Dockerfile
    ports:
      - "8082:8082"
    environment:
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=smarthome_devices
      - DATABASE_USER=postgres
      - DATABASE_PASSWORD=postgres
      - KAFKA_BROKERS=kafka:9092
    volumes:
      - ./device_service/init.sql:/app/init.sql:ro
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
      zookeeper:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    restart: unless-stopped
    networks:
      - smarthome-network
```

А также предварительно заложена возможность взаимодействия с Apache Kafka и ZooKeeper (добавлены контейнеры в docker-compose и заложена минимальная логика для взаимодействия DEVICE_SERVICE с ними).

В результате созданы Dockerfiles для каждого микросервиса и docker-compose для их запуска.
Проверить работоспособность api каждого микросервиса можно с помощью curl запросов:
- [CURL запросы для smart_home (MONOLIT)](./apps/smart_home/api_doc/curl.txt)
- [CURL запросы для gateway_api](./apps/gateway_api/api_doc/curl.txt)
- [CURL запросы для temperature_api](./apps/temperature_api/api_doc/curl.txt)
- [CURL запросы для device_service](./apps/device_service/api_doc/curl.txt)