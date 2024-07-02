from datetime import datetime, timezone

def get_field_default(model, field):
  return getattr(model, field).default.arg

def get_duration_seconds(time):
  return (get_utc_now() - time).total_seconds()

def parse_date(date):
  format = '%Y-%m-%dT%H:%M:%S.%f' if '.' in date else '%Y-%m-%dT%H:%M:%S'
  return datetime.strptime(date, format)

def get_utc_now():
  return datetime.now(timezone.utc).replace(tzinfo=None)

def upsert(session, model, rows):
    from sqlalchemy.dialects import postgresql
    from sqlalchemy import inspect

    table = model.__table__
    stmt = postgresql.insert(table)
    primary_keys = [key.name for key in inspect(table).primary_key]
    update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}

    if not update_dict:
        raise ValueError("insert_or_update resulted in an empty update_dict")

    stmt = stmt.on_conflict_do_update(index_elements=primary_keys,
                                      set_=update_dict)

    session.execute(stmt, rows)

class MyException(Exception):
  pass
