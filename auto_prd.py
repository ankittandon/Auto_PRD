import fitz
import base64
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from anthropic import Anthropic
import requests
import os

# Set up the Anthropic API client
MODEL_NAME = "claude-3-haiku-20240229"

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    raise ValueError("No API key found in environment variables. Make sure ANTHROPIC_API_KEY is set in your .env file.")

client = Anthropic(
    api_key=anthropic_api_key,
)

# Step 2 Gather Documents and ask a question
# List of Apple's earnings release PDF URLs
pdf_urls = [
    "https://www.apple.com/newsroom/pdfs/fy2023-q4/FY23_Q4_Consolidated_Financial_Statements.pdf",
    "https://www.apple.com/newsroom/pdfs/fy2023-q3/FY23_Q3_Consolidated_Financial_Statements.pdf",
    "https://www.apple.com/newsroom/pdfs/FY23_Q2_Consolidated_Financial_Statements.pdf",
    "https://www.apple.com/newsroom/pdfs/FY23_Q1_Consolidated_Financial_Statements.pdf"
]

# User's question
QUESTION = "What are the key trends in Apple's revenue across these quarters?"  # Or whatever question you want to ask

# Step 3 Download and Convert PDFs
# Function to download a PDF file from a URL and save it to a specified folder
def download_pdf(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(folder, url.split("/")[-1])
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    else:
        print(f"Failed to download PDF from {url}")
        return None
    
# Define the function to convert a PDF to a list of base64-encoded PNG images
def pdf_to_base64_pngs(pdf_path, quality=75, max_size=(1024, 1024)):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    base64_encoded_pngs = []

    # Iterate through each page of the PDF
    for page_num in range(doc.page_count):
        # Load the page
        page = doc.load_page(page_num)

        # Render the page as a PNG image
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))

        # Convert the pixmap to a PIL Image
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Resize the image if it exceeds the maximum size
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert the PIL Image to base64-encoded PNG
        image_data = io.BytesIO()
        image.save(image_data, format='PNG', optimize=True, quality=quality)
        image_data.seek(0)
        base64_encoded = base64.b64encode(image_data.getvalue()).decode('utf-8')
        base64_encoded_pngs.append(base64_encoded)

    # Close the PDF document
    doc.close()

    return base64_encoded_pngs

# Folder to save the downloaded PDFs
folder = "../images/using_sub_agents"


# Create the directory if it doesn't exist, using exist_ok=True
os.makedirs(folder, exist_ok=True)

# Download the PDFs concurrently
with ThreadPoolExecutor() as executor:
    pdf_paths = list(executor.map(download_pdf, pdf_urls, [folder] * len(pdf_urls)))

# Remove any None values (failed downloads) from pdf_paths
pdf_paths = [path for path in pdf_paths if path is not None]


# Step 4 Generate a specific prompt for Haiku using Opus
def generate_haiku_prompt(question):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Based on the following question, please generate a specific prompt for an LLM sub-agent to extract relevant information from an earning's report PDF. Each sub-agent only has access to a single quarter's earnings report. Output only the prompt and nothing else.\n\nQuestion: {question}"}
            ]
        }
    ]

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2048,
        messages=messages
    )

    return response.content[0].text
    
haiku_prompt = generate_haiku_prompt(QUESTION)
print(haiku_prompt)


# Step 5 Extract Information from PDFs
def extract_info(pdf_path, haiku_prompt):
    base64_encoded_pngs = pdf_to_base64_pngs(pdf_path)
    
    messages = [
        {
            "role": "user",
            "content": [
                *[{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_encoded_png}} for base64_encoded_png in base64_encoded_pngs],
                {"type": "text", "text": haiku_prompt}
            ]
        }
    ]
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2048,
        messages=messages
    )
    
    return response.content[0].text, pdf_path

def process_pdf(pdf_path):
    return extract_info(pdf_path, haiku_prompt)

# Process the PDFs concurrently with Haiku sub-agent models
with ThreadPoolExecutor() as executor:
    extracted_info_list = list(executor.map(process_pdf, pdf_paths))

extracted_info = ""
# Display the extracted information from each model call
for info in extracted_info_list:
    extracted_info += "<info quarter=\"" + info[1].split("/")[-1].split("_")[1] + "\">" + info[0] + "</info>\n"
print(extracted_info)

# Step 6 Pass information to Opus
# Prepare the messages for the powerful model
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": f"Based on the following extracted information from Apple's earnings releases, please provide a response to the question: {QUESTION}\n\nAlso, please generate Python code using the matplotlib library to accompany your response. Enclose the code within <code> tags.\n\nExtracted Information:\n{extracted_info}"}
        ]
    }
]

# Generate the matplotlib code using the powerful model
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=4096,
    messages=messages
)

generated_response = response.content[0].text
print("Generated Response:")
print(generated_response)

# Step 6 Extract response and execute Matplotlib code
# Extract the matplotlib code from the response
# Function to extract the code and non-code parts from the response
def extract_code_and_response(response):
    start_tag = "<code>"
    end_tag = "</code>"
    start_index = response.find(start_tag)
    end_index = response.find(end_tag)
    if start_index != -1 and end_index != -1:
        code = response[start_index + len(start_tag):end_index].strip()
        non_code_response = response[:start_index].strip()
        return code, non_code_response
    else:
        return None, response.strip()

matplotlib_code, non_code_response = extract_code_and_response(generated_response)

print(non_code_response)
if matplotlib_code:

    # Execute the extracted matplotlib code
    exec(matplotlib_code)
else:
    print("No matplotlib code found in the response.")