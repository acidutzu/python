import argparse
import urllib.parse
import subprocess
import pandas as pd
from datetime import datetime
from gitlab import Gitlab

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = '<project_id>'
search_phrases = ["ABC", "DFG", "GHI"]


def get_failed_job_logs(failed_job):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(failed_job.id)
    job_trace = job.trace()
    return job_trace


def execute_script(pipeline_status, failed_job, pipeline_id):
    if pipeline_status == 'failed':
        print(f'Pipeline {pipeline_id} failed.')
        if failed_job:
            print(f'Failed Job: {failed_job.name}')
            logs = get_failed_job_logs(failed_job)

            now = datetime.now().strftime('%Y-%m-%d_%H-%M')
            filename = f'failed_job_{failed_job.id}_logs_{now}.txt'
            with open(filename, 'w') as file:
                file.write(logs)

            print(f'Failed job logs written to: {filename}')

        # Logic for failed pipelines here

    elif pipeline_status == 'success':
        print(f'Pipeline {pipeline_id} succeeded.')
        # Logic for success pipelines here

    else:
        print(f'Pipeline {pipeline_id} has an unknown status. Script execution skipped.')


def generate_report(pipeline_statuses, failed_jobs, successful_pipelines):
    report_data = []
    for pipeline_id, status in pipeline_statuses.items():
        if status == 'failed':
            report_data.append({'Pipeline ID': f'<a href="{gitlab_url}/{project_id}/pipelines/{pipeline_id}">{pipeline_id}</a>',
                               'Status': status})
        elif status == 'success':
            report_data.append({'Pipeline ID': f'<a href="{gitlab_url}/{project_id}/pipelines/{pipeline_id}">{pipeline_id}</a>',
                               'Status': status})

    for job_id, job_logs in failed_jobs.items():
        job_logs_urlencoded = urllib.parse.quote(job_logs)
        report_data.append({'Failed Job ID': f'<a href="{gitlab_url}/{project_id}/jobs/{job_id}">{job_id}</a>',
                            'Job Logs': f'<a href="data:text/plain;charset=utf-8,{job_logs_urlencoded}" '
                                        f'download="job_{job_id}_logs.txt">Download Logs</a>'})

    for pipeline_id in successful_pipelines:
        report_data.append({'Pipeline ID': f'<a href="{gitlab_url}/{project_id}/pipelines/{pipeline_id}">{pipeline_id}</a>',
                            'Status': 'success'})

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

def get_pipeline_ids():
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    schedules = project.schedules.list()

    pipeline_ids = []
    for schedule in schedules:
        if any(phrase in schedule.description for phrase in search_phrases):
            pipelines = schedule.pipelines.list()
            pipeline_ids.extend([pipeline.id for pipeline in pipelines])

    return pipeline_ids


def process_pipelines(pipeline_ids):
    pipeline_statuses = {}
    failed_jobs = {}

    for pipeline_id in pipeline_ids:
        pipeline_status, failed_job = get_pipeline_status(pipeline_id)
        execute_script(pipeline_status, failed_job, pipeline_id)
        pipeline_statuses[pipeline_id] = pipeline_status

        if failed_job:
            failed_jobs[failed_job.id] = get_failed_job_logs(failed_job)

    generate_report(pipeline_statuses, failed_jobs)


def main():
    parser = argparse.ArgumentParser(description='Process pipeline IDs')
    parser.add_argument('pipeline_ids', nargs='*', help='Pipeline IDs separated by space')
    args = parser.parse_args()
    pipeline_ids = args.pipeline_ids

    if not pipeline_ids:
        pipeline_ids = get_pipeline_ids()

    process_pipelines(pipeline_ids)


if __name__ == '__main__':
    main()

