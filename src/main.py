import os
import sys
import json
from datetime import datetime
from enum import Enum
# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_cors import CORS
from models.user import db
from routes.user import user_bp
from routes.agents import agents_bp

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Enum types and datetime objects"""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.json_encoder = CustomJSONEncoder

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(agents_bp, url_prefix='/api/agents')

# Database configuration
config_name = os.environ.get('FLASK_ENV', 'development')
from config import get_config
config_class = get_config(config_name)

# Set configuration
app.config.from_object(config_class)

# If using SQLite, create directory
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    database_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
    os.makedirs(database_dir, exist_ok=True)

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'multi_agent_marketing_system',
        'timestamp': '2024-01-01T00:00:00Z'
    }

if __name__ == '__main__':
    print("🚀 Starting Multi-Agent Marketing System...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔌 API endpoints available at: http://localhost:5000/api")
    print("🤖 Agent endpoints available at: http://localhost:5000/api/agents")
    print("💾 Database location:", os.path.join(database_dir, 'app.db'))
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
