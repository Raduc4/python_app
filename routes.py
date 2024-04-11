import json
import os
import time
from __init__ import webserver
from flask import request, jsonify

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response_one(job_id):
    webserver.logger.info(f'get_results/{job_id}')

    if not os.path.exists(f'app/results/{job_id}'):
        return jsonify({"status": "error", "reason": "Invalid job_id"})
    
    with open(f'app/results/{job_id}', 'r') as f:
        try:
            text = f.read()
            json_data = json.loads(text)
            return jsonify(json_data)
        except json.JSONDecodeError as e:
            print(f.read())
            return jsonify({"status": "error", "reason": "Invalid job_id"})
    

@webserver.route('/api/num_jobs', methods=['GET'])
def get_response_count():
    webserver.logger.info('num_jobs')

    running_tasks = 0
    for file in os.listdir('app/results'):
        with open(f'app/results/{file}', 'r') as f:
            data = json.loads(f.read())
            if data['status'] == 'running':
                running_tasks += 1
    
    return running_tasks

@webserver.route('/api/jobs', methods=['GET'])
def get_response_all():
    webserver.logger.info('jobs')

    task_states = []
    for file in os.listdir('app/results'):
        with open(f'app/results/{file}', 'r') as f:
            data = json.loads(f.read())
            task_states.append({file: data['status']})
    
    return jsonify({"status": "done", "data": task_states})

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def get_response():
    webserver.logger.info('graceful_shutdown')

    webserver.tasks_runner.stop()
    return jsonify({"status": "done"})

def send_request(webserver, data: tuple, f):
    with webserver.lock:
        job_id = webserver.job_counter
        webserver.job_counter += 1
    
    task = {'job_id': job_id, 'data': data, 'f': f}
    webserver.tasks_runner.add_task(task)

    return {'job_id': job_id}

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    webserver.logger.info(f'states_mean - {request.json}')

    question = request.json['question']
    return send_request(webserver, (question,), webserver.data_ingestor.average)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    webserver.logger.info(f'state_mean - {request.json}')
    
    question, state = request.json['question'], request.json['state']
    return send_request(webserver, (question, state), webserver.data_ingestor.average)


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    webserver.logger.info(f'best5 - {request.json}')
    
    question = request.json['question']
    return send_request(webserver, (question, "best"), webserver.data_ingestor.top5)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    webserver.logger.info(f'worst5 - {request.json}')
    
    question = request.json['question']
    return send_request(webserver, (question, "worst"), webserver.data_ingestor.top5)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    webserver.logger.info(f'global_mean - {request.json}')
    
    question = request.json['question']
    return send_request(webserver, (question, None, True), webserver.data_ingestor.average)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    webserver.logger.info(f'diff_from_mean - {request.json}')
    
    question = request.json['question']
    return send_request(webserver, (question,), webserver.data_ingestor.diff_from_average)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    webserver.logger.info(f'state_diff_from_mean - {request.json}')
    
    question, state = request.json['question'], request.json['state']
    return send_request(webserver, (question, state ), webserver.data_ingestor.diff_from_average)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    webserver.logger.info(f'mean_by_category - {request.json}')
    
    question = request.json['question']
    return send_request(webserver, (question,), webserver.data_ingestor.average_by_category)

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    webserver.logger.info(f'state_mean_by_category - {request.json}')
    
    question, state = request.json['question'], request.json['state']
    return send_request(webserver, (question, state), webserver.data_ingestor.average_by_category)

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
