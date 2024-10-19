"""Implementation of the HTTP endpoints."""

import dataclasses

import fastapi

from nlpanno import data
from nlpanno.server import requestcontext, transferobject, types
from nlpanno.server.transferobject import to_dto

router = fastapi.APIRouter()


@router.get("/samples", response_model=list[transferobject.SampleDTO])
def get_samples(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> list[transferobject.SampleDTO]:
	"""Get all samples."""
	all_samples = request_context.database.find_samples()
	return to_dto(all_samples)


@router.get("/taskConfig", response_model=transferobject.TaskConfigDTO)
def get_task_config(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.TaskConfigDTO:
	"""Get the task config."""
	task_config = request_context.database.get_task_config()
	return to_dto(task_config)


@router.get("/nextSample")
def get_next_sample(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.SampleDTO | None:
	"""Get the next sample (e.g. for annotation)."""
	not_labeled = request_context.database.find_samples({"text_class": None})
	if len(not_labeled) == 0:
		return None

	sample_id = request_context.sampler(not_labeled)
	sample = request_context.database.get_sample_by_id(sample_id)
	return to_dto(sample)


@router.patch("/samples/{sample_id}")
def patch_sample(
	sample_id: str,
	sample_patch: types.SamplePatch,
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.SampleDTO:
	"""Patch (partial update) a sample."""
	sample = request_context.database.get_sample_by_id(sample_id)

	old_dict = dataclasses.asdict(sample)
	# Since some fields of Sample are Optional and PATCH allows partial updates,
	# it is distinguished between fields that were not given (-> don't update)
	# and fields that were given as None (-> set to None).
	update_dict = sample_patch.model_dump(exclude_unset=True)
	new_dict = {**old_dict, **update_dict}

	updated_sample = data.Sample(**new_dict)
	request_context.database.update_sample(updated_sample)

	# TODO: Do this always on db update? e.g. register like an
	#  event listener?
	request_context.worker.notify_data_update()

	sample = request_context.database.get_sample_by_id(sample_id)
	return to_dto(sample)


@router.get("/status")
def get_status(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.StatusDTO:
	"""Get the status of the server."""
	worker_status = request_context.worker.get_status()
	return to_dto(worker_status)
