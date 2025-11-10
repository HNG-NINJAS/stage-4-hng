#!/usr/bin/env python3
"""
Seed script to create initial templates
Run: python scripts/seed_templates.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import List, Dict

BASE_URL = os.getenv("TEMPLATE_SERVICE_URL", "http://localhost:3004")
API_URL = f"{BASE_URL}/api/v1/templates"


templates: List[Dict] = [
    {
        "template_id": "welcome_email",
        "name": "Welcome Email",
        "description": "Sent to new users upon registration",
        "type": "email",
        "category": "onboarding",
        "subject": "Welcome to {{company_name}}, {{name}}! 🎉",
        "body": """Hi {{name}},

Welcome to {{company_name}}! We're excited to have you on board.

To get started, please verify your email by clicking the link below:
{{verification_link}}

If you have any questions, feel free to reach out to our support team.

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "password_reset",
        "name": "Password Reset",
        "description": "Password reset email",
        "type": "email",
        "category": "security",
        "subject": "Reset Your Password - {{company_name}}",
        "body": """Hi {{name}},

We received a request to reset your password for your {{company_name}} account.

Click the link below to reset your password:
{{reset_link}}

This link will expire in {{expiry_hours}} hours.

If you didn't request this, please ignore this email and your password will remain unchanged.

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "order_confirmation",
        "name": "Order Confirmation",
        "description": "Order confirmation email",
        "type": "email",
        "category": "transactional",
        "subject": "Order Confirmation #{{order_id}} - {{company_name}}",
        "body": """Hi {{name}},

Thank you for your order!

Order Details:
- Order ID: {{order_id}}
- Total: ${{total}}
- Date: {{order_date}}

Items Ordered:
{{items}}

Your order will be processed within 24 hours. We'll send you a shipping notification once your order ships.

Track your order: {{tracking_url}}

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "order_shipped",
        "name": "Order Shipped Push Notification",
        "description": "Push notification when order ships",
        "type": "push",
        "category": "transactional",
        "subject": "Your order #{{order_id}} has shipped! 📦",
        "body": "Good news {{name}}! Your order is on its way. Track it here: {{tracking_url}}",
        "language_code": "en"
    },
    {
        "template_id": "promotional_offer",
        "name": "Promotional Offer",
        "description": "Marketing promotion email",
        "type": "email",
        "category": "marketing",
        "subject": "Special Offer: {{discount}}% Off Just For You! 🎁",
        "body": """Hi {{name}},

Great news! We're offering you an exclusive {{discount}}% discount on your next purchase!

Use promo code: {{promo_code}}

This offer expires on {{expiry_date}}, so don't miss out!

Shop now: {{shop_url}}

Happy shopping!
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "account_alert",
        "name": "Account Alert Push",
        "description": "Security alert push notification",
        "type": "push",
        "category": "security",
        "subject": "🔒 Security Alert - {{company_name}}",
        "body": "{{alert_message}}. If this wasn't you, please secure your account immediately.",
        "language_code": "en"
    },
    {
        "template_id": "payment_received",
        "name": "Payment Received",
        "description": "Payment confirmation email",
        "type": "email",
        "category": "transactional",
        "subject": "Payment Received - {{company_name}}",
        "body": """Hi {{name}},

We've received your payment of ${{amount}}.

Payment Details:
- Amount: ${{amount}}
- Payment Method: {{payment_method}}
- Transaction ID: {{transaction_id}}
- Date: {{payment_date}}

Thank you for your business!

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "subscription_reminder",
        "name": "Subscription Reminder",
        "description": "Subscription renewal reminder",
        "type": "email",
        "category": "transactional",
        "subject": "Your {{plan_name}} Subscription Renews Soon",
        "body": """Hi {{name}},

This is a friendly reminder that your {{plan_name}} subscription will renew on {{renewal_date}}.

Renewal Amount: ${{amount}}
Payment Method: {{payment_method}}

To make changes to your subscription, visit your account settings:
{{account_url}}

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    },
    {
        "template_id": "new_message",
        "name": "New Message Push",
        "description": "Push notification for new messages",
        "type": "push",
        "category": "notification",
        "subject": "💬 New message from {{sender_name}}",
        "body": "{{sender_name}}: {{message_preview}}",
        "language_code": "en"
    },
    {
        "template_id": "account_verification",
        "name": "Account Verification",
        "description": "Email verification",
        "type": "email",
        "category": "security",
        "subject": "Verify Your Email - {{company_name}}",
        "body": """Hi {{name}},

Please verify your email address to complete your registration.

Verification Code: {{verification_code}}

Or click this link: {{verification_link}}

This code will expire in {{expiry_minutes}} minutes.

Best regards,
The {{company_name}} Team""",
        "language_code": "en"
    }
]


def seed_templates():
    """Seed all templates"""
    print("=" * 50)
    print("🌱 Seeding Template Service")
    print("=" * 50)
    print(f"Target: {BASE_URL}")
    print()
    
    success_count = 0
    error_count = 0
    
    for template in templates:
        try:
            response = requests.post(API_URL, json=template, timeout=10)
            
            if response.status_code == 201:
                print(f"✅ Created: {template['template_id']}")
                success_count += 1
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"⚠️  Skipped (exists): {template['template_id']}")
            else:
                print(f"❌ Failed: {template['template_id']} - {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                error_count += 1
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Could not connect to {BASE_URL}")
            print("   Make sure the service is running!")
            return
        except Exception as e:
            print(f"❌ Error creating {template['template_id']}: {str(e)}")
            error_count += 1
    
    print()
    print("=" * 50)
    print(f"🎉 Seeding Complete!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print("=" * 50)


def add_translations():
    """Add Spanish translations for some templates"""
    print("\n🌍 Adding translations...")
    
    translations = [
        {
            "template_id": "welcome_email",
            "language_code": "es",
            "subject": "¡Bienvenido a {{company_name}}, {{name}}! 🎉",
            "body": """Hola {{name}},

¡Bienvenido a {{company_name}}! Estamos emocionados de tenerte con nosotros.

Para comenzar, verifica tu correo electrónico haciendo clic en el enlace a continuación:
{{verification_link}}

Si tienes alguna pregunta, no dudes en contactar a nuestro equipo de soporte.

Saludos cordiales,
El equipo de {{company_name}}"""
        },
        {
            "template_id": "password_reset",
            "language_code": "es",
            "subject": "Restablecer tu Contraseña - {{company_name}}",
            "body": """Hola {{name}},

Recibimos una solicitud para restablecer tu contraseña de {{company_name}}.

Haz clic en el enlace a continuación para restablecer tu contraseña:
{{reset_link}}

Este enlace caducará en {{expiry_hours}} horas.

Si no solicitaste esto, ignora este correo y tu contraseña permanecerá sin cambios.

Saludos cordiales,
El equipo de {{company_name}}"""
        },
        {
            "template_id": "order_shipped",
            "language_code": "es",
            "subject": "¡Tu pedido #{{order_id}} ha sido enviado! 📦",
            "body": "¡Buenas noticias {{name}}! Tu pedido está en camino. Rastréalo aquí: {{tracking_url}}"
        }
    ]
    
    for translation in translations:
        template_id = translation.pop("template_id")
        try:
            response = requests.post(
                f"{API_URL}/{template_id}/translations",
                json=translation,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ Added translation: {template_id} ({translation['language_code']})")
            else:
                print(f"❌ Failed translation: {template_id}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print()
    seed_templates()
    add_translations()
    print()