import argparse
import requests
import pandas as pd
from datetime import datetime
from gitlab import Gitlab

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'


def get_pipeline_ids():
    url = f"{gitlab_url}/api/v4/projects/{project_id}/pipeline_schedules"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schedules = response.json()
        pipeline_ids = [schedule['last_pipeline']['id'] for schedule in schedules]
        return pipeline_ids
    else:
        print(f"Failed to retrieve pipeline schedules. Error: {response.content}")
        return []


def get_failed_job_logs(job_id):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(job_id)
    job_trace = job.trace()
    return job_trace


def get_pipeline_details(pipeline_id):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    pipeline = project.pipelines.get(pipeline_id)

    pipeline_name = pipeline.name
    job_names = [job.name for job in pipeline.jobs.list()]
    job_ids = [job.id for job in pipeline.jobs.list()]

    job_logs = ""
    if pipeline.status == 'failed' and job_ids:
        job_logs = get_failed_job_logs(job_ids[0])

    return pipeline_name, job_names, job_ids, job_logs


def generate_report(report_data):
    df = pd.DataFrame(report_data)

    def color_cells(val):
        color = 'red' if val == 'failed' else 'green'
        return f'background-color: {color}'

    styled_df = df.style.applymap(color_cells, subset=['Status'])

    report_html = styled_df.render()

    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f'pipeline_report_{now}.html'

    with open(filename, 'w') as file:
        file.write(report_html)

    print(f'Pipeline report generated: {filename}')


def process_pipelines(project_id):
    pipeline_ids = get_pipeline_ids()

    pipeline_statuses = []
    failed_jobs = []
    successful_pipelines = []

    for pipeline_id in pipeline_ids:
        pipeline_name, job_names, job_ids, job_logs = get_pipeline_details(pipeline_id)

        if pipeline_name:
            pipeline_statuses.append({'Pipeline ID': pipeline_id, 'Pipeline Name': pipeline_name})

            if job_names and job_ids:
                pipeline_statuses[-1]['Jobs'] = ', '.join(job_names)
                pipeline_statuses[-1]['Job IDs'] = ', '.join(job_ids)

            if job_logs:
                failed_jobs.append({'Pipeline ID': pipeline_id, 'Failed Job Logs': job_logs})
            else:
                successful_pipelines.append(pipeline_id)

    generate_report(pipeline_statuses + failed_jobs + successful_pipelines)


def main():
    parser = argparse.ArgumentParser(description='Process pipeline IDs')
    parser.add_argument('project_id', type=int, help='Project ID')
    args = parser.parse_args()
    project_id = args.project_id

    process_pipelines(project_id)


if __name__ == '__main__':
    main()
