from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URLCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String(200), nullable=False)
    full_url = db.Column(db.String(2000), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float, nullable=False)
    error_message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.full_url,  # For compatibility with frontend
            'base_url': self.base_url,
            'full_url': self.full_url,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }

from urllib.parse import urlparse, urlunparse

def get_base_url(url):
    """Return URL without query parameters"""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def check_url(url):
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=10)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        return {
            'url': url,
            'base_url': get_base_url(url),
            'status_code': response.status_code,
            'response_time': response_time,
            'error_message': ''
        }
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'base_url': get_base_url(url),
            'status_code': -1,
            'response_time': 0,
            'error_message': 'Request timed out'
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'base_url': get_base_url(url),
            'status_code': -1,
            'response_time': 0,
            'error_message': str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history_index():
    # Get all distinct URLs to show in the dropdown
    subquery = db.session.query(URLCheck.base_url).group_by(URLCheck.base_url).subquery()
    urls = db.session.query(subquery).all()
    url_list = [url[0] for url in urls]
    url = request.args.get('url')  # Get URL from query parameter
    return render_template('history.html', urls=url_list, url=url)

@app.route('/check', methods=['POST'])
def check():
    urls = request.json.get('urls', [])
    results = []
    
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        
        result = check_url(url)
        check_record = URLCheck(
            base_url=result['base_url'],
            full_url=result['url'],
            status_code=result['status_code'],
            response_time=result['response_time'],
            error_message=result['error_message']
        )
        db.session.add(check_record)
        results.append(result)
    
    db.session.commit()
    return jsonify(results)

@app.route('/history/<url>')
def history(url):
    checks = URLCheck.query.filter_by(base_url=url).order_by(URLCheck.timestamp.desc()).limit(100).all()
    return jsonify([check.to_dict() for check in checks])

@app.route('/history/<url>')
def history_page(url):
    checks = URLCheck.query.filter_by(base_url=url).order_by(URLCheck.timestamp.desc()).limit(100).all()
    return render_template('history.html', url=url, checks=checks)

@app.route('/api/history')
def history_data():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
            
        checks = URLCheck.query.filter_by(base_url=url).order_by(URLCheck.timestamp.desc()).limit(100).all()
        if not checks:
            return jsonify([])
        return jsonify([check.to_dict() for check in checks])
    except Exception as e:
        print(f"Error in history_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def stats_data():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
            
        checks = URLCheck.query.filter_by(base_url=url).all()
        
        if not checks:
            return jsonify({
                'total_checks': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'last_check': None
            })

        total_checks = len(checks)
        successful_checks = sum(1 for check in checks if 200 <= check.status_code < 300)
        avg_response_time = sum(check.response_time for check in checks) / total_checks
        last_check = checks[-1]

        return jsonify({
            'total_checks': total_checks,
            'success_rate': (successful_checks / total_checks) * 100,
            'avg_response_time': avg_response_time,
            'last_check': last_check.to_dict()
        })
    except Exception as e:
        print(f"Error in stats_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        # Drop existing tables if they exist
        # db.drop_all()
        # Create new tables with updated schema
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
