import gitlab
import argparse

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = '<project_id>'

def get_job_ids_and_names(pipeline_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    pipeline = project.pipelines.get(pipeline_id)
    
    jobs = pipeline.jobs.list()

    job_ids = []
    job_names = []

    for job in jobs:
        job_ids.append(job.id)
        job_names.append(job.name)

    return job_ids, job_names

def get_failed_job_logs(job_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(job_id)
    job_trace = job.trace()
    return job_trace

def process_pipeline(pipeline_id):
    gl = gitlab.Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    pipeline = project.pipelines.get(pipeline_id)
    
    if pipeline.status == 'success':
        print(f"Pipeline {pipeline.name} is OK")
    else:
        print(f"Pipeline {pipeline.name} failed.")
        job_ids, job_names = get_job_ids_and_names(pipeline_id)

        for job_id, job_name in zip(job_ids, job_names):
            job_logs = get_failed_job_logs(job_id)
            print(f"Logs for Failed Job '{job_name}' (ID: {job_id}):")
            print(job_logs)

def main():
    parser = argparse.ArgumentParser(description='Process pipeline IDs')
    parser.add_argument('pipeline_ids', nargs='+', help='Pipeline IDs separated by space')
    args = parser.parse_args()
    pipeline_ids = args.pipeline_ids

    for pipeline_id in pipeline_ids:
        process_pipeline(pipeline_id)

if __name__ == '__main__':
    main()
