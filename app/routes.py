import os
import tempfile

from flask import jsonify, render_template, request

from app import app
from app.ocr import (
    compare_invoice_fields,
    extract_invoice_fields,
    extract_text_from_image,
    extract_text_from_pdf,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare_invoices", methods=["POST"])
def compare_invoices():
    temp_files = []

    try:
        if "invoice1" not in request.files or "invoice2" not in request.files:
            return jsonify({"error": "Both invoice files are required."}), 400

        file1 = request.files["invoice1"]
        file2 = request.files["invoice2"]

        if file1.filename == "" or file2.filename == "":
            return jsonify({"error": "Please select both invoice files."}), 400

        file1_path = _save_upload_to_temp(file1)
        file2_path = _save_upload_to_temp(file2)
        temp_files.extend([file1_path, file2_path])

        text1 = _extract_text_from_uploaded_file(file1_path, file1.filename)
        text2 = _extract_text_from_uploaded_file(file2_path, file2.filename)

        invoice1_fields = extract_invoice_fields(text1)
        invoice2_fields = extract_invoice_fields(text2)

        comparison = compare_invoice_fields(invoice1_fields, invoice2_fields)

        response = {
            **comparison,
            "result": "Invoices are the same!" if comparison["same_invoice"] else "Invoices are different.",
        }

        return jsonify(response)

    except RuntimeError as exc:
        return jsonify({"error": f"Processing error: {str(exc)}"}), 500
    except Exception as exc:
        return jsonify({"error": f"An unexpected error occurred: {str(exc)}"}), 500
    finally:
        for path in temp_files:
            try:
                os.remove(path)
            except OSError:
                pass


def _save_upload_to_temp(uploaded_file):
    _, extension = os.path.splitext(uploaded_file.filename)
    suffix = extension if extension else ".bin"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        uploaded_file.save(temp_file.name)
        return temp_file.name


def _extract_text_from_uploaded_file(file_path, original_filename):
    extension = os.path.splitext(original_filename.lower())[1]

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
        return extract_text_from_image(file_path)

    try:
        return extract_text_from_pdf(file_path)
    except Exception:
        return extract_text_from_image(file_path)