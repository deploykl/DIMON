# ~/sms_server.py
from flask import Flask, request, jsonify
import subprocess
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SMSSender:
    def send_sms(self, phone_number, message):
        """Envía SMS usando Termux API"""
        try:
            # Limpiar número (remover espacios, etc.)
            clean_phone = phone_number.strip().replace(" ", "")
            
            # Comando Termux para enviar SMS
            cmd = f'termux-sms-send -n "{clean_phone}" "{message}"'
            
            logger.info(f"Enviando SMS a {clean_phone}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ SMS enviado exitosamente a {clean_phone}")
                return True
            else:
                logger.error(f"❌ Error enviando SMS: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Excepción enviando SMS: {e}")
            return False

sms_sender = SMSSender()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "SMS Server"})

@app.route('/sms', methods=['POST'])
def send_sms():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        phone_number = data.get('phone')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({"error": "Phone and message are required"}), 400
        
        # Validar número de teléfono básico
        if not phone_number.startswith('+'):
            return jsonify({"error": "Phone number must include country code (+51...)"}), 400
        
        # Enviar SMS
        success = sms_sender.send_sms(phone_number, message)
        
        if success:
            return jsonify({
                "status": "sent", 
                "to": phone_number,
                "message_length": len(message)
            })
        else:
            return jsonify({"error": "Failed to send SMS"}), 500
            
    except Exception as e:
        logger.error(f"Error en endpoint /sms: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Obtener IP del dispositivo para acceso externo
    host = '0.0.0.0'  # Escuchar en todas las interfaces
    port = 5000
    
    print(f"🚀 Servidor SMS iniciado en http://{host}:{port}")
    print("📞 Endpoints disponibles:")
    print("   GET  /health - Estado del servicio")
    print("   POST /sms - Enviar SMS")
    
    app.run(host=host, port=port, debug=False)