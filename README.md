# Django-Vue Project

## Note

This project is created with the following scripts.

```bash
npm config set registry https://registry.npm.taobao.org
npm install -g vue-cli
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple django
django-admin startproject api
mv api backend
vue init webpack frontend
```

## Getting Started

Install prerequisites

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
