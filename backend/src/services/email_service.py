import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_recovery_email(to_email: str, token: str) -> bool:
        """
        Envía el código de recuperación de contraseña de 6 dígitos mediante SMTP.
        Retorna True si el envío fue exitoso.
        """
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port_raw = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")

        if not all([smtp_host, smtp_port_raw, smtp_user, smtp_pass]):
            logger.error("Credenciales SMTP incompletas. Verifique SMTP_HOST, SMTP_PORT, SMTP_USER y SMTP_PASSWORD en el .env.")
            return False

        smtp_port = int(smtp_port_raw)

        subject = "Código de Recuperación de Contraseña - CRM Industrial"
        
        # Plantilla de correo HTML básica
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    <div style="background-color: #4f46e5; padding: 20px; text-align: center;">
                        <h2 style="color: white; margin: 0;">Recuperación de Contraseña</h2>
                    </div>
                    <div style="padding: 30px;">
                        <p>Hemos recibido una solicitud para restablecer la contraseña de su cuenta en <strong>CRM Industrial SaaS</strong>.</p>
                        <p>Su código de seguridad (token) temporal es:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; background-color: #f3f4f6; padding: 15px 25px; border-radius: 6px; color: #1f2937;">{token}</span>
                        </div>
                        <p style="color: #666; font-size: 14px;">Este código es válido únicamente durante los próximos 10 minutos. Si usted no solicitó este cambio, puede ignorar este mensaje de forma segura.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"CRM Industrial <{smtp_user}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        try:
            # Conexión STARTTLS segura
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Correo de recuperación enviado exitosamente a {to_email}")
            return True
        except Exception as e:
            logger.error(f"Fallo al enviar correo SMTP a {to_email}: {str(e)}")
            return False
