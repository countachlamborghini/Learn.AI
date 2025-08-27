.PHONY: api web install-api dev-api dev-web web-install build-web

install-api:
	pip3 install --user -r services/api/requirements.txt --break-system-packages || pip3 install --user -r services/api/requirements.txt

dev-api:
	uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000

web-install:
	cd apps/web && npm install

dev-web:
	cd apps/web && npm run dev

build-web:
	cd apps/web && npm run build

