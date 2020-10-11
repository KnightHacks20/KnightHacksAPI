#######
#
# classify_images.py
#
# This is a test driver for running our species classifier.  It classifies
# one or more hard-coded image files, writing the top N results for each
# to a .csv file.
#
# You should set the options in the 'Options' cell before running.
#
# This script has two non-code dependencies:
#
# * a classification model file.
#
# * a taxonomy file, so the scientific names used in the training data can
#   be mapped to common names.
#
# By default, both point to URLs and will be downloaded to a temp directory
# automatically.
#
# Dependencies (may work against later versions, but this was the test environment):
#
# conda install pytorch==1.2.0 torchvision==0.4.0 cudatoolkit=10.0 -c pytorch
# pip install pretrainedmodels==0.7.4
# pip install pillow==6.1.0
# pip install progressbar2==3.51.0
# pip install cupy-cuda100==7.3.0
# pip install torchnet==0.0.4
#
####### 

#%% Imports

import sys
import os
import pandas as pd
import glob
import urllib
import tempfile
import warnings
warnings.filterwarnings("ignore")

api_root = r'./'

images_to_classify_base = None
images_to_classify = [r'./test/elephant.jpg']
classification_output_file = './test/test.csv'

taxonomy_path = None
classification_model_path = 'https://lilablobssc.blob.core.windows.net/models/species_classification/species_classification.2019.12.00.pytorch'
detection_model_path = None
use_gpu = False

subdirs_to_import = ['DetectionClassificationAPI','FasterRCNNDetection','PyTorchClassification']    

# List of image sizes to use, one per model in the ensemble.  Images will be resized 
# and reshaped to square images prior to classification.  
#
# We typically specify [560,560] if we're loading our Inception/InceptionResnet 
# ensemble. For ResNext, we typically specify [448].
#
image_sizes = [560, 560]
mak_k_to_print = 3
debug_max_images = -1

#%% Path setup to import the classification code

# if (not api_root.lower() in map(str.lower,sys.path)):
    
#     print('Adding {} to the python path'.format(api_root))
#     sys.path.insert(0,api_root)

for s in subdirs_to_import:
    if (not s.lower() in map(str.lower,sys.path)):
        import_path = os.path.join(api_root,s)
        print('Adding {} to the python path'.format(import_path))
        sys.path.insert(0,import_path)    

import api as speciesapi
            
def download_url(url, destination_filename=None, progress_updater=None, force_download=False, 
                 temp_dir=None):
    '''
    Download a URL to a temporary file
    '''
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
    '''
    Latin --> common lookup
    '''
    
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


#%% Download models if necessary

classification_model_path = download_url(classification_model_path)   
if taxonomy_path is not None:
    taxonomy_path = download_url(taxonomy_path) 

#%% Build Latin --> common mapping

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


#%% Create the model(s)

# print('Loading model')
# model = speciesapi.DetectionClassificationAPI(classification_model_path, 
#                                               detection_model_path,
#                                               image_sizes, 
#                                               use_gpu)
# print('Finished loading model')


#%% Prepare the list of images and query names

# if isinstance(images_to_classify,str):
#     images_to_classify = [images_to_classify]
# assert isinstance(images_to_classify,list)
# images = images_to_classify
# print('Processing a list of {} images'.format(len(images)))

# n_errors = 0
# n_images_classified = 0
# n_images = len(images)

# if classification_output_file is not None:
#     f = open(classification_output_file,'w+')

# # i_fn = 1; fn = images[i_fn]    
# for i_fn,fn in enumerate(images):
    
#     print('Processing image {} of {}'.format(i_fn,n_images))
#     fn = fn.replace('\\','/')
#     query = ''
        
#     if images_to_classify_base is not None:
#         fn = os.path.join(images_to_classify_base,fn)

#     # with torch.no_grad():
#     # print('Clasifying image {}'.format(fn))
#     # def predict_image(self, image_path, topK=1, multiCrop=False, predict_mode=PredictMode.classifyUsingDetect):
#     try:
#         prediction = model.predict_image(fn, topK=min(5,mak_k_to_print), multiCrop=False, 
#                                              predict_mode=speciesapi.PredictMode.classifyOnly)
#         n_images_classified = n_images_classified + 1
        
#     except Exception as e:
#         print('Error classifying image {} ({}): {}'.format(i_fn,fn,str(e)))
#         n_errors = n_errors + 1
#         continue

#     # i_prediction = 0
#     for i_prediction in range(0, min(len(prediction.species), mak_k_to_print)):
#         latin_name = prediction.species[i_prediction]
#         likelihood = prediction.species_scores[i_prediction]
#         likelihood = '{0:0.3f}'.format(likelihood)
#         common_name = do_latin_to_common(latin_name)
#         s = '"{}","{}","{}","{}",{}","{}","{}"'.format(
#                 i_fn,fn,query,i_prediction,latin_name,common_name,likelihood)
#         if classification_output_file is not None:
#             f.write(s + '\n')
        
#     if debug_max_images > 0 and i_fn >= debug_max_images:
#         break
        
# if classification_output_file is not None:
#     f.close()
    
# print('Finished classifying {} of {} images ({} errors)'.format(n_images_classified,n_images,n_errors))
