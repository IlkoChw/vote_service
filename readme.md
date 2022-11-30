<h2>Система голосований с храниением в redis</h2>

<h3>Сборка и запуск контейнеров:</h3>
docker-compose up --build -d

<h3>Запуск сценария голосования со случайным распределением голосов:</h3>
docker-compose run --rm votes python main.py
