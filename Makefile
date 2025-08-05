.PHONY: up down build test clean

up:
	docker-compose up -d --build

down:
	docker-compose down

build:
	docker-compose build

test:
	curl -X POST "http://localhost:8000/predict" \
	-H "Content-Type: application/json" \
	-d '{"MedInc":8.3252,"HouseAge":41.0,"AveRooms":6.984127,"AveBedrms":1.023810,"Population":322.0,"AveOccup":2.555556,"Latitude":37.88,"Longitude":-122.23}'

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf mlflow/mlruns
