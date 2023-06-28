# Forex Data Pipeline

![Screenshot](img/pipeline.png)

## About the Docker Compose File. 

In the docker-compose file, each service is a cointainer that runs for the application. Each service is built based on a its Dockerfile. 

docker-compose.yml
```yaml
######################################################
# AIRFLOW
######################################################

  airflow:
    build: ./docker/airflow
    restart: always
    container_name: airflow
    volumes:
      - ./mnt/airflow/airflow.cfg:/opt/airflow/airflow.cfg
      - ./mnt/airflow/dags:/opt/airflow/dags
    ports:
      - 8080:8080
    healthcheck:
      test: [ "CMD", "nc", "-z", "airflow", "8080" ]
      timeout: 45s
      interval: 10s
      retries: 10
```
in the `volumes` parameter, we are saying that the dags created in <mark>/mnt/airflow/dags</mark> is binded with <mark>/opt/airflow/dags</mark> inside the docker container. So the files that we put in <mark>/mnt/airflow/dags</mark> in the local machine will be synchornized with the folder dags inside the Airflow docker container. This applies also with local <mark>/mnt/airflow/airflow.cfg</mark> and <mark>opt/airflow/airflow.cfg</mark> inside the container. 

