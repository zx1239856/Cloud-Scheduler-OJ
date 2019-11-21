# Deploy Cloud Scheduler to Web

The backend server is based on Django, in which case you can start it up directly on port 8000 via `python manage.py runserver`.

!!! warning
    **DO NOT** serve backend server in this manner when you are in production environment.


## Load Initial Data
After you provided a valid `config.py`, you can migrate database and load initial data (a default super admin, with username and password both set to `admin`). The following commands may be used
```bash
python manage.py migrate
python manage.py loaddata database.json
```

## Build Frontend
The frontend is written in `Vue.js`. You need to compile them before deploying.
```bash
npm install yarn -g # install yarn for faster building
cd frontend
yarn install
yarn build
```
This will generate a `dist` folder in `frontend`, which can be served by Nginx later.

## Serve Backend in Production
The backend consists of `WSGI`(HTTP) and `ASGI`(WebSocket) parts, which should be served separately.
### Serve `WSGI`
This part is served by [gunicorn](https://gunicorn.org/), you can use this command
```bash
gunicorn api.wsgi -k gevent -b 0.0.0.0:8000 -D --access-logfile - --log-level info
```
If you prefer a configuration file, you can provide one. Please refer to [Gunicorn Docs](http://docs.gunicorn.org/en/stable/) for details.

### Serve `ASGI`
This part is served by [daphne](https://github.com/django/daphne), use this command
```bash
daphne api.asgi:application --bind 0.0.0.0 --port 8001
```

## Nginx Reverse Proxy
An nginx reverse proxy is recommended to add extra functionality, such as HTTPS and path rewrite. Here is an example configuration
```conf
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	root /opt/frontend/dist;   # path to frontend dist

	index index.html index.htm index.nginx-debian.html;

	server_name _;  # your server name

	location / {
		try_files $uri $uri/ /index.html;
	}

	location /api/ {  # api server
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
		proxy_set_header X-Forwarded-Proto $scheme;
		rewrite "^/api/(.*)$" /$1 break;
    	proxy_send_timeout 1h;
		client_max_body_size 4g;
    }

	location /ws/ {   # websocket server
		proxy_pass http://127.0.0.1:8001/;
		proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
		proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
		proxy_set_header X-Forwarded-Proto $scheme;
		rewrite "^/ws/(.*)$" /$1 break;
		proxy_connect_timeout 1d;
    	proxy_send_timeout 1d;
    	proxy_read_timeout 1d;
	}

	access_log /opt/nginx.access.log;
	error_log /opt/nginx.error.log;
}
```
You can access API server via `<base_url>/api/` and WebSocket server via `<base_url>/ws/`.