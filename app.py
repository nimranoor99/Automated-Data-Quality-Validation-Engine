from flask import Flask, render_template, jsonify, request
from data_quality import DataQualityEngine
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Real-time dashboard for Product Managers"""
    engine = DataQualityEngine('sample_data.xlsx')
    results = engine.run_all_checks()
    return render_template('dashboard.html', data=results)

@app.route('/api/quality', methods=['GET'])
def api_quality():
    """REST API endpoint for quality results"""
    engine = DataQualityEngine('sample_data.xlsx')
    results = engine.run_all_checks()
    return jsonify(results)

@app.route('/api/repair', methods=['POST'])
def api_repair():
    """API to trigger automated repair actions"""
    engine = DataQualityEngine('sample_data.xlsx')
    results = engine.run_all_checks()
    
    # Simulated repair actions
    repairs = {
        'duplicates_removed': results['checks']['duplicates']['count'],
        'missing_fields_filled': sum(results['checks']['missing_fields'].values()),
        'drift_corrected': results['checks']['config_drift']['invalid_ips_count']
    }
    return jsonify({'status': 'success', 'repairs_applied': repairs})

if __name__ == '__main__':
    app.run(debug=True, port=5000)