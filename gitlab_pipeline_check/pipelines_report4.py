import argparse
import urllib.parse
import subprocess
import pandas as pd
from datetime import datetime
import requests

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = '<project_id>'
search_phrases = ['ABC', 'DFG', 'GHI']
strings_to_find = ['WHAT WHAT', 'WHERE WHERE']
characters_to_capture = 5


def get_failed_job_logs(job_id):
    url = f"{gitlab_url}/api/v4/projects/{project_id}/jobs/{job_id}/trace"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return ''


def capture_string(text, string_to_find):
    index = text.find(string_to_find)
    if index != -1:
        start_index = index + len(string_to_find)
        end_index = start_index + characters_to_capture
        return text[start_index:end_index]
    return ''



def get_pipeline_ids():
    pipeline_ids = []

    # Fetch pipeline schedules using GitLab API
    url = f"{gitlab_url}/api/v4/projects/{project_id}/pipeline_schedules"
    headers = {"PRIVATE-TOKEN": access_token}
    response = requests.get(url, headers=headers)
    schedules = response.json()

    for schedule in schedules:
        if schedule.get("description") in search_phrases:
            schedule_id = schedule.get("id")
            schedule_url = f"{url}/{schedule_id}"
            schedule_response = requests.get(schedule_url, headers=headers)
            schedule_data = schedule_response.json()
            pipeline_id = schedule_data.get("last_pipeline").get("id")
            pipeline_ids.append(pipeline_id)

    return pipeline_ids






def process_pipelines(project_id):
    pipeline_ids = get_pipeline_ids()

    pipeline_statuses = []
    failed_jobs = []

    for pipeline_id in pipeline_ids:
        url = f"{gitlab_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pipeline = response.json()
            pipeline_status = pipeline['status']
            if pipeline_status == 'success':
                pipeline_statuses.append({'Pipeline ID': pipeline_id, 'Status': 'OK'})
            elif pipeline_status == 'failed':
                job_id = pipeline['user']['id']
                job_name = pipeline['user']['name']
                job_logs = get_failed_job_logs(job_id)
                failed_jobs.append({'Pipeline ID': pipeline_id, 'Failed Job': job_name, 'Job Logs': job_logs})
        else:
            print(f"Failed to retrieve pipeline {pipeline_id}. Error: {response.content}")

    report_data = pd.DataFrame(pipeline_statuses + failed_jobs)
    report_data['Pipeline ID'] = report_data['Pipeline ID'].apply(lambda x: f'<a href="{gitlab_url}/{project_id}/pipelines/{x}">{x}</a>')

    for string_to_find in strings_to_find:
        report_data[string_to_find] = report_data['Job Logs'].apply(lambda x: capture_string(x, string_to_find))

    report_html = report_data.to_html(escape=False)

    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f'pipeline_report_{now}.html'

    with open(filename, 'w') as file:
        file.write(report_html)

    print(f'Pipeline report generated: {filename}')


def main():
    parser = argparse.ArgumentParser(description='Process pipeline schedules')
    parser.add_argument('project_id', type=int, help='Project ID')
    args = parser.parse_args()
    project_id = args.project_id

    process_pipelines(project_id)


if __name__ == '__main__':
    main()
