from datetime import datetime, timezone

def get_field_default(model, field):
  return getattr(model, field).default.arg

def get_duration_seconds(time):
  return (get_utc_now() - time).total_seconds()

def format_date(date):

  format = '%Y-%m-%dT%H:%M:%S'

  if len('2023-03-22T23:03:20') == len(str(date)):
    return datetime.strptime(date, format)

  return datetime.strptime(date, format + '.%f')

def get_utc_now():
  return datetime.now(timezone.utc).replace(tzinfo=None)
