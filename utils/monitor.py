from flask import Blueprint, jsonify
monitor_bp = Blueprint('monitor', __name__)
METRICS = {'cache_hits':0,'cache_misses':0,'local_executions':0,'cloud_executions':0,'total_tasks':0}
def increment_metric(k):
    if k in METRICS:
        METRICS[k]+=1
@monitor_bp.route('/metrics')
def metrics():
    return jsonify(METRICS)
