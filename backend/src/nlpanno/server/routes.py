import fastapi
from nlpanno import database, sampling
from nlpanno.server import dependencies

router = fastapi.APIRouter()


@router.get('/samples')
def get_samples(db: database.Database = dependencies.DB):
    all_samples = db.find_all()
    return all_samples


@router.get('/nextSample')
def get_next_sample(
    db: database.Database = dependencies.DB,
    sampler: sampling.Sampler = dependencies.SAMPLER
):
    not_labeled = db.find_all({ "text_class": None })
    if len(not_labeled) == 0:
        return None

    sample_id = sampler(not_labeled)
    return db.get_id(sample_id)
