#######OKISH
from gitlab import Gitlab
import textwrap
import pandas as pd
import requests

gitlab_url = 'https://gitlab.com'
access_token = 'your_token_FFFFFFF000'
project_id = 40361633
search_phrases = ["AAA","BBB"]
teams_webhook_url = '<teams_webhook_url>'


def get_pipeline_ids():
    pipeline_ids = []
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


def get_job_id_names(pipeline_ids):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)

    data = []
    for pipeline_id in pipeline_ids:
        pipeline = project.pipelines.get(pipeline_id)
        jobs = pipeline.jobs.list()
        for job in jobs:
            job_logs = get_job_logs(job.id)
            captured_words = find_captured_words(job_logs)
            data.append({'Pipeline ID': pipeline_id, 'Job ID': job.id, 'Job Name': job.name, 'Job Logs': job_logs, 'Captured Words': captured_words})
            print(f"Pipeline ID: {pipeline_id}\n\tJob ID: {job.id}\n\tJob Name: {job.name}\n\tJob Logs: {job_logs}\n\tCaptured Words: {captured_words}\n")
            
            teams_message = f"Pipeline ID: {pipeline_id}\n\tJob ID: {job.id}\n\tJob Name: {job.name}\n\tJob Logs: {job_logs}\n\tCaptured Words: {captured_words}\n"
            send_teams_message(teams_message)

    df = pd.DataFrame(data)
    df.to_html('report.html', index=False)


#old
# def get_job_logs(job_id):
#     gl = Gitlab(gitlab_url, private_token=access_token)
#     project = gl.projects.get(project_id)
#     job = project.jobs.get(job_id)
#     job_trace_bytes = job.trace()
#     job_trace_str = job_trace_bytes.decode('utf-8')
#     wrapped_logs = textwrap.fill(job_trace_str, width=80)
#     return wrapped_logs

#new
def get_job_logs(job_id):
    gl = Gitlab(gitlab_url, private_token=access_token)
    project = gl.projects.get(project_id)
    job = project.jobs.get(job_id)
    job_trace_bytes = job.trace()
    job_trace_str = job_trace_bytes.decode('utf-8')
    lines = job_trace_str.splitlines()

    if len(lines) > 600:
        lines = lines[-30:]  # keep the last 30 lines if total lines exceed 600

    wrapped_logs = textwrap.fill('\n'.join(lines), width=80)
    return wrapped_logs


def find_captured_words(job_logs):
    captured_words = []
    search_words = ["executor", "environment"]
    for word in search_words:
        lines = job_logs.splitlines()
        for line in lines:
            line = line.lower()
            index = line.find(word)
            if index != -1:
                start_index = max(0, index - 15)
                end_index = min(len(line), index + len(word) + 15)
                captured_word = line[start_index:end_index]
                captured_words.append(captured_word)
    return captured_words

def process_pipelines():
    pipeline_ids = get_pipeline_ids()
    get_job_id_names(pipeline_ids)

process_pipelines()