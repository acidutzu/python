import argparse
import urllib.parse
import subprocess
import pandas as pd
from datetime import datetime
from gitlab import Gitlab

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = '<project_id>'
search_phrases = ['ABC', 'DFG', 'GHI']
strings_to_find = ['WHAT WHAT', 'WHERE WHERE']
characters_to_capture = 5


def get_failed_job_logs(job_id):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(job_id)
    job_trace = job.trace()
    return job_trace


def capture_string(text, string_to_find):
    index = text.find(string_to_find)
    if index != -1:
        start_index = index + len(string_to_find)
        end_index = start_index + characters_to_capture
        return text[start_index:end_index]
    return ''


def process_pipelines(project_id):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    schedules = project.schedules.list(all=True)

    pipeline_statuses = []
    failed_jobs = []

    for schedule in schedules:
        if any(phrase in schedule.description for phrase in search_phrases):
            pipeline_id = schedule.last_pipeline['id']
            pipeline = project.pipelines.get(pipeline_id)

            if pipeline.status == 'success':
                pipeline_statuses.append({'Pipeline ID': pipeline_id, 'Status': 'OK'})
            elif pipeline.status == 'failed':
                failed_job = pipeline.jobs.list(failed=True).first()
                if failed_job:
                    job_id = failed_job.id
                    job_name = failed_job.name
                    job_logs = get_failed_job_logs(job_id)
                    failed_jobs.append({'Pipeline ID': pipeline_id, 'Failed Job': job_name, 'Job Logs': job_logs})

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
