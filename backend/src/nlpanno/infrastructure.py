import abc
from typing import Self
from nlpanno import usecases


class Session(abc.ABC):
	"""Base class for database sessions."""

	@abc.abstractmethod
	def __enter__(self) -> Self:
		raise NotImplementedError()

	@abc.abstractmethod
	def __exit__(self, exc_type, exc_value, traceback) -> None:
		raise NotImplementedError()

	@property
	@abc.abstractmethod
	def sample_repository(self) -> usecases.SampleRepository:
		raise NotImplementedError()

	@abc.abstractmethod
	def commit(self) -> None:
		raise NotImplementedError()
	
	@abc.abstractmethod
	def create_tables(self) -> None:
		raise NotImplementedError()


class SessionFactory(abc.ABC):
	"""Base class for session factories."""

	@abc.abstractmethod
	def __call__(self) -> Session:
		raise NotImplementedError()
