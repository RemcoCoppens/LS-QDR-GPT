from flask import Flask, send_from_directory, request, jsonify, render_template
import os
from model.process_document import ProcessDocument
from label_studio_sdk import Client
from datetime import datetime
import re

app = Flask(__name__)

@app.route('/')
def index():
    projects = get_ls_projects()
    return render_template('upload.html', projects=projects)

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/favicon.ico')
def favicon():
    print("Favicon route accessed")
    return send_from_directory('static', 'favicon.ico')

@app.route('/process', methods=['POST'])
def process():
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    
    files = request.files.getlist('files')
    project_name = request.form.get('project_name')
    if project_name:
        project_title = project_name
    else:
        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        project_title = f"PDF Annotations {current_timestamp}"

    ls_data_ingestion, response_data, uploaded_files = [], [], []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join('/tmp', file.filename)
            file.save(pdf_path)
             
            doc = ProcessDocument(file_path=pdf_path)
            text, labels = doc.get_LS_output()
            ls_data_ingestion.append(prepare_task(raw_text=text, labels=labels))

            uploaded_files.append(file.filename)
            response_data.append({"filename": file.filename, "status": "Processed"})
        else:
            response_data.append({"filename": file.filename, "status": "Invalid file format"})

    upload_to_label_studio(
        data=ls_data_ingestion,
        project_title=project_title
    )
    # return jsonify({"message": f"Processing completed, Data uploaded to Label Studio project: {project_title}", "details": response_data}), 200
    return render_template('process.html', project_name=project_title, uploaded_files=uploaded_files)

def get_ls_projects() -> list:
    client = Client(url='http://localhost:8080', api_key='423d3ad2f3f42774c15cf061ffa569137dc57334')
    projects = client.get_projects()
    return [project.title for project in projects]

def get_spans(text:str, attributes:dict, only_first_occurrence:bool=True) -> list:
    spans = []
    for label, values in attributes.items():
        if not isinstance(values, list):
            values = [values]
        for value in values:
            pattern = re.escape(value)
            for match in re.finditer(pattern, text):
                spans.append({
                    'text': match.group(),
                    'label': label,
                    'start': match.start(),
                    'end': match.end()
                })
                if only_first_occurrence:
                    break
    return spans

def prepare_task(raw_text:str, labels:dict) -> dict:   
    results = []
    cleaned_labels = {key: value for key, value in labels.items() if value is not None}

    for span in get_spans(text=raw_text, attributes=cleaned_labels):
        results.append({
            'from_name': 'label',
            'to_name': 'text',
            'type': 'labels',
            'value': {
                'start': span['start'],
                'end': span['end'],
                'text': span['text'],
                'labels': [span['label']]
            },
            'readonly': False,
            'hidden': False
        })

    return {
        'data': {
            'text': raw_text
        },
        'annotations': [{
            'model_version': 'beta_V1',
            'result': results
        }]
    }

def upload_to_label_studio(data:list, project_title:str) -> None:
    client = Client(url='http://localhost:8080', api_key='423d3ad2f3f42774c15cf061ffa569137dc57334')
    project = get_project_by_title(client, project_title)
    if not project:
        project = client.start_project(title=project_title, label_config="""
        <View>
        <Labels name="label" toName="text">
            <Label value="klant_naam"></Label>
            <Label value="gebouw_naam"></Label>
            <Label value="adres"></Label>
            <Label value="soort_installatie"></Label>
            <Label value="element_merk"></Label>
            <Label value="element_type"></Label>
            <Label value="element_ID"></Label>
            <Label value="ruimte_nummer"></Label>
            <Label value="ruimte_omschrijving"></Label>
            <Label value="datum_van_keuring"></Label>
            <Label value="keuringsresultaat"></Label>
            <Label value="herstel_acties"></Label>
            <Label value="gebreken"></Label>
            <Label value="opmerkingen"></Label>
            <Label value="tijdsbesteding_monteur"></Label>
            <Label value="conditie"></Label>
            <Label value="datum_van_onderhoud_en_inspectie"></Label>
            <Label value="uitgevoerd_onderhoud"></Label>
        </Labels>
        <Text name="text" value="$text"></Text>
        </View>
        """)
    
    project.import_tasks(data)

def get_project_by_title(client, title):
    projects = client.get_projects()
    for project in projects:
        if project.title == title:
            return project
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
