"""Implementation of the HTTP endpoints."""

import dataclasses

import fastapi
import fastapi.staticfiles
import fastapi.templating

from nlpanno import data
from nlpanno.server import requestcontext, status, transferobject, types, static

router = fastapi.APIRouter(prefix="/api")


@router.get("/samples")
def get_samples(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> list[transferobject.SampleDTO]:
	"""Get all samples."""
	all_samples = request_context.database.find_samples()
	return [transferobject.SampleDTO.from_domain_object(sample) for sample in all_samples]


@router.get("/taskConfig", response_model=transferobject.TaskConfigDTO)
def get_task_config(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.TaskConfigDTO:
	"""Get the task config."""
	return transferobject.TaskConfigDTO.from_domain_object(request_context.task_config)


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
	return transferobject.SampleDTO.from_domain_object(sample)


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

	request_context.worker.notify_data_update()

	sample = request_context.database.get_sample_by_id(sample_id)
	return transferobject.SampleDTO.from_domain_object(sample)


@router.get("/status")
def get_status(
	request_context: requestcontext.RequestContext = requestcontext.DEPENDS,
) -> transferobject.StatusDTO:
	"""Get the status of the server."""
	worker_status = request_context.worker.get_status()
	app_status = status.Status(worker_status)
	return transferobject.StatusDTO.from_domain_object(app_status)
