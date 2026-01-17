-- ✅ ТОЛЬКО тестовые данные (SQLAlchemy создает структуру)
INSERT INTO devices (name, type, location, status, mac_address, user_id) VALUES
('Living Room Temperature Sensor', 'temperature_sensor', 'Living Room', 'online', '13:37:20:79:05:A3', 1),
('Kitchen Temperature Sensor', 'temperature_sensor', 'Kitchen', 'online', '13:37:E7:6A:B7:C7', 1),
('Front Door Smart Lock', 'unknown', 'Entrance', 'online', '13:37:1A:A5:82:16', 1),
('Bedroom Motion Sensor', 'motion_sensor', 'Bedroom', 'online', '13:37:AB:CD:EF:01', 1),
('Garage Humidity Sensor', 'humidity_sensor', 'Garage', 'offline', '13:37:DE:AD:BE:EF', 2)
ON CONFLICT (mac_address) DO NOTHING;