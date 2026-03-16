"""
email_alert.py — Envio de alertas por e-mail via SMTP.

Suporta texto puro e HTML. Implementa retry com backoff exponencial
para lidar com falhas transitórias de rede.
"""

import logging
import os
import smtplib
import time
from email.message import EmailMessage
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração via variáveis de ambiente
# ---------------------------------------------------------------------------
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SENDER: Optional[str] = os.getenv("EMAIL_SENDER")
PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")

_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 2  # segundos


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def send_alert(
    receiver: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    max_retries: int = _MAX_RETRIES,
) -> None:
    """
    Envia um e-mail de alerta via SMTP com TLS.

    Parâmetros
    ----------
    receiver : str
        Endereço de e-mail do destinatário.
    subject : str
        Assunto da mensagem.
    body : str
        Corpo em texto puro (fallback para clientes sem suporte a HTML).
    html_body : str, opcional
        Versão HTML do corpo. Se fornecida, é adicionada como alternativa.
    max_retries : int
        Número máximo de tentativas em caso de falha (padrão: 3).

    Raises
    ------
    RuntimeError
        Se ``EMAIL_SENDER`` ou ``EMAIL_PASSWORD`` não estiverem definidos.
    smtplib.SMTPException
        Se todas as tentativas falharem.
    """
    if not SENDER or not PASSWORD:
        raise RuntimeError(
            "As variáveis de ambiente EMAIL_SENDER e EMAIL_PASSWORD devem estar definidas no .env"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = receiver
    msg.set_content(body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    last_exc: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug("Tentativa %d/%d de envio de e-mail...", attempt, max_retries)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SENDER, PASSWORD)
                smtp.send_message(msg)
            logger.info("E-mail enviado com sucesso para %s", receiver)
            return
        except (smtplib.SMTPException, OSError) as exc:
            last_exc = exc
            wait = _RETRY_BACKOFF_BASE ** attempt
            logger.warning(
                "Falha no envio (tentativa %d/%d): %s. Aguardando %ds...",
                attempt, max_retries, exc, wait,
            )
            if attempt < max_retries:
                time.sleep(wait)

    raise smtplib.SMTPException(
        f"Todas as {max_retries} tentativas de envio falharam."
    ) from last_exc
