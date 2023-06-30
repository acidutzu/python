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
    
    for pipeline_status in pipeline_statuses:
        report_data.append({'Pipeline ID': pipeline_status['Pipeline ID'], 'Status': pipeline_status['Status']})

    for failed_job in failed_jobs:
        report_data.append({
            'Pipeline ID': failed_job['Pipeline ID'],
            'Status': 'Failed',
            'Pipeline Name': failed_job['Pipeline Name'],
            'Job Names': failed_job['Jobs Names'],
            'Job IDs': failed_job['Jobs IDs'],
            'Job Logs': failed_job['Job Logs']
        })

    df = pd.DataFrame(report_data)

    # Create a styled DataFrame
    styled_df = df.style.applymap(lambda x: 'background-color: green' if x == 'OK' else 'background-color: red', subset=['Status'])

    # Generate HTML report
    now = pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')
    report_filename = f'pipeline_report_{now}.html'

    with open(report_filename, 'w') as file:
        file.write(styled_df.render())

    print(f"Pipeline report generated: {report_filename}")
