#encoding=utf-8

class StringUtils:

    @staticmethod
    def parse_list_to_idstr(ids):
	if ids is not None and len(ids) > 0:
	    id_str = ''
	    for id in ids:
		id_str = id_str + "'" + id +  "'" + ","
	    return id_str[:len(id_str) - 1]

	return ''
