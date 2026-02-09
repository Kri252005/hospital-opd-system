from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from models.database import init_db

# Import blueprints
from routes import patient, doctor

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
try:
    init_db()
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")
    exit(1)

# Register blueprints
app.register_blueprint(patient.bp, url_prefix='/api/patient')
app.register_blueprint(doctor.bp, url_prefix='/api/doctor')

# Home route
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hospital OPD Management System</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            h1 { color: #667eea; margin-bottom: 1rem; }
            h3 { color: #2d3748; margin-top: 2rem; margin-bottom: 1rem; }
            .success { color: #48bb78; font-weight: 600; margin-bottom: 1rem; }
            ul { list-style: none; padding: 0; }
            li { 
                padding: 0.75rem; 
                margin: 0.5rem 0; 
                background: #f7fafc;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.3s;
            }
            a:hover { color: #764ba2; }
            .dashboard-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }
            .dashboard-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                transition: transform 0.3s;
                text-decoration: none;
                display: block;
            }
            .dashboard-card:hover { transform: translateY(-5px); }
            .dashboard-card h4 { margin: 0; font-size: 1.2rem; }
            .dashboard-card p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.875rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Hospital OPD Management System</h1>
            <p class="success">✓ API is running successfully!</p>
            
            <h3>📊 Dashboards</h3>
            <div class="dashboard-links">
                <a href="/admin" class="dashboard-card">
                    <h4>👨‍💼 Admin Dashboard</h4>
                    <p>Patient check-in and queue management</p>
                </a>
                <a href="/doctor/1" class="dashboard-card">
                    <h4>👨‍⚕️ Doctor Dashboard</h4>
                    <p>Dr. Rajesh Kumar - Cardiology</p>
                </a>
                <a href="/patient-display" class="dashboard-card">
                    <h4>📺 Patient Display Board</h4>
                    <p>Public waiting area display</p>
                </a>
            </div>
            
            <h3>🔌 Available API Endpoints</h3>
            <ul>
                <li><code>POST /api/patient/checkin</code> - Check in patient</li>
                <li><code>GET /api/patient/queue-status/&lt;queue_id&gt;</code> - Get queue status</li>
                <li><code>GET /api/doctor/&lt;doctor_id&gt;/queue</code> - Get doctor's queue</li>
                <li><code>GET /api/doctor/&lt;doctor_id&gt;/current</code> - Get current patient</li>
                <li><code>POST /api/doctor/&lt;doctor_id&gt;/start-consultation</code> - Start consultation</li>
                <li><code>POST /api/doctor/&lt;doctor_id&gt;/end-consultation</code> - End consultation</li>
            </ul>
        </div>
    </body>
    </html>
    '''

# Dashboard routes
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/doctor/<int:doctor_id>')
def doctor_dashboard(doctor_id):
    return render_template('doctor_dashboard.html', doctor_id=doctor_id)

@app.route('/patient-display')
def patient_display():
    return render_template('patient_display.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    print("🚀 Starting Hospital OPD System...")
    print("📡 Server running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)