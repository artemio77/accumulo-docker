from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from docker.types import Mount

# Define path to data
raw_data_path = "/opt/airflow/data/raw/data__{{ ds }}.csv"
pred_data_path = "/opt/airflow/data/predict/labels__{{ ds }}.json"
result_data_path = "/opt/airflow/data/predict/result__{{ ds }}.json"

# Define keyword arguments to use for all DockerOperator tasks
dockerops_kwargs = {
    "mount_tmp_dir": False,
    "mounts": [
        Mount(
            source="/Users/aderevets/IdeaProjects/grockstocks/code/ml/data",  # Change to your path
            target="/opt/airflow/data/",
            type="bind",
        )
    ],
    "retries": 1,
    "api_version": "1.30",
    "docker_url": "tcp://docker-socket-proxy:2375",
    "network_mode": "bridge",
}


# Create DAG
@dag("snp_500_report_analysis", start_date=days_ago(0), schedule="@daily", catchup=False)
def taskflow():
    # Task 1
    # TODO implement data loader for s&p 500 reports
    # Task 2
    report_summarization = DockerOperator(
        task_id="report_summarization",
        container_name="report_summarization",
        image="report-summarization:latest",
        command=f"python report_summary.py",
        **dockerops_kwargs,
    )

    # Task 3
    # TODO implement report results anywhere

    report_summarization


taskflow()
