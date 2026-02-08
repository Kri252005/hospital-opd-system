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
    <h1>Hospital OPD Management System</h1>
    <p>API is running successfully!</p>
    <h3>Available Endpoints:</h3>
    <ul>
        <li>POST /api/patient/checkin - Check in patient</li>
        <li>GET /api/patient/queue-status/&lt;queue_id&gt; - Get queue status</li>
        <li>GET /api/doctor/&lt;doctor_id&gt;/queue - Get doctor's queue</li>
        <li>GET /api/doctor/&lt;doctor_id&gt;/current - Get current patient</li>
        <li>POST /api/doctor/&lt;doctor_id&gt;/start-consultation - Start consultation</li>
        <li>POST /api/doctor/&lt;doctor_id&gt;/end-consultation - End consultation</li>
    </ul>
    '''

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