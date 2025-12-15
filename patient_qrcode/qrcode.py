import qrcode
import frappe
from io import BytesIO
import base64


@frappe.whitelist()
def generate_qr_code(doc, method):
    """Generate Patient QR Code on Patient document save"""
    print("######## QR Code Generation Started ########")
    
    try:
        if frappe.local.flags.get("qr_code_generated"):
            return
        frappe.local.flags["qr_code_generated"] = True 

        base_url = frappe.utils.get_url()
        asset_url = f"{base_url}/app/patient/{doc.name}"
        
        # Patient QR Code Data
        asset_data = (
            f"ID: {doc.name}\n"
            f"Trial ID: {doc.custom_trial_id}\n"
            f"Patient Initials: {doc.custom_patient_initials}\n"
            f"Date of birth: {doc.dob}\n"
            f"Gender: {doc.sex}\n"
            f"Blood Group: {doc.blood_group}\n"
            f"Weight on the Day of Leukapheresis (Kgs): {doc.custom_weight_on_the_day_of_leukapheresis}\n"
            f"Hospital ID (UHID): {doc.custom_hospital_id_uhid}\n"
            f"ASSET URL: {asset_url}\n"
        )

        # Generate QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(asset_data.strip())
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_data = f"data:image/png;base64,{qr_code_base64}"

        # Save to Patient document
        doc.db_set("custom_base64data", qr_code_data)

        print("######## QR Code Generated & Stored Successfully ########")

    except Exception as e:
        frappe.log_error(f"QR Code Generation Error for Patient {doc.name}: {str(e)}")


@frappe.whitelist()
def generate_cart_qr_codes(patient_id, cart_name):
    """
    Generate three different QR codes for CarT Manufacturing:
    1. Patient QR Code - Contains patient information
    2. BMR QR Code - Contains patient info + Type: BMR + Batch
    3. G-Rex QR Code - Contains patient info + Type: G-Rex + Batch
    """
    try:
        # Get patient details
        patient = frappe.get_doc('Patient', patient_id)
        patient_name = patient.patient_name or patient_id
        
        # Determine batch: use passed batch, or try common patient fields, else 'N/A'
        batch_value = batch 
        
        base_url = frappe.utils.get_url()
        patient_url = f"{base_url}/app/patient/{patient_id}"
        
        # Base patient data
        base_patient_data = (
            f"ID: {patient_id}\n"
            f"Patient Name: {patient_name}\n"
            f"Trial ID: {patient.custom_trial_id or 'N/A'}\n"
            f"Patient Initials: {patient.custom_patient_initials or 'N/A'}\n"
            f"Date of Birth: {patient.dob or 'N/A'}\n"
            f"Gender: {patient.sex or 'N/A'}\n"
            f"Blood Group: {patient.blood_group or 'N/A'}\n"
            f"Hospital ID (UHID): {patient.custom_hospital_id_uhid or 'N/A'}\n"
            f"URL: {patient_url}"
        )
        
        cart = frappe.get_doc("CarT Manufacturing", cart_name)
        batch_value = cart.batch or "N/A"
        
        # Generate Patient QR Code (original patient data)
        patient_qr_data = base_patient_data
        patient_qr_base64 = generate_qr_code_base64(patient_qr_data)
        
        # Generate BMR QR Code (batch + patient data + BMR type)
        bmr_qr_data = (
            f"Batch: {batch_value}\n"
            f"Type: BMR (Batch Manufacturing Record)\n"
            f"{base_patient_data}"
        )
        bmr_qr_base64 = generate_qr_code_base64(bmr_qr_data)
        
        # Generate G-Rex QR Code (batch + patient data + G-Rex type)
        grex_qr_data = (
            f"Batch: {batch_value}\n"
            f"Type: G-Rex\n"
            f"{base_patient_data}"
        )
        grex_qr_base64 = generate_qr_code_base64(grex_qr_data)
        
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
    Generate a QR code from data and return it as a base64 string
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5,
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