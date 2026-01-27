"""
Notification System

This tool sends notifications about workflow events via multiple channels.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    FILE = "file"
    CONSOLE = "console"


class NotificationSystem:
    """Send notifications via multiple channels"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Channel configurations
        self.email_config = self.config.get('email', {})
        self.slack_config = self.config.get('slack', {})
        self.discord_config = self.config.get('discord', {})
        self.webhook_config = self.config.get('webhook', {})
        
        # Enabled channels
        self.enabled_channels = self.config.get('enabled_channels', [
            NotificationChannel.CONSOLE.value
        ])
        
        # Notification log
        self.notification_log = []
        self.log_file = self.config.get('log_file', 'notifications.log')
    
    def send_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        data: Optional[Dict] = None,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send notification to specified channels
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            data: Optional additional data
            channels: List of channels to use (None = use all enabled)
            
        Returns:
            Dictionary with success status per channel
        """
        if channels is None:
            channels = self.enabled_channels
        
        # Create notification object
        notification = {
            'title': title,
            'message': message,
            'type': notification_type.value,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Log notification
        self.notification_log.append(notification)
        
        # Send to each channel
        results = {}
        
        for channel in channels:
            try:
                if channel == NotificationChannel.CONSOLE.value:
                    results[channel] = self._send_console(notification)
                elif channel == NotificationChannel.EMAIL.value:
                    results[channel] = self._send_email(notification)
                elif channel == NotificationChannel.SLACK.value:
                    results[channel] = self._send_slack(notification)
                elif channel == NotificationChannel.DISCORD.value:
                    results[channel] = self._send_discord(notification)
                elif channel == NotificationChannel.WEBHOOK.value:
                    results[channel] = self._send_webhook(notification)
                elif channel == NotificationChannel.FILE.value:
                    results[channel] = self._send_file(notification)
                else:
                    logger.warning(f"Unknown channel: {channel}")
                    results[channel] = False
            except Exception as e:
                logger.error(f"Error sending to {channel}: {e}")
                results[channel] = False
        
        return results
    
    def _send_console(self, notification: Dict) -> bool:
        """Send to console"""
        try:
            icon = {
                NotificationType.INFO.value: 'ℹ️',
                NotificationType.SUCCESS.value: '✅',
                NotificationType.WARNING.value: '⚠️',
                NotificationType.ERROR.value: '❌',
                NotificationType.CRITICAL.value: '🔥'
            }.get(notification['type'], 'ℹ️')
            
            print(f"\n{icon} [{notification['type'].upper()}] {notification['title']}")
            print(f"   {notification['message']}")
            print(f"   Time: {notification['timestamp']}")
            
            if notification['data']:
                print(f"   Data: {json.dumps(notification['data'], indent=2)}")
            
            return True
        except Exception as e:
            logger.error(f"Console notification error: {e}")
            return False
    
    def _send_email(self, notification: Dict) -> bool:
        """Send via email"""
        try:
            if not self.email_config:
                logger.warning("Email not configured")
                return False
            
            smtp_host = self.email_config.get('smtp_host')
            smtp_port = self.email_config.get('smtp_port', 587)
            username = self.email_config.get('username')
            password = self.email_config.get('password')
            from_addr = self.email_config.get('from_address')
            to_addrs = self.email_config.get('to_addresses', [])
            
            if not all([smtp_host, username, password, from_addr, to_addrs]):
                logger.warning("Incomplete email configuration")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = ', '.join(to_addrs)
            msg['Subject'] = f"[{notification['type'].upper()}] {notification['title']}"
            
            # Email body
            body = f"""
{notification['title']}

{notification['message']}

Time: {notification['timestamp']}
Type: {notification['type']}

