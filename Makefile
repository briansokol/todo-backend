.PHONY: dev test migrate generate-schemas

dev:
	uvicorn main:app --reload --port 8000

test:
	pytest tests/ -v

migrate:
	alembic upgrade head

generate-schemas:
	@echo "Regenerate Pydantic schemas from openapi.yaml using datamodel-code-generator"
	@echo "Run: datamodel-codegen --input ../todo-contracts/openapi.yaml --output app/schemas/generated.py"
