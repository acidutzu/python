import requests
import json
from datetime import datetime
from gitlab import Gitlab

gitlab_url = '<gitlab_url>'
access_token = '<access_token>'
project_id = '<project_id>'
teams_webhook_url = '<teams_webhook_url>'

def get_failed_job_logs(failed_job):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(failed_job.id)
    job_trace = job.trace()
    return job_trace

def send_teams_message(message):
    payload = {
        'text': message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(teams_webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print('Message sent successfully.')
    else:
        print('Failed to send message.')

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

            # Send Teams message with the log of the failed job
            teams_message = f"Pipeline {pipeline_id} failed.\nFailed Job: {failed_job.name}\nJob Logs:\n{logs}"
            send_teams_message(teams_message)
        else:
            # Send Teams message for pipeline failure without specific failed job information
            teams_message = f"Pipeline {pipeline_id} failed."
            send_teams_message(teams_message)
    elif pipeline_status == 'success':
        print(f'Pipeline {pipeline_id} succeeded.')
        # Logic for success pipelines here
    else:
        print(f'Pipeline {pipeline_id} has an unknown status. Script execution skipped.')

# Example usage
pipeline_id = '<pipeline_id>'
failed_job_id = '<failed_job_id>'  # Set to None if there is no failed job
pipeline_status = 'failed'  # Set the actual pipeline status
failed_job = {'id': failed_job_id, 'name': 'Failed Job'} if failed_job_id else None

execute_script(pipeline_status, failed_job, pipeline_id)