{json.dumps(notification['data'], indent=2) if notification['data'] else ''}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {len(to_addrs)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Email notification error: {e}")
            return False
    
    def _send_slack(self, notification: Dict) -> bool:
        """Send to Slack"""
        try:
            if not self.slack_config:
                logger.warning("Slack not configured")
                return False
            
            webhook_url = self.slack_config.get('webhook_url')
            
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False
            
            # Color coding
            colors = {
                NotificationType.INFO.value: '#3498db',
                NotificationType.SUCCESS.value: '#2ecc71',
                NotificationType.WARNING.value: '#f39c12',
                NotificationType.ERROR.value: '#e74c3c',
                NotificationType.CRITICAL.value: '#c0392b'
            }
            
            payload = {
                "attachments": [{
                    "color": colors.get(notification['type'], '#95a5a6'),
                    "title": notification['title'],
                    "text": notification['message'],
                    "fields": [
                        {
                            "title": "Type",
                            "value": notification['type'].upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": notification['timestamp'],
                            "short": True
                        }
                    ]
                }]
            }
            
            if notification['data']:
                payload['attachments'][0]['fields'].append({
                    "title": "Additional Data",
                    "value": f"```{json.dumps(notification['data'], indent=2)}```",
                    "short": False
                })
            
            import requests
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return True
            else:
                logger.error(f"Slack error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
            return False
    
    def _send_discord(self, notification: Dict) -> bool:
        """Send to Discord"""
        try:
            if not self.discord_config:
                logger.warning("Discord not configured")
                return False
            
            webhook_url = self.discord_config.get('webhook_url')
            
            if not webhook_url:
                logger.warning("Discord webhook URL not configured")
                return False
            
            # Color coding (decimal format for Discord)
            colors = {
                NotificationType.INFO.value: 3447003,      # Blue
                NotificationType.SUCCESS.value: 3066993,   # Green
                NotificationType.WARNING.value: 15844367,  # Yellow
                NotificationType.ERROR.value: 15158332,    # Red
                NotificationType.CRITICAL.value: 12589840  # Dark Red
            }
            
            embed = {
                "embeds": [{
                    "title": notification['title'],
                    "description": notification['message'],
                    "color": colors.get(notification['type'], 10070709),
                    "fields": [
                        {
                            "name": "Type",
                            "value": notification['type'].upper(),
                            "inline": True
                        },
                        {
                            "name": "Time",
                            "value": notification['timestamp'],
                            "inline": True
                        }
                    ],
                    "timestamp": notification['timestamp']
                }]
            }
            
            if notification['data']:
                embed['embeds'][0]['fields'].append({
                    "name": "Additional Data",
                    "value": f"```json\n{json.dumps(notification['data'], indent=2)}\n```",
                    "inline": False
                })
            
            import requests
            response = requests.post(webhook_url, json=embed)
            
            if response.status_code == 204:
                logger.info("Discord notification sent")
                return True
            else:
                logger.error(f"Discord error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord notification error: {e}")
            return False
    
    def _send_webhook(self, notification: Dict) -> bool:
        """Send to custom webhook"""
        try:
            if not self.webhook_config:
                logger.warning("Webhook not configured")
                return False
            
            url = self.webhook_config.get('url')
            headers = self.webhook_config.get('headers', {})
            
            if not url:
                logger.warning("Webhook URL not configured")
                return False
            
            import requests
            response = requests.post(url, json=notification, headers=headers)
            
            if response.status_code in [200, 201, 204]:
                logger.info("Webhook notification sent")
                return True
            else:
                logger.error(f"Webhook error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
            return False
    
    def _send_file(self, notification: Dict) -> bool:
        """Write to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(notification) + '\n')
            
            logger.debug(f"Notification logged to {self.log_file}")
            return True
            
        except Exception as e:
            logger.error(f"File notification error: {e}")
            return False
    
    def send_video_generated(self, video_path: str, topic: str, duration: float):
        """Send notification for completed video generation"""
        self.send_notification(
            title="Video Generated",
            message=f"New video generated successfully: {topic}",
            notification_type=NotificationType.SUCCESS,
            data={
                'video_path': video_path,
                'topic': topic,
                'duration': duration
            }
        )
    
    def send_upload_complete(self, platform: str, url: str, title: str):
        """Send notification for completed upload"""
        self.send_notification(
            title="Upload Complete",
            message=f"Video uploaded to {platform}: {title}",
            notification_type=NotificationType.SUCCESS,
            data={
                'platform': platform,
                'url': url,
                'title': title
            }
        )
    
    def send_error(self, operation: str, error_message: str):
        """Send error notification"""
        self.send_notification(
            title=f"Error in {operation}",
            message=error_message,
            notification_type=NotificationType.ERROR,
            data={'operation': operation}
        )
    
    def send_workflow_complete(self, stats: Dict):
        """Send notification for completed workflow"""
        self.send_notification(
            title="Workflow Complete",
            message=f"Workflow completed. Generated {stats.get('videos_generated', 0)} videos.",
            notification_type=NotificationType.SUCCESS,
            data=stats
        )
    
    def get_notification_history(self, limit: int = 100) -> List[Dict]:
        """
        Get recent notifications
        
        Args:
            limit: Maximum number of notifications to return
            
        Returns:
            List of recent notifications
        """
        return self.notification_log[-limit:]
    
    def clear_history(self):
        """Clear notification history"""
        count = len(self.notification_log)
        self.notification_log.clear()
        logger.info(f"Cleared {count} notifications from history")


def main():
    """Example usage"""
    
    # Configure notification system
    config = {
        'enabled_channels': ['console', 'file'],
        'log_file': 'test_notifications.log',
        'email': {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-password',
            'from_address': 'your-email@gmail.com',
            'to_addresses': ['recipient@example.com']
        }
    }
    
    notifier = NotificationSystem(config)
    
    # Send various notifications
    notifier.send_notification(
        "Test Notification",
        "This is a test notification",
        NotificationType.INFO
    )
    
    notifier.send_video_generated(
        '/path/video.mp4',
        'AI Tutorial',
        60.5
    )
    
    notifier.send_error(
        'Video Upload',
        'Failed to connect to YouTube API'
    )
    
    notifier.send_workflow_complete({
        'videos_generated': 5,
        'videos_uploaded': 4,
        'duration': 123.45
    })
    
    print(f"\nSent {len(notifier.get_notification_history())} notifications")


if __name__ == '__main__':
    main()
