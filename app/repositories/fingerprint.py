from typing import List

from ..models import Fingerprint, Song, db


class FingerprintRepository:
    def __init__(self, db=db) -> None:
        self.db = db

    def upsert(self, fingerprint, song: Song):
        try:
            fingerprint_db = self.get_by_id(
                fingerprint.id) if hasattr(fingerprint, "id") else None

            if not fingerprint_db:
                fingerprint_db = Fingerprint()

            fingerprint_db.hash = fingerprint["hash"]
            fingerprint_db.offset = int(fingerprint["offset"])
            fingerprint_db.song = song

            self.db.session.add(fingerprint_db)
            self.db.session.commit()

            return fingerprint_db
        except Exception as ex:
            self.db.session.rollback()

            return None

    def get_by_id(self, id: int) -> Fingerprint:
        return Fingerprint.query.filter_by(id=id).first()

    def get_by_hash(self, hash) -> Fingerprint:
        return Fingerprint.query.filter_by(hash=hash).first()

    def get_all_by_hashes(self, hashes) -> List[Fingerprint]:
        return Fingerprint.query.filter(Fingerprint.hash.in_(hashes)).all()
