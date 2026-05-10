from pydoc import text

from anthropic import Anthropic

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter

import os

import dotenv

dotenv.load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
model_name = os.getenv("MODEL_NAME")
client = Anthropic(api_key = api_key)

# Get the absolute path of the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DRILLING_PATH = os.path.join(BASE_DIR, "backend", "data", "raw_documents", "drilling")
REFINERY_PATH = os.path.join(BASE_DIR, "backend", "data", "raw_documents", "refinery")

os.makedirs(DRILLING_PATH, exist_ok=True)
os.makedirs(REFINERY_PATH, exist_ok=True)


BASE_PROMPT = """
You are generating synthetic technical equipment documentation for an oil and gas company.
These documents are realistic but entirely fictional — no real proprietary data is used.
All safety procedures must align with OSHA and API industry standards.
Write in formal technical documentation style. Be specific and detailed.
Use realistic but fictional company names, part numbers, and engineer names.

Every document must follow this structure for identity information:

Company_Name: {company_name}
Field_Engineer: {field_engineer}
Field_Engineer_Id: {field_engineer_id}
Document_Version: {document_version}

Machine_Name: {machine_name}
Machine_Id: {machine_id}
Installation_Date: {installation_date}
Number_Of_Units_In_Machine: {number_of_units_in_machine}

For each unit include:
Unit_Name: {unit_name}
Unit_Id: {unit_id}
Manufacture_Date: {manufacture_date}
Manufacturer_Company_Name: {manufacturer_company_name}
Manufacturer_Company_Id: {manufacturer_company_id}
Inventory_Quantity: {inventory_quantity}
Supplier_Information: {supplier_information}

Domain-specific technical details will be appended per document type.
Ensure all procedures comply with OSHA 1910 and API RP 54 standards.
"""

def save_as_pdf(content, filename, folder_path):
    file_path = os.path.join(folder_path, filename)
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    story = []
    for line in content.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1,6))

    doc.build(story)

    print (f"Saved document to: {file_path}")

def generate_drilling_document():
    equipment_list = ["Top Drive System", "Blowout Preventer", "Mud Pump", "Drill Bit", "Rotary Table"]

    for equipment in equipment_list:
        prompt = prompt = BASE_PROMPT + f"""
        Generate a detailed technical document for: {equipment}

        IMPORTANT INSTRUCTIONS:
        - Be concise in each section. Use bullet points not paragraphs.
        - You MUST complete ALL four sections. Do not stop mid-document.
        - Keep each section to maximum 10 bullet points.
        - If running low on space, summarize remaining points briefly but ALWAYS complete all sections.

        For each unit in this equipment include:

        DOMAIN SPECIFICATIONS:
        - Wellbore_Depth_Rating:
        - Operating_Pressure_PSI:
        - Drilling_Fluid_Compatibility:
        - Known_Error_Codes:
        - Replacement_Part_Number:
        - Maintenance_Schedule:

        SECTION 1 - USE CASE (max 5 bullet points):
        Describe the function and operational role of this unit.

        SECTION 2 - FAILURE CAUSES (max 5 bullet points):
        List known failure modes ranked by frequency with error codes.

        SECTION 3 - SOLUTIONS (max 5 bullet points):
        Corrective actions aligned with API RP 54 and OSHA 1910 standards.

        SECTION 4 - INVENTORY DATA (max 4 bullet points):
        Stock quantity, reorder threshold, supplier, lead time.

        Complete all four sections before ending the document.
        """
        
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.content[0].text.strip()
        filename = f"{equipment.replace(' ', '_')}_Documentation.pdf"
        save_as_pdf(content, filename, DRILLING_PATH)

def generate_refinery_document():
    equipment_list = ["Heat Exchanger", "Distillation Column", "Centrifugal Pump", "Pressure Vessel", "Compressor"]

    for equipment in equipment_list:
        prompt = prompt = BASE_PROMPT + f"""
        Generate a detailed technical document for: {equipment}

        IMPORTANT INSTRUCTIONS:
        - Be concise in each section. Use bullet points not paragraphs.
        - You MUST complete ALL four sections. Do not stop mid-document.
        - Keep each section to maximum 10 bullet points.
        - If running low on space, summarize remaining points briefly but ALWAYS complete all sections.

        For each unit in this equipment include:

        DOMAIN SPECIFICATIONS:
        - Wellbore_Depth_Rating:
        - Operating_Pressure_PSI:
        - Drilling_Fluid_Compatibility:
        - Known_Error_Codes:
        - Replacement_Part_Number:
        - Maintenance_Schedule:

        SECTION 1 - USE CASE (max 5 bullet points):
        Describe the function and operational role of this unit.

        SECTION 2 - FAILURE CAUSES (max 5 bullet points):
        List known failure modes ranked by frequency with error codes.

        SECTION 3 - SOLUTIONS (max 5 bullet points):
        Corrective actions aligned with API RP 54 and OSHA 1910 standards.

        SECTION 4 - INVENTORY DATA (max 4 bullet points):
        Stock quantity, reorder threshold, supplier, lead time.

        Complete all four sections before ending the document.
        """
        
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.content[0].text.strip()
        filename = f"{equipment.replace(' ', '_')}_Documentation.pdf"
        save_as_pdf(content, filename, REFINERY_PATH)
    

if __name__ == "__main__":
    print("Starting document generation pipeline...")
    generate_drilling_document()
    print(f"Drilling documents generated successfully in the {DRILLING_PATH} directory.")
    generate_refinery_document()
    print(f"Refinery documents generated successfully in the {REFINERY_PATH} directory.")
    print("Document generation pipeline complete.")