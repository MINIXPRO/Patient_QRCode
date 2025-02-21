import qrcode
import frappe
from io import BytesIO
import base64


@frappe.whitelist()
def generate_qr_code(doc, method):
    print("######## QR Code Generation Started ########")
    
    try:
                    
        if frappe.local.flags.get("qr_code_generated"):
            return
        frappe.local.flags["qr_code_generated"] = True 

        base_url = frappe.utils.get_url()
        asset_url = f"{base_url}/app/patient/{doc.name}"
        
          

        
        asset_data = (
            f"ID: {doc.name}\n"
            f"Trial ID: {doc.custom_trial_id}\n"
            f"Patient Initials: {doc.item_code}\n"
            f"Date of birth: {doc.custom_patient_initials}\n"
            f"Gender: {doc.sex}\n"
            f"Blood Group: {doc.blood_group}\n"
            f"Weight on the Day of Leukapheresis (Kgs): {doc.custom_weight_on_the_day_of_leukapheresis}\n"
            f"Hospital ID (UHID): {doc.custom_hospital_id_uhid}\n"
            f"ASSET URL: {asset_url}\n"
        )

        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(asset_data.strip())
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_data = f"data:image/png;base64,{qr_code_base64}"

        
        doc.db_set("custom_base64data", qr_code_data)

        # if qr_code_base64:  
        #     doc.db_set("custom_is_audited", 1)



        print("######## QR Code Generated & Stored Successfully ########")

    except Exception as e:
        frappe.log_error(f"QR Code Generation Error for Asset {doc.name}: {str(e)}")


# # Py












# import qrcode
# import frappe
# import json
# from io import BytesIO
# import base64

# @frappe.whitelist()
# def generate_qr_code(doc, **kwargs):  
#     """Generate QR Code and save in the document"""

#     print("######## QR Code Generation Started ########")

#     try:
#         # Check if doc is a string (JSON), then parse it into a dictionary
#         if isinstance(doc, str):
#             doc = json.loads(doc)

#         # Fetch the Asset document using its name if necessary
#         asset = frappe.get_doc("Patient", doc["name"])  # Use square brackets as it's now a dictionary

#         if frappe.local.flags.get("qr_code_generated"):
#             return
#         frappe.local.flags["qr_code_generated"] = True 

#         base_url = frappe.utils.get_url()
#         asset_url = f"{base_url}/app/patient/{asset.name}"

#         asset_data = (
#             f"ASSET CODE: {asset.name}\n"
#             f"ASSET NAME: {asset.asset_name}\n"
#             f"ITEM CODE: {asset.item_code}\n"
#             f"CATEGORY: {asset.asset_category}\n"
#             f"LOCATION: {asset.location}\n"
#             f"CUSTODIAN: {asset.custodian}\n"
#             f"MODEL: {asset.custom_model}\n"
#             f"SEGMENT: {asset.segment}\n"
#             f"SERIAL NUMBER: {asset.custom_serial_number}\n"
#             f"PURCHASE RECEIPT: {asset.purchase_receipt}\n"
#             f"PURCHASE DATE: {asset.purchase_date}\n"
#             f"AVAILABLE FOR USE: {asset.available_for_use_date}\n"
#             f"ASSET URL: {asset_url}\n"
#         )

#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(asset_data.strip())
#         qr.make(fit=True)
#         img = qr.make_image(fill="black", back_color="white")

#         buffer = BytesIO()
#         img.save(buffer, format="PNG")
#         qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
#         qr_code_data = f"data:image/png;base64,{qr_code_base64}"

#         asset.db_set("custom_base64data", qr_code_data)

#         # if qr_code_base64:  
#         #     asset.db_set("custom_is_audited", 1)

#         print("######## QR Code Generated & Stored Successfully ########")

#         return {"success": True, "message": "QR Code Generated Successfully!"}

#     except Exception as e:
#         frappe.log_error(f"QR Code Generation Error for Asset {doc['name'] if isinstance(doc, dict) else 'Unknown'}: {str(e)}")
#         return {"success": False, "message": str(e)}












