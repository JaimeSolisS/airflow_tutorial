# Notes

## Create a DAG
Whenever you create a DAG, there are a couple of things you always need to define.

1. Import the DAG object
2. Instantiate a the DAG object
3. Define a unique dag id
4. Define a start date
5. Define a scheduled interval
6. Define the catchup parameter

```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from datetime import datetime

with DAG('user_processing', start_date=datetime(2023,3,1), 
        schedule_interval='@daily', catchup=False) as dag:
```

## Create a Task
They are 2 steps that you will always do when you create a task:  
1. Import the operator
2. Define the task id

Remember, the task id must be unique across all tasks in the same DAG.

That being said, create the task create_table with:
```python

with DAG('user_processing', start_date=datetime(2023,3,1), 
        schedule_interval='@daily', catchup=False) as dag:
    
        create_table = PostgresOperator(
        task_id='create_table', #keep same name for variable and task ID
        postgres_conn_id='postgres', #Define this connection in Airflow UI
        sql='''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            );
        '''
        )
```

## When adding a new task to DAG, always test it

```bash
$ docker-compose ps
NAME                                 IMAGE                  COMMAND                  SERVICE             CREATED             STATUS                    PORTS
airflow_docker-airflow-scheduler-1   apache/airflow:2.3.4   "/usr/bin/dumb-init …"   airflow-scheduler   48 minutes ago      Up 35 minutes (healthy)   8080/tcp
airflow_docker-airflow-triggerer-1   apache/airflow:2.3.4   "/usr/bin/dumb-init …"   airflow-triggerer   48 minutes ago      Up 35 minutes (healthy)   8080/tcp
airflow_docker-airflow-webserver-1   apache/airflow:2.3.4   "/usr/bin/dumb-init …"   airflow-webserver   48 minutes ago      Up 35 minutes (healthy)   0.0.0.0:8080->8080/tcp
airflow_docker-postgres-1            postgres:13            "docker-entrypoint.s…"   postgres            49 minutes ago      Up 35 minutes (healthy)   5432/tcp

$ docker exec -it airflow_docker-airflow-scheduler-1 /bin/bash
airflow@8ac4beaf7e4c:/opt/airflow$ airflow tasks test user_processing create_table 2022-03-01
[2023-03-03 18:29:45,034] {base.py:68} INFO - Using connection ID 'postgres' for task execution.
[2023-03-03 18:29:45,043] {sql.py:315} INFO - Running statement: CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            ), parameters: None
[2023-03-03 18:29:45,336] {taskinstance.py:1412} INFO - Marking task as SUCCESS. dag_id=user_processing, task_id=create_table, execution_date=20220301T000000, start_date=, end_date=20230303T182945  
```

exit with Ctrl-d

## Ad a Sensor

A sensor is a special type of operator.
It waits for something to happen before executing the next task.

For example, if you want to wait for files, you can use the FileSensor.

If you want to wait for an entry in an S3 bucket, you can use the S3KeySensor.

## Implement a sensor for api 
```python
    is_api_available = HttpSensor(
            task_id='is_api_available', 
            http_conn_id='user_api', 
            endpoint='api/'    
        )
```

Create the connection user_api on UI
```
Name: user_api    
Connection type: HTTP  
Host: https://randomuser.me/
```

## Implement a task to extract users from api 
```python
    extract_user = SimpleHttpOperator(
            task_id='extract_user',
            http_conn_id='user_api',
            endpoint='api/',
            method='GET',
            response_filter=lambda response: json. loads(response. text),
            log_response=True
        )
```

## Python Operator 
The python operator allows you to execute a python function 

```python
def process_user_func(ti): #ti stands for task instance
    #we need this parameter to pull the data that has been downloaded by the task extract.
    user = ti.xcom_pull(task_ids="extract_user")
    user = user['results'][0]
    processed_user = pd.json_normalize({
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['name']['country'],
        'username': user['name']['username'],
        'password': user['name']['password'],
        'email': user['name']['email'],
    })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

with DAG('user_processing' ....
        
    ...
    ...
    ...

    process_user = PythonOperator(
        task_id = 'process_user', 
        python_callable= process_user_func
    )
```