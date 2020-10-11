import sys
import os
import pandas as pd
import glob
import urllib
import tempfile
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, jsonify
app = Flask(__name__)

api_root = r'./'
taxonomy_path = 'https://lilablobssc.blob.core.windows.net/models/species_classification/species_classification.2019.12.00.taxa.csv'
# taxonomy_path = None
classification_model_path = 'https://lilablobssc.blob.core.windows.net/models/species_classification/species_classification.2019.12.00.pytorch'
detection_model_path = None

subdirs_to_import = ['DetectionClassificationAPI','FasterRCNNDetection','PyTorchClassification']    

image_sizes = [560, 560]
mak_k_to_print = 3
use_gpu = False

for s in subdirs_to_import:
    if (not s.lower() in map(str.lower,sys.path)):
        import_path = os.path.join(api_root,s)
        print('Adding {} to the python path'.format(import_path))
        sys.path.insert(0,import_path)    

import api as speciesapi
            
def download_url(url, destination_filename=None, progress_updater=None, force_download=False, 
                 temp_dir=None):
    if temp_dir is None:
        temp_dir = os.path.join(tempfile.gettempdir(),'species_classification')
        os.makedirs(temp_dir,exist_ok=True)
        
    # This is not intended to guarantee uniqueness, we just know it happens to guarantee
    # uniqueness for this application.
    if destination_filename is None:
        url_as_filename = url.replace('://', '_').replace('.', '_').replace('/', '_')
        destination_filename = \
            os.path.join(temp_dir,url_as_filename)
    if (not force_download) and (os.path.isfile(destination_filename)):
        print('Bypassing download of already-downloaded file {}'.format(os.path.basename(url)))
        return destination_filename
    print('Downloading file {}'.format(os.path.basename(url)),end='')
    urllib.request.urlretrieve(url, destination_filename, progress_updater)  
    assert(os.path.isfile(destination_filename))
    nBytes = os.path.getsize(destination_filename)
    print('...done, {} bytes.'.format(nBytes))
    return destination_filename

def do_latin_to_common(latin_name):
    if len(latin_to_common) == 0:
        return latin_name
    
    latin_name = latin_name.lower()
    if not latin_name in latin_to_common:
        print('Warning: latin name {} not in lookup table'.format(latin_name))
        common_name = latin_name
    else:
        common_name = latin_to_common[latin_name]
        common_name = common_name.strip()
        
    if (len(common_name) == 0):
        print('Warning: empty result for latin name {}'.format(latin_name))
        common_name = latin_name

    return common_name

classification_model_path = download_url(classification_model_path)   
if taxonomy_path is not None:
    taxonomy_path = download_url(taxonomy_path) 

latin_to_common = {}

if taxonomy_path is not None:
        
    print('Reading taxonomy file from {}'.format(taxonomy_path))
    
    # Read taxonomy file; takes ~1 minute
    df = pd.read_csv(taxonomy_path)
    df = df.fillna('')
    
    # Columns are:
    #
    # taxonID,scientificName,parentNameUsageID,taxonRank,vernacularName,wikipedia_url
    
    nRows = df.shape[0]
        
    for index, row in df.iterrows():
    
        latin_name = row['scientificName']
        latin_name = latin_name.strip()
        if len(latin_name)==0:
            print('Warning: invalid scientific name at {}'.format(index))
            latin_name = 'unknown'
        common_name = row['vernacularName']
        common_name = common_name.strip()
        latin_name = latin_name.lower()
        common_name = common_name.lower()
        latin_to_common[latin_name] = common_name
    
    print('Finished reading taxonomy file')

model = speciesapi.DetectionClassificationAPI(classification_model_path, 
                                              detection_model_path,
                                              image_sizes, 
                                              use_gpu)

# @app.route('/')
# def home():
#     return 'SPECIATE'

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
    	params = request.get_json(force=True)
    	print(params)
    	path = params['path']
    	predictions = get_prediction(path)
    return jsonify({'species': predictions})

def get_prediction(path):
	path = path.replace('\\','/')
	query = ''
	prediction = model.predict_image(path, topK=min(5,mak_k_to_print), multiCrop=False, 
	                                             predict_mode=speciesapi.PredictMode.classifyOnly)
	output_preds = []

	for i_prediction in range(0, min(len(prediction.species), mak_k_to_print)):
	    latin_name = prediction.species[i_prediction]
	    likelihood = prediction.species_scores[i_prediction]
	    likelihood = '{0:0.3f}'.format(likelihood)
	    common_name = do_latin_to_common(latin_name)
	    s = '"{}","{}","{}","{}",{}","{}","{}"'.format(
	            0, path,query,i_prediction,latin_name,common_name,likelihood)
	    output_preds.append(s)

	return output_preds

if __name__ == '__main__':
    app.run(port=5000, debug=True)    