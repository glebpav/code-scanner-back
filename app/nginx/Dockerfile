FROM nginx:stable

WORKDIR /workdir

COPY configs/default.conf /etc/nginx/conf.d/
COPY entrypoint.sh entrypoint.sh
RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]