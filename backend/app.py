from flask import Flask, jsonify
from flask_cors import CORS
from api import api_bp
from api.auth.routes import auth_bp
# TEMP DISABLED: from api.image.routes import image_bp
# TEMP DISABLED: from api.admin.routes import admin_bp
# TEMP DISABLED: from api.admin.settings import settings_bp
# TEMP DISABLED: from api.survey.routes import survey_bp
# TEMP DISABLED: from api.monitor.routes import monitor_bp
from config.settings import settings
from utils.session_utils import get_dynamic_session_timeout
from datetime import timedelta
from api.chat.routes import chat_bp  # New AI Chat Service


import os
import logging
import threading
# DISABLED: from services.scheduler_service import MonitoringScheduler
# AI Chat Service will handle its own model loading

def create_app():
    app = Flask(__name__)
    
    # Configure Flask sessions with dynamic timeout
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'crpf-mental-health-secret-key-change-in-production')
    
    # Use dynamic session timeout, with fallback to settings default
    try:
        session_timeout = get_dynamic_session_timeout()
    except:
        session_timeout = settings.SESSION_TIMEOUT
        
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=session_timeout)
    
    # Update CORS configuration using settings
    allowed_origins = list({
        settings.FRONTEND_URL,
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    })
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True  # Enable credentials for session cookies
        }
    })


    # Register the main API blueprint
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # TEMP DISABLED: app.register_blueprint(image_bp, url_prefix='/api/image')
    # TEMP DISABLED: app.register_blueprint(admin_bp, url_prefix='/api/admin')
    # TEMP DISABLED: app.register_blueprint(settings_bp, url_prefix='/api/admin/settings')
    # TEMP DISABLED: app.register_blueprint(survey_bp, url_prefix='/api/survey')
    # TEMP DISABLED: app.register_blueprint(monitor_bp, url_prefix='/api/monitor')
    app.register_blueprint(chat_bp, url_prefix='/api/ai-chat')  # New AI Chat Service

    # Enhanced AI Chat Service: Initialize in background for better startup performance
    def start_enhanced_ai_chat_service():
        """Initialize Enhanced AI Chat Service in background thread"""
        try:
            print("[APP] Starting Enhanced AI Chat Service...")
            logging.info("Starting Enhanced AI Chat Service...")
            from services.enhanced_ai_chat_service import get_enhanced_ai_chat_service
            service = get_enhanced_ai_chat_service()
            status = service.get_health_status()
            print(f"[APP] Enhanced AI Chat Service status: {status}")
            logging.info(f"Enhanced AI Chat Service initialization completed: {status}")
        except Exception as e:
            print(f"[APP] Error starting Enhanced AI Chat Service: {e}")
            logging.error(f"Error starting Enhanced AI Chat Service: {e}")
    
    # Start Enhanced AI Chat Service initialization in background thread (non-blocking)
    print("[APP] Launching Enhanced AI Chat Service thread...")
    chat_service_thread = threading.Thread(target=start_enhanced_ai_chat_service, daemon=True)
    chat_service_thread.start()

    # DISABLED: Initialize scheduler for CCTV monitoring
    # scheduler = MonitoringScheduler()
    
    # DISABLED: Start scheduler within app context
    # with app.app_context():
    #     scheduler.start()

    # DISABLED: Cleanup on app shutdown
    # @app.teardown_appcontext
    # def cleanup(error):
    #     scheduler.stop()
    
    return app

app = create_app()

@app.route('/')
def hello():
    return jsonify({"message": "CRPF Mental Health Monitoring System API"})

if __name__ == '__main__':
    app.run(debug=settings.DEBUG_MODE, port=settings.BACKEND_PORT)
