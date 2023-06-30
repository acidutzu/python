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
        elif pipeline_status == 'failed':
            failed_jobs.append({
                'Pipeline ID': pipeline_id,
                'Pipeline Name': pipeline_name,
                'Jobs Names': job_names,
                'Jobs IDs': job_ids,
                'Job Logs': job_logs
            })

    pipeline_statuses_df = pd.DataFrame(pipeline_statuses)

    failed_jobs_df = pd.DataFrame(failed_jobs)

    now = pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')
    pipeline_statuses_filename = f'pipeline_statuses_{now}.html'
    failed_jobs_filename = f'failed_jobs_{now}.html'

    pipeline_statuses_df.to_html(pipeline_statuses_filename, index=False)
    failed_jobs_df.to_html(failed_jobs_filename, index=False)

    print(f"Pipeline statuses saved to: {pipeline_statuses_filename}")
    print(f"Failed jobs saved to: {failed_jobs_filename}")
