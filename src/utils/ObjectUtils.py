#encoding=utf-8
from bunch import bunchify

class ObjectUtils:

    @staticmethod
    def dic_2_object(dics):
	return bunchify(dics)
