from flask import Blueprint, jsonify, send_file
from apifairy import body, other_responses
from flask_marshmallow import Marshmallow
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
import tempfile
import logging

qrcode_bp = Blueprint("qrcode_pdf", __name__, url_prefix='/qrcode')
ma = Marshmallow(qrcode_bp)


class QRCodeInput(ma.Schema):
    data = ma.String(
        required=True, description="Données à encoder dans le QR Code"
    )


@qrcode_bp.route('/generate', strict_slashes=False, methods=['POST'])
@body(QRCodeInput)
@other_responses({400: 'Bad request', 500: 'Internal error'})
def generate_qrcode_pdf(data):
    """
    Génère un PDF avec un QR Code et les infos fournies.
    """
    logging.info("Generating QR Code PDF")
    try:
        qr_data = data['data']
        print("A")
        # Génération du QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color="black", back_color="white").convert("RGB")
        print("B")
        # Convertir l’image en ImageReader compatible ReportLab
        buffer_img = BytesIO()
        qr_img.save(buffer_img, format="PNG")
        buffer_img.seek(0)
        pil_img = Image.open(buffer_img)
        qr_image = ImageReader(pil_img)
        print("C")
        # Génération du PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, "Voici les informations reçues :")
        c.drawString(50, 780, qr_data)
        c.drawImage(qr_image, 50, 600, width=150, height=150)
        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        print("D")
        # Créer un fichier temporaire pour contourner l'erreur BytesIO
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_buffer.getvalue())
            tmp_path = tmp.name

        return send_file(
            tmp_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name="qrcode_infos.pdf"
        )

    except Exception as e:
        logging.info("Generating QR Code PDF")
        logging.warning("Generating QR Code PDF")
        return jsonify({"error": str(e)}), 500
