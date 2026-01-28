import qrcode
import frappe
from io import BytesIO
import base64
import urllib.parse

@frappe.whitelist()
def generate_qr_code(doc, method=None):
    try:
        # QR already generated
        # if doc.custom_base64data:
        #     return
        base_url = frappe.utils.get_url()
        params = {
            "pid": doc.name,
            "trial_id": doc.get("custom_trial_id"),
            "initials": doc.get("custom_patient_initials"),
            "dob": doc.get("dob"),
            "gender": doc.get("sex"),
            "blood_group": doc.get("blood_group"),
            "weight": doc.get("custom_weight_on_the_day_of_leukapheresis"),
            "uid": doc.get("custom_hospital_id_uhid"),
            "redirect_to": f"/app/patient/{urllib.parse.quote(doc.name)}"
        }
        # remove empty values
        params = {k: v for k, v in params.items() if v}
        query_string = urllib.parse.urlencode(
            params, quote_via=urllib.parse.quote
        )
        qr_url = f"{base_url}/patient-summary?{query_string}"
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=4
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        base64_data = (
            "data:image/png;base64,"
            + base64.b64encode(buffer.getvalue()).decode()
        )
        doc.db_set(
            "custom_base64data",
            base64_data,
            update_modified=False
        )
        frappe.logger().info(
            f"QR Code generated successfully for Patient {doc.name}"
        )
    except Exception as e:
        frappe.log_error(
            title="QR Code Generation Error",
            message=f"Patient: {doc.name}\nError: {str(e)}"
        )
        frappe.throw("Failed to generate QR Code")







@frappe.whitelist()
def generate_cart_qr_codes(patient_id, cart_name):
    """
    Generate three different QR codes for CarT Manufacturing:
    1. Patient QR Code - Contains patient information (opens web page)
    2. BMR QR Code - Contains patient info + Type: BMR + Batch (opens web page)
    3. G-Rex QR Code - Contains patient info + Type: G-Rex + Batch (opens web page)
    """
    try:
        # Get patient details
        patient = frappe.get_doc('Patient', patient_id)
        patient_name = patient.patient_name or patient_id
        
        # Get cart details
        cart = frappe.get_doc("CarT Manufacturing", cart_name)
        batch_value = cart.batch or "N/A"
        
        base_url = frappe.utils.get_url()
        
        # Generate Patient QR Code (URL with patient data)
        patient_params = {
            "pid": patient_id,
            "trial_id": patient.custom_trial_id,
            "initials": patient.custom_patient_initials,
            "dob": patient.dob,
            "gender": patient.sex,
            "blood_group": patient.blood_group,
            "uid": patient.custom_hospital_id_uhid,
            "redirect_to": f"/app/patient/{urllib.parse.quote(patient_id)}"
        }
        # Remove empty values
        patient_params = {k: v for k, v in patient_params.items() if v}
        patient_query_string = urllib.parse.urlencode(patient_params, quote_via=urllib.parse.quote)
        patient_qr_url = f"{base_url}/patient-summary?{patient_query_string}"
        patient_qr_base64 = generate_qr_code_base64(patient_qr_url)
        
        # Generate BMR QR Code (URL with BMR data)
        bmr_params = {
            "pid": patient_id,
            "trial_id": patient.custom_trial_id,
            "initials": patient.custom_patient_initials,
            "dob": patient.dob,
            "gender": patient.sex,
            "blood_group": patient.blood_group,
            "uid": patient.custom_hospital_id_uhid,
            "batch": batch_value,
            "type": "BMR",
            "type_full": "Batch Manufacturing Record",
            "redirect_to": f"/app/cart-manufacturing/{urllib.parse.quote(cart_name)}"
        }
        # Remove empty values
        bmr_params = {k: v for k, v in bmr_params.items() if v}
        bmr_query_string = urllib.parse.urlencode(bmr_params, quote_via=urllib.parse.quote)
        bmr_qr_url = f"{base_url}/patient-bmr?{bmr_query_string}"
        bmr_qr_base64 = generate_qr_code_base64(bmr_qr_url)
        
        # Generate G-Rex QR Code (URL with G-Rex data)
        grex_params = {
            "pid": patient_id,
            "trial_id": patient.custom_trial_id,
            "initials": patient.custom_patient_initials,
            "dob": patient.dob,
            "gender": patient.sex,
            "blood_group": patient.blood_group,
            "uid": patient.custom_hospital_id_uhid,
            "batch": batch_value,
            "type": "G-Rex",
            "redirect_to": f"/app/cart-manufacturing/{urllib.parse.quote(cart_name)}"
        }
        # Remove empty values
        grex_params = {k: v for k, v in grex_params.items() if v}
        grex_query_string = urllib.parse.urlencode(grex_params, quote_via=urllib.parse.quote)
        grex_qr_url = f"{base_url}/patient-grex?{grex_query_string}"
        grex_qr_base64 = generate_qr_code_base64(grex_qr_url)
        
        return {
            'patient_qr': patient_qr_base64,
            'bmr_qr': bmr_qr_base64,
            'grex_qr': grex_qr_base64,
            'patient_name': patient_name
        }
        
    except Exception as e:
        frappe.log_error(f"Error generating CarT QR codes for patient {patient_id}: {str(e)}")
        frappe.throw(f"Failed to generate QR codes: {str(e)}")


