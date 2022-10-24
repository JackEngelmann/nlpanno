from random import sample
import copy
import fastapi
from nlpanno import database, sampling
from nlpanno.server import dependencies, types

router = fastapi.APIRouter()


@router.get('/samples')
def get_samples(db: database.Database = dependencies.DB):
    all_samples = db.find_samples()
    return all_samples


@router.get('/nextSample')
def get_next_sample(
    db: database.Database = dependencies.DB,
    sampler: sampling.Sampler = dependencies.SAMPLER
):
    not_labeled = db.find_samples({ "text_class": None })
    if len(not_labeled) == 0:
        return None

    sample_id = sampler(not_labeled)
    return db.get_sample_by_id(sample_id)

@router.patch('/samples/{sample_id}')
def patch_sample(sample_id: str, sample_patch: types.SamplePatch, db: database.Database = dependencies.DB):
    # Since some fields of Sample are Optional and PATCH allows partial updates,
    # it is distinguished between fields that were not given (-> don't update)
    # and fields that were given as None (-> set to None).
    keys_to_update = sample_patch.dict(exclude_unset=True).keys()
    sample = db.get_sample_by_id(sample_id)
    sample_copy = copy.deepcopy(sample)
    if 'text' in keys_to_update:
        assert sample_patch.text is not None
        sample_copy.text = sample_patch.text
    if 'text_class' in keys_to_update:
        sample_copy.text_class = sample_patch.text_class
    if 'text_class_prediction' in keys_to_update:
        sample_copy.text_class_prediction = sample_patch.text_class_prediction
    db.update_sample(sample_copy)
    return db.get_sample_by_id(sample_id)
