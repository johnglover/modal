import os
import h5py
import numpy as np

data_path = os.environ.get('MODAL_DATA_PATH', os.path.realpath(__file__))
onsets_path = os.environ.get(
    'MODAL_ONSETS_PATH', os.path.join(data_path, "onsets.hdf5")
)

def _sample_and_metadata(db, file_name):
    """
    Return a dict containing a copy of a sample and all of its metadata.
    """
    data = {'name': file_name}
    data['samples'] = np.array(db[file_name], dtype=np.double)
    for attribute, value in db[file_name].attrs.iteritems():
        data[attribute] = value
    return data

def samples(file_name=None, attribute_name=None, attribute_value=None):
    """
    Return samples from Modal database.

    If a file name is given, returns a dict containing the given sample and its metadata.
    If not, returns a dict containing dicts of samples and the corresponding metadata.
    Samples can optionally be filtered by attribute name and value.
    """
    samples = {}
    db = None
    try:
        db = h5py.File(onsets_path, 'r')
        if file_name:
            samples = _sample_and_metadata(db, file_name)
        else:
            for f in db:
                if attribute_name and attribute_value:
                    if db[f].attrs[attribute_name] != attribute_value:
                        continue
                samples[f] = _sample_and_metadata(db, f)
    finally:
        if db: db.close()

    return samples

def list_onset_files():
    """
    List names of all files in the onsets database.
    Note: This is now deprecated in favour of modal.db.samples()
    """
    print "Deprecation Warning: list_onset_files() is now deprecated in favour of modal.db.samples()"
    return samples().keys()

def list_onset_files_poly():
    """
    List names of all polyphonic files in the database.
    Note: list_onset_files_poly() is now deprecated in favour of modal.db.samples()
    """
    print "Deprecation Warning: This function is now deprecated in favour of modal.db.samples()"
    return samples(None, 'texture', 'Polyphonic').keys()

def num_onsets():
    """
    Get the current number of onsets in the database.
    """
    num_onsets = 0
    try:
        onsets_db = h5py.File(onsets_path, 'r')
        for file in onsets_db:
            num_onsets += len(onsets_db[file].attrs['onsets'])
    finally:
        onsets_db.close()
    return num_onsets

def get_audio_file(file_name):
    """
    Get a given audio file from the onset database.
    """
    sample = samples(file_name)
    return (sample['samples'], sample['sampling_rate'], sample['onsets'])

