from random import sample
import copy
import fastapi
from nlpanno import database
from nlpanno.server import requestcontext, types, transferobject
from nlpanno.server.transferobject import to_dto
from typing import List
import dataclasses

router = fastapi.APIRouter()


@router.get('/samples', response_model=List[transferobject.SampleDTO])
def get_samples(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS
):
    all_samples = request_context.db.find_samples()
    return to_dto(all_samples)


@router.get('/taskConfig', response_model=transferobject.TaskConfigDTO)
def get_task_config(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS
):
    task_config = request_context.db.get_task_config()
    return to_dto(task_config)



@router.get('/nextSample')
def get_next_sample(
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS
):
    not_labeled = request_context.db.find_samples({ "text_class": None })
    if len(not_labeled) == 0:
        return None

    sample_id = request_context.sampler(not_labeled)
    sample = request_context.db.get_sample_by_id(sample_id)
    return to_dto(sample)


@router.patch('/samples/{sample_id}')
def patch_sample(
    sample_id: str,
    sample_patch: types.SamplePatch,
    request_context: requestcontext.RequestContext = requestcontext.DEPENDS
):
    sample = request_context.db.get_sample_by_id(sample_id)

    old_dict = dataclasses.asdict(sample)
    # Since some fields of Sample are Optional and PATCH allows partial updates,
    # it is distinguished between fields that were not given (-> don't update)
    # and fields that were given as None (-> set to None).
    update_dict = sample_patch.dict(exclude_unset=True)
    new_dict = {**old_dict, **update_dict}

    updated_sample = database.Sample(**new_dict)
    request_context.db.update_sample(updated_sample)

    # TODO: Do this always on db update? e.g. register like an
    #  event listener?
    request_context.worker.notify_data_update()

    sample = request_context.db.get_sample_by_id(sample_id)
    return to_dto(sample)
