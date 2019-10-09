# First stage, build the frontend
FROM node:10.16.3

RUN npm config set registry https://registry.npm.taobao.org

ENV FRONTEND=/opt/frontend
ENV BACKEND=/opt/backend

WORKDIR $FRONTEND

COPY frontend/package.json $FRONTEND
COPY frontend/package-lock.json $FRONTEND
RUN npm install

COPY frontend/ $FRONTEND
RUN npm run build
COPY backend/ $BACKEND
RUN npm run apidocs

# Second stage for nginx
FROM elice/python-nginx:3.7

ENV HOME=/opt/backend

WORKDIR $HOME

# Copy frontend from the first stage
COPY --from=0 /opt/frontend/dist /opt/frontend/dist
COPY --from=0 /opt/apidocs /opt/apidocs
COPY nginx/ nginx/

RUN rm -r /etc/nginx/conf.d \
 && ln -s $HOME/nginx /etc/nginx/conf.d \
 && ln -sf /dev/stdout /var/log/nginx/access.log \
 && ln -sf /dev/stderr /var/log/nginx/error.log

COPY backend/requirements.txt $HOME
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY backend/ $HOME
COPY config/ $HOME

EXPOSE 80

ENV PYTHONUNBUFFERED=true
CMD ["/bin/sh", "run.sh"]