def generate_qr_code_base64(data):
    """
    Generate a QR code from data (URL) and return it as a base64 string
    """
    try:
        # Create QR code instance (same settings as your working example)
        qr = qrcode.QRCode(
            version=1,  # Changed to None for automatic sizing
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Changed to M for better reliability
            box_size=10,  # Changed to match your working example
            border=5,  # Changed to match your working example
        )
        
        # Add data and generate
        qr.add_data(data.strip())
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        frappe.log_error(f"Error in generate_qr_code_base64: {str(e)}")
        raise
    
    
@frappe.whitelist()
def get_item_qr_codes_for_table(cart_manufacturing_name):
    """
    Generate QR codes for items in CarT Manufacturing table (with URL)
    """
    try:
        frappe.logger().info(f"Starting QR code generation for: {cart_manufacturing_name}")
        
        doc = frappe.get_doc("CarT Manufacturing", cart_manufacturing_name)
        
        if not doc.patient or not doc.batch:
            frappe.logger().warning(f"Missing patient or batch for {cart_manufacturing_name}")
            return {}
        
        patient = frappe.get_doc("Patient", doc.patient)
        patient_name = patient.patient_name or doc.patient
        base_url = frappe.utils.get_url()
        qr_data = {}
        
        frappe.logger().info(f"Processing {len(doc.items)} items for patient: {patient_name}")
        
        for item in doc.items:
            try:
                frappe.logger().debug(f"Generating QR for item: {item.item_code}")
                
                # Create URL with parameters instead of plain text
                item_params = {
                    "manufacturing": doc.name,
                    "batch": doc.batch,
                    "patient": patient_name,
                    "pid": doc.patient,
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "dose": item.dose or "N/A",
                    "redirect_to": f"/app/cart-manufacturing/{urllib.parse.quote(doc.name)}"
                }
                # Remove empty values
                item_params = {k: v for k, v in item_params.items() if v}
                item_query_string = urllib.parse.urlencode(item_params, quote_via=urllib.parse.quote)
                item_qr_url = f"{base_url}/cart-item?{item_query_string}"
                
                # Generate QR code with URL
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=8,
                    border=4
                )
                qr.add_data(item_qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
                
                # Store QR code with additional item info
                qr_data[item.name] = {
                    "qr_code": qr_base64,
                    "dose": item.dose or "N/A",
                    "qty": item.qty
                }
                
            except Exception as e:
                frappe.logger().error(f"Error generating QR for item {item.item_code}: {str(e)}")
                frappe.log_error(frappe.get_traceback(), f"QR Generation Error - {item.item_code}")
                continue
        
        frappe.logger().info(f"Successfully generated {len(qr_data)} QR codes for {cart_manufacturing_name}")
        return qr_data
        
    except Exception as e:
        frappe.logger().error(f"Fatal error in get_item_qr_codes_for_table: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"QR Generation Fatal Error - {cart_manufacturing_name}")
        return {}
