# Cloud Scheduler

## Note

Deployment Environment:

```
node 10.16.3
npm 6.9.0
python 3.7.1
```

This project is created with the following scripts:

```bash
# frontend
npm config set registry https://registry.npm.taobao.org
npm install --global vue-cli
vue init webpack frontend
# backend
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple django
django-admin startproject api
mv api backend
```

## Getting Started

Install dependencies.

```bash
cd frontend
npm install
cd ../backend
pip install -r requirements.txt
```

Run backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Run frontend

```bash
cd frontend
npm run dev
```

## Unit Tests

Frontend

```bash
npm run unit
```

Backend

```bash
pytest
```

Note: if you encounter problems in frontend unit test, try

```bash
node node_modules/jest/bin/jest.js --clearCache
```

## Style Tests

Frontend

```bash
npm run lint
```

Backend

```bash
pylint --load-plugins=pylint_django api
```
