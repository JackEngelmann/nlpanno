import json
from nlpanno import domain, usecases
import sqlite3
import torch


class InMemorySampleRepository(usecases.SampleRepository):
	"""Sample repository using an in-memory list."""

	def __init__(self, samples: tuple[domain.Sample, ...]) -> None:
		self.samples = samples

	def get_by_id(self, id_: domain.Id) -> domain.Sample:
		for sample in self.samples:
			if sample.id == id_:
				return sample
		raise ValueError(f"Sample with id {id_} not found")
	
	def get_all(self) -> tuple[domain.Sample, ...]:
		return self.samples	
	
	def update(self, sample: domain.Sample) -> None:
		for i, existing_sample in enumerate(self.samples):
			if existing_sample.id == sample.id:
				self.samples[i] = sample
				return
		raise ValueError(f"Sample with id {sample.id} not found")
	
	def get_unlabeled(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self.samples if not sample.is_labeled)
	
	def get_labeled(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self.samples if sample.is_labeled)
	
	def get_unembedded(self) -> tuple[domain.Sample, ...]:
		return tuple(sample for sample in self.samples if not sample.embedding)
	
	def create(self, sample: domain.Sample) -> None:
		self.samples = self.samples + (sample,)


class SQLiteSampleRepository(usecases.SampleRepository):
	"""Sample repository using a SQLite database."""

	def __init__(self, database_path: str) -> None:
		self._database_path = database_path
	
	def __enter__(self) -> "SQLiteSampleRepository":
		self._connection = sqlite3.connect(self._database_path)
		self._create_table()
		self._connection.row_factory = sqlite3.Row
		return self
	
	def _create_table(self) -> None:
		cursor = self._connection.cursor()
		cursor.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                id TEXT PRIMARY KEY,
                text TEXT,
                embedding BLOB
            )
        """)
		cursor.execute("""
            CREATE TABLE IF NOT EXISTS estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id TEXT,
                text_class TEXT,
                confidence REAL,
				FOREIGN KEY(sample_id) REFERENCES samples(id)
            )
		""")
		self._connection.commit()
	
	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self._connection.close()
	
	def create(self, sample: domain.Sample) -> None:
		cursor = self._connection.cursor()
		embedding = None
		if sample.embedding is not None:
			list_embedding = sample.embedding.tolist()
			embedding = json.dumps(list_embedding)
		cursor.execute("INSERT INTO samples (id, text, embedding) VALUES (?, ?, ?)", (sample.id, sample.text, embedding))

		for estimate in sample.estimates:
			cursor.execute(
				"INSERT INTO estimates (sample_id, text_class, confidence) VALUES (?, ?, ?)",
				(sample.id, estimate.text_class, estimate.confidence),
			)
		self._connection.commit()
	
	def get_by_id(self, id_: domain.Id) -> domain.Sample:
		cursor = self._connection.cursor()
		cursor.execute("SELECT * FROM samples WHERE id = ?", (id_,))
		row = cursor.fetchone()
		if row is None:
			raise ValueError(f"Sample with id {id_} not found")
		sample = self._row_to_sample(row)
		cursor.execute("SELECT * FROM estimates WHERE sample_id = ?", (id_,))
		rows = cursor.fetchall()
		sample.estimates = tuple(self._row_to_estimate(row) for row in rows)
		return sample
	
	def update(self, sample: domain.Sample) -> None:
		cursor = self._connection.cursor()
		# TODO: Remove duplication with create.
		embedding = None
		if sample.embedding is not None:
			list_embedding = sample.embedding.tolist()
			embedding = json.dumps(list_embedding)
		cursor.execute("UPDATE samples SET text = ?, embedding = ? WHERE id = ?", (sample.text, embedding, sample.id))

		cursor.execute("DELETE FROM estimates WHERE sample_id = ?", (sample.id,))
		for estimate in sample.estimates:
			cursor.execute(
				"INSERT INTO estimates (sample_id, text_class, confidence) VALUES (?, ?, ?)",
				(sample.id, estimate.text_class, estimate.confidence),
			)
		self._connection.commit()
	
	def get_all(self) -> tuple[domain.Sample, ...]:
		cursor = self._connection.cursor()
		cursor.execute("SELECT * FROM samples")
		rows = cursor.fetchall()
		return tuple(self._row_to_sample(row) for row in rows)
	
	def get_unlabeled(self) -> tuple[domain.Sample, ...]:
		cursor = self._connection.cursor()
		cursor.execute("SELECT * FROM samples WHERE text IS NOT NULL")
		rows = cursor.fetchall()
		samples = tuple(self._row_to_sample(row) for row in rows)
		for sample in samples:
			cursor.execute("SELECT * FROM estimates WHERE sample_id = ?", (sample.id,))
			rows = cursor.fetchall()
			sample.estimates = tuple(self._row_to_estimate(row) for row in rows)
		return samples
	
	def get_labeled(self) -> tuple[domain.Sample, ...]:
		cursor = self._connection.cursor()
		cursor.execute("SELECT * FROM samples WHERE text IS NULL")
		rows = cursor.fetchall()
		samples = tuple(self._row_to_sample(row) for row in rows)
		for sample in samples:
			cursor.execute("SELECT * FROM estimates WHERE sample_id = ?", (sample.id,))
			rows = cursor.fetchall()
			sample.estimates = tuple(self._row_to_estimate(row) for row in rows)
		return samples
	
	def get_unembedded(self) -> tuple[domain.Sample, ...]:
		cursor = self._connection.cursor()
		cursor.execute("SELECT * FROM samples WHERE embedding IS NULL")
		rows = cursor.fetchall()
		samples = tuple(self._row_to_sample(row) for row in rows)
		for sample in samples:
			cursor.execute("SELECT * FROM estimates WHERE sample_id = ?", (sample.id,))
			rows = cursor.fetchall()
			sample.estimates = tuple(self._row_to_estimate(row) for row in rows)
		return samples
	
	def _row_to_sample(self, row: sqlite3.Row) -> domain.Sample:
		embedding = None
		if row["embedding"] is not None:
			json_embedding = json.loads(row["embedding"])
			embedding = torch.tensor(json_embedding)
		return domain.Sample(
			id=row["id"],
			text=row["text"],
			embedding=embedding,
		)
	
	def _row_to_estimate(self, row: sqlite3.Row) -> domain.ClassEstimate:
		return domain.ClassEstimate(
			text_class=row["text_class"],
			confidence=row["confidence"],
		)