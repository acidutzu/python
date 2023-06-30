def generate_report(report_data):
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


def process_pipelines(project_id):
    pipeline_ids = get_pipeline_ids()

    pipeline_statuses = []
    failed_jobs = []
    successful_pipelines = []

    for pipeline_id in pipeline_ids:
        pipeline_name, job_names, job_ids, job_logs = get_pipeline_details(pipeline_id)

        if pipeline_name:
            pipeline_statuses.append({'Pipeline ID': pipeline_id, 'Pipeline Name': pipeline_name})

            if job_names and job_ids:
                pipeline_statuses[-1]['Jobs'] = ', '.join(job_names)
                pipeline_statuses[-1]['Job IDs'] = ', '.join(job_ids)

            if job_logs:
                failed_jobs.append({'Pipeline ID': pipeline_id, 'Failed Job Logs': job_logs})
            else:
                successful_pipelines.append(pipeline_id)

    generate_report(pipeline_statuses + failed_jobs + successful_pipelines)


# def main():
#     parser = argparse.ArgumentParser(description='Process pipeline IDs')
#     parser.add_argument('project_id', type=int, help='Project ID')
#     args = parser.parse_args()
#     project_id = args.project_id

process_pipelines(project_id)


# if __name__ == '__main__':
#     main()
