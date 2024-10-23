"""Database implementation using SQLite."""
import sqlite3
from . import base
from nlpanno import domain


class SQLiteSampleRepository(base.SampleRepository):
    """Sample repository implementation using SQLite."""

    def __init__(self, database_path: str) -> None:
        self._connection = sqlite3.connect(database_path)
        self._create_table()
        self._connection.row_factory = sqlite3.Row
    
    def _create_table(self) -> None:
        """Create the samples table."""
        cursor = self._connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS samples (id TEXT PRIMARY KEY, text TEXT, text_class TEXT)")
        self._connection.commit()
    
    def get_by_id(self, id_: domain.Id) -> domain.Sample:
        """Get a sample by the unique identifier."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM samples WHERE id = ?", (id_,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"No sample with id {id_}")
        return self._row_to_sample(row)
    
    def create(self, sample: domain.Sample) -> None:
        """Create a sample."""
        cursor = self._connection.cursor()
        cursor.execute("INSERT INTO samples (id, text, text_class) VALUES (?, ?, ?)", (sample.id, sample.text, sample.text_class))
        self._connection.commit()
    
    def get_all(self) -> tuple[domain.Sample, ...]:
        """Get all samples."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM samples")
        return tuple(self._row_to_sample(row) for row in cursor.fetchall())
    
    def update(self, sample: domain.Sample) -> None:
        """Update a sample."""
        cursor = self._connection.cursor()
        cursor.execute("UPDATE samples SET text = ?, text_class = ? WHERE id = ?", (sample.text, sample.text_class, sample.id))
        self._connection.commit()
    
    def get_unlabeled(self) -> tuple[domain.Sample, ...]:
        """Get all unlabeled samples."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM samples WHERE text_class IS NULL")
        return tuple(self._row_to_sample(row) for row in cursor.fetchall())
    
    def _row_to_sample(self, row: sqlite3.Row) -> domain.Sample:
        """Convert a row to a sample."""
        return domain.Sample(row["id"], row["text"], row["text_class"])
