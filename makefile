.PHONY: install etl backend frontend demo

install:
	pip install -r requirements.txt

etl:
	python -m app.etl

backend:
	uvicorn app.api:app --host 0.0.0.0 --port 8000

frontend:
	API_URL=http://127.0.0.1:8000 streamlit run dashboard/app.py --server.port=8501

demo:
	# naive, but good enough: backend in background, then frontend
	(uvicorn app.api:app --host 0.0.0.0 --port 8000 &) && \
	API_URL=http://127.0.0.1:8000 streamlit run dashboard/app.py --server.port=8501