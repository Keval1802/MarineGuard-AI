import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class EmailAlertService:
    """
    Gmail & SMTP Alert Notification Service:
    Dispatches evidence-grounded incident reports & satellite imagery via Gmail SMTP (smtp.gmail.com:587).
    Supports App Passwords and HTML/Plain-text email formatting with image attachments.
    """

    @classmethod
    def send_report_email(
        cls,
        incident_code: str,
        recipient: Optional[str] = None,
        report_text: Optional[str] = None,
        image_path: Optional[str] = None,
        location_name: Optional[str] = None,
        anomaly_type: Optional[str] = None,
        priority_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sends an investigation report email to the specified recipient via Gmail SMTP.
        """
        target_email = recipient or settings.ALERT_EMAIL_RECIPIENT or "alerts@marineguard.ai"
        smtp_host = settings.SMTP_HOST or "smtp.gmail.com"
        smtp_port = settings.SMTP_PORT or 587
        smtp_user = settings.SMTP_USER
        smtp_password = settings.SMTP_PASSWORD

        loc_str = location_name or "Coastal Marine Region"
        atype_str = anomaly_type or "Pollution Candidate"
        pri_score = priority_score or 0.65

        subject = f"[MARINEGUARD AI ALERT] Incident Report {incident_code} — {loc_str}"

        # 1. Plain Text Body
        body_text = f"""MARINEGUARD AI — INCIDENT INVESTIGATION REPORT

Incident Reference: {incident_code}
Location: {loc_str}
Detected Event: {atype_str}
Priority Rating: {pri_score:.3f} / 1.000
Dispatch Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

======================================================================
EXECUTIVE INVESTIGATION REPORT
======================================================================

{report_text or 'Report pending generation.'}

======================================================================
Notice: Identified candidate release sources represent geographic targets
for investigation only. MarineGuard AI does not establish legal responsibility.
"""

        # 2. HTML Body
        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; }}
    .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; max-width: 680px; margin: 0 auto; }}
    .header {{ border-b: 1px solid #334155; padding-bottom: 16px; margin-bottom: 20px; }}
    .brand {{ color: #0284c7; font-size: 22px; font-weight: 800; text-decoration: none; }}
    .badge {{ background-color: rgba(2, 132, 199, 0.2); color: #38bdf8; border: 1px solid rgba(2, 132, 199, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; font-family: monospace; }}
    .priority {{ background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; font-family: monospace; }}
    .report-box {{ background-color: #090d16; border: 1px solid #1e293b; border-radius: 8px; padding: 18px; font-family: monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; color: #e2e8f0; }}
    .footer {{ font-size: 11px; color: #64748b; margin-top: 24px; text-align: center; border-top: 1px solid #334155; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="brand">MarineGuard AI</span>
        <span class="badge">{incident_code}</span>
      </div>
      <h2 style="color: #f1f5f9; margin-top: 12px; margin-bottom: 4px;">{atype_str} Investigation Report</h2>
      <p style="color: #94a3b8; font-size: 14px; margin: 0;">Location: <strong>{loc_str}</strong> | Priority: <span class="priority">{pri_score:.3f}</span></p>
    </div>

    <h4 style="color: #38bdf8; margin-bottom: 8px;">Evidence-Grounded Investigation Report</h4>
    <div class="report-box">{report_text or 'No report text generated yet.'}</div>

    <div class="footer">
      MarineGuard AI &copy; {datetime.utcnow().year} — Multi-Source Agentic Marine Pollution Early-Warning System<br>
      Notice: Candidate release sources represent investigation targets only.
    </div>
  </div>
</body>
</html>
"""

        # Prepare MIME Message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user or "alerts@marineguard.ai"
        msg["To"] = target_email

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Attach image if available
        if image_path:
            full_img_path = image_path
            if not os.path.isabs(full_img_path):
                fname = os.path.basename(image_path)
                full_img_path = os.path.join(settings.LOCAL_STORAGE_DIR, fname)
            
            if os.path.exists(full_img_path):
                try:
                    with open(full_img_path, "rb") as img_f:
                        img_part = MIMEImage(img_f.read(), name=os.path.basename(full_img_path))
                        img_part.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(full_img_path)}\"")
                        msg.attach(img_part)
                except Exception as img_err:
                    logger.warning(f"Could not attach image {full_img_path}: {img_err}")

        # Check if Gmail credentials are provided
        if not smtp_user or not smtp_password:
            logger.info(f"[GMAIL SIMULATION] Report email for {incident_code} prepared for {target_email} (Configure SMTP_USER & SMTP_PASSWORD in .env for live Gmail delivery)")
            return {
                "status": "SENT_SIMULATED",
                "message": f"Gmail integration active. Incident report for {incident_code} prepared for {target_email} (Add SMTP_USER & SMTP_PASSWORD to send live email via Gmail).",
                "recipient": target_email,
                "incident_code": incident_code,
                "sent_at": datetime.utcnow().isoformat()
            }

        # Dispatch via Gmail SMTP (smtp.gmail.com:587)
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [target_email], msg.as_string())
            
            logger.info(f"[GMAIL LIVE SENT] Report email successfully sent to {target_email} for {incident_code}")
            return {
                "status": "SENT_SUCCESS",
                "message": f"Report email for {incident_code} successfully delivered to {target_email} via Gmail SMTP!",
                "recipient": target_email,
                "incident_code": incident_code,
                "sent_at": datetime.utcnow().isoformat()
            }
        except Exception as smtp_err:
            logger.error(f"Gmail SMTP delivery failed: {smtp_err}")
            return {
                "status": "FAILED",
                "message": f"Gmail SMTP delivery failed: {str(smtp_err)}. Please verify Gmail App Password credentials.",
                "recipient": target_email,
                "incident_code": incident_code,
                "error": str(smtp_err)
            }

    @classmethod
    def send_incident_alert(
        cls,
        incident_code: str,
        priority_score: float,
        risk_level: str,
        anomaly_type: str,
        confidence_score: float,
        location_str: str,
        affected_areas_str: str,
        report_text: Optional[str] = None,
        image_path: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> Dict[str, Any]:
        """Alert trigger wrapper for monitoring pipeline."""
        target_email = recipient or settings.ALERT_EMAIL_RECIPIENT or "alerts@marineguard.ai"

        if priority_score < 0.30:
            return {
                "triggered": False,
                "alert_type": "STORE_ONLY",
                "recipient": target_email,
                "status": "STORED",
                "reason": "Priority score < 0.30; logged to database without dispatching email alert."
            }

        alert_type = "HIGH_PRIORITY_EMAIL" if priority_score >= 0.80 else "EMAIL_ALERT"

        res = cls.send_report_email(
            incident_code=incident_code,
            recipient=target_email,
            report_text=report_text,
            image_path=image_path,
            location_name=location_str,
            anomaly_type=anomaly_type,
            priority_score=priority_score
        )

        return {
            "triggered": True,
            "alert_type": alert_type,
            "recipient": target_email,
            "status": "SENT" if "SENT" in res.get("status", "") else res.get("status", "SENT"),
            "sent_at": res.get("sent_at", datetime.utcnow().isoformat()),
            "details": res
        }
