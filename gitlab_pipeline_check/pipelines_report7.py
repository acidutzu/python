import gitlab

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = 99988

def get_pipeline_ids(project_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    pipelines = project.pipelines.list()
    
    pipeline_ids = []
    for pipeline in pipelines:
        if pipeline.name in ["AAA", "BBB"]:
            pipeline_ids.append(pipeline.id)
    
    return pipeline_ids

def get_job_details(pipeline_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    pipeline = project.pipelines.get(pipeline_id)
    jobs = pipeline.jobs.list()

    job_details = [{'Job ID': job.id, 'Job Name': job.name} for job in jobs]
    return job_details

def get_job_logs(job_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(job_id)
    job_trace = job.trace()

    return job_trace

def process_pipelines(project_id):
    pipeline_ids = get_pipeline_ids(project_id)

    for pipeline_id in pipeline_ids:
        job_details = get_job_details(pipeline_id)
        
        for job in job_details:
            job_id = job['Job ID']
            job_name = job['Job Name']
            job_logs = get_job_logs(job_id)
            
            if 'THIS' in job_logs or 'THAT' in job_logs:
                log_start = job_logs.find('THIS') - 10
                log_end = job_logs.find('THAT') + 10
                captured_log = job_logs[log_start:log_end]
                print(f"Job ID: {job_id}, Job Name: {job_name}, Captured Log: {captured_log}")

process_pipelines(project_id)
