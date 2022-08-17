from ..models import Song, db


class SongRepository:
    def __init__(self, db=db) -> None:
        self.db = db

    def upsert(self, song):
        try:
            song_db = self.get_by_id(song.id) if hasattr(song, "id") else None

            if not song_db:
                song_db = Song()

            song_db.name = song["name"]
            song_db.file_hash = song["file_hash"]

            self.db.session.add(song_db)
            self.db.session.commit()

            return song_db
        except Exception as ex:
            self.db.session.rollback()

            return None

    def get_by_id(self, id: int) -> Song:
        return Song.query.filter_by(id=id).first()

    def get_by_file_hash(self, file_hash: str) -> Song:
        return Song.query.filter_by(file_hash=file_hash).first()
