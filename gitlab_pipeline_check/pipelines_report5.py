import gitlab
import pandas as pd

def process_pipelines(project_id):
    pipeline_ids = get_pipeline_ids()

    pipeline_statuses = []
    failed_jobs = []

    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)

    for pipeline_id in pipeline_ids:
        pipeline = project.pipelines.get(pipeline_id)
        pipeline_name = pipeline.name
        pipeline_status = pipeline.status
        job_ids = []
        job_names = []
        job_logs = []

        for job in pipeline.jobs.list():
            job_ids.append(job.id)
            job_names.append(job.name)
            job_logs.append(get_failed_job_logs(job))

        if pipeline_status == 'success':
            pipeline_statuses.append({'Pipeline ID': pipeline_id, 'Status': 'OK'})
            failed_jobs.append({
                'Pipeline ID': pipeline_id,
                'Pipeline Name': pipeline_name,
                'Jobs Names': 'N/A',
                'Jobs IDs': 'N/A',
                'Job Logs': 'N/A'
            })
        elif pipeline_status == 'failed':
            failed_jobs.append({
                'Pipeline ID': pipeline_id,
                'Pipeline Name': pipeline_name,
                'Jobs Names': job_names,
                'Jobs IDs': job_ids,
                'Job Logs': job_logs
            })

    generate_report(pipeline_statuses, failed_jobs)

def generate_report(pipeline_statuses, failed_jobs):
    report_data = []

    for pipeline_id, status in pipeline_statuses.items():
        report_data.append({'Pipeline ID': pipeline_id, 'Status': status})

    for job_id, job_data in failed_jobs.items():
        report_data.append({'Failed Job ID': job_id, 'Job Name': job_data['name'], 'Job Logs': job_data['logs']})

    for pipeline_id in successful_pipelines:
        report_data.append({'Pipeline ID': pipeline_id, 'Status': 'success'})

    df = pd.DataFrame(report_data)

    def color_cells(val):
        color = 'red' if val == 'failed' else 'green'
        return f'background-color: {color}'

    styled_df = df.style.applymap(color_cells, subset=['Status'])

    report_html = styled_df.to_html(escape=False)

    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f'pipeline_report_{now}.html'

    with open(filename, 'w') as file:
        file.write(report_html)

    print(f'Pipeline report generated: {filename}')
