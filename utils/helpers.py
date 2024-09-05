# get object from tabel, return None if not exist
def get_or_none(model_class, **kwargs):
	try:
		return model_class.objects.get(**kwargs)
	except model_class.DoesNotExist:
		return None
