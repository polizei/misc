# encoding: utf-8

from re import match as rmatch, sub as rsub, I

class Inflector:
	'''Inflector for common english words and other text-transformation functions, such as underscore/camelize'''

	_singular = [
		[r's$'										, r''],
		[r'(n)ews$'									, r'\1ews'],
		[r'([dti])a$'								, r'\1um'],
		[r'((a)naly|(b)a|(d)iagno|(p)arenthe|(p)rogno|(s)ynop|(t)he)ses$', r'\1\2sis'],
		[r'(^analy)ses$'							, r'\1sis'],
		[r'([^f])ves$'								, r'\1fe'],
		[r'(hive)s$'								, r'\1'],
		[r'(tive)s$'								, r'\1'],
		[r'([lr])ves$'								, r'\1f'],
		[r'([^aeiouy]|qu)ies$'						, r'\1y'],
		[r'(s)eries$'								, r'\1eries'],
		[r'(m)ovies$'								, r'\1ovie'],
		[r'(x|ch|ss|sh)es$'							, r'\1'],
		[r'([m|l])ice$'								, r'\1ouse'],
		[r'(bus)es$'								, r'\1'],
		[r'(o)es$'									, r'\1'],
		[r'(shoe)s$'								, r'\1'],
		[r'(ax|cris|diagnos|test)es$'				, r'\1is'],
		[r'(alumn|cact|fung|octop|vir)i$'			, r'\1us'],
		[r'(alias|status)es$'						, r'\1'],
		[r'^(ox)en'									, r'\1'],
		[r'(vert|ind)ices$'							, r'\1ex'],
		[r'(append|matr)ices$'						, r'\1ix'],
		[r'(quiz)zes$'								, r'\1'],
		[r'(database)s$'							, r'\1'],
	]
	_plural = [
		[r'$'										, r's'],
		[r's$'										, r's'],
		[r'(ax|test)is$'							, r'\1es'],
		[r'(alumn|cact|fung|octop|vir)us$'			, r'\1i'],
		[r'(alias|status)$'							, r'\1es'],
		[r'(bu)s$'									, r'\1ses'],
		[r'(buffal|tomat)o$'						, r'\1oes'],
		[r'([dti])um$'								, r'\1a'],
		[r'sis$'									, r'ses'],
		[r'(?:([^f])fe|([lr])f)$'					, r'\1\2ves'],
		[r'(hive)$'									, r'\1s'],
		[r'([^aeiouy]|qu)y$'						, r'\1ies'],
		[r'(x|ch|ss|sh)$'							, r'\1es'],
		[r'(append|ind|matr|vert)(?:ix|ex)$'		, r'\1ices'],
		[r'([m|l])ouse$'							, r'\1ice'],
		[r'^(ox)$'									, r'\1en'],
		[r'(quiz)$'									, r'\1zes'],
	]
	_irregular = [
		['person'									, 'people'],
		['man'										, 'men'],
		['human'									, 'humans'],
		['child'									, 'children'],
		['sex'										, 'sexes'],
		['move'										, 'moves'],
	]
	_uncountable = [
		['equipment'								, 'equipment'],
		['information'								, 'information'],
		['rice'										, 'rice'],
		['money'									, 'money'],
		['species'									, 'species'],
		['series'									, 'series'],
		['fish'										, 'fish'],
		['sheep'									, 'sheep'],
	]
	_unaccent = {
		r'À': 'A', r'Á': 'A', r'Â': 'A', r'Ã': 'A', r'Ä': 'A', r'Å': 'A', r'Æ': 'A', r'Ç': 'C',
		r'È': 'E', r'É': 'E', r'Ê': 'E', r'Ë': 'E', r'Ì': 'I', r'Í': 'I', r'Î': 'I', r'Ï': 'I',
		r'Ð': 'D', r'Ñ': 'N', r'Ò': 'O', r'Ó': 'O', r'Ô': 'O', r'Õ': 'O', r'Ö': 'O', r'Ø': 'O',
		r'Ù': 'U', r'Ú': 'U', r'Û': 'U', r'Ü': 'U', r'Ý': 'Y', r'Þ': 'T', r'ß': 's', r'à': 'a',
		r'á': 'a', r'â': 'a', r'ã': 'a', r'ä': 'a', r'å': 'a', r'æ': 'a', r'ç': 'c', r'è': 'e',
		r'é': 'e', r'ê': 'e', r'ë': 'e', r'ì': 'i', r'í': 'i', r'î': 'i', r'ï': 'i', r'ð': 'e',
		r'ñ': 'n', r'ò': 'o', r'ó': 'o', r'ô': 'o', r'õ': 'o', r'ö': 'o', r'ø': 'o', r'ù': 'u',
		r'ú': 'u', r'û': 'u', r'ü': 'u', r'ý': 'y', r'þ': 't', r'ÿ': 'y'
	}
	_latinize = {
		'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ж': 'Zh', 'З': 'Z',
		'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
		'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'Ch',
		'Ш': 'Sh', 'Щ': 'Sht', 'Ъ': 'Y', 'Ь': 'I', 'Ю': 'Ju', 'Я': 'Ja',
		'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh', 'з': 'z',
		'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
		'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
		'ш': 'sh', 'щ': 'sht', 'ъ': 'y', 'ь': 'i', 'ю': 'ju', 'я': 'ja',
	}

	@classmethod
	def singularize(cls, what):
		'''Singularizes english words (example: people => person, sheep => sheep, lines => line)'''

		for x in range(len(cls._uncountable) - 1, -1, -1):
			value = cls._uncountable[x][0]

			if value == what[-len(value):].lower():
				return what

		for x in range(len(cls._irregular) - 1, -1, -1):
			key = cls._irregular[x][1]
			value = cls._irregular[x][0]

			if key == what[-len(key):].lower():
				return what[:-len(key)] + value

		for x in range(len(cls._singular) - 1, -1, -1):
			key = cls._singular[x][0]
			value = cls._singular[x][1]

			if rmatch(key, what, I):
				return rsub(key, value, what, I)

		return what

	@classmethod
	def pluralize(cls, what):
		'''Pluralizes english words (example: person => people, news => news, post => posts)'''

		for x in range(len(cls._uncountable) - 1, -1, -1):
			value = cls._uncountable[x][0]

			if value == what[-len(value):].lower():
				return what

		for x in range(len(cls._irregular) - 1, -1, -1):
			key = cls._irregular[x][0]
			value = cls._irregular[x][1]

			if key == what[-len(key):].lower():
				return what[:-len(key)] + value

		for x in range(len(cls._plural) - 1, -1, -1):
			key = cls._plural[x][0]
			value = cls._plural[x][1]

			if rmatch(key, what, I):
				return rsub(key, value, what, I)

		return what

	@classmethod
	def camelize(cls, what):
		'''Camelizes given word (example: blog_posts => BlogPosts, who's online? => WhoSOnline)'''

		return what.replace('_', ' ').title()

	@classmethod
	def underscore(cls, what):
		'''Underscores a camelized word (example: BlogPosts => blog_posts, MyDBConnector => my_db_connector)'''

		return rsub('([A-Z]+)', r'_\1', rsub('([A-Z]+)([A-Z][a-z])', r'_\1_\2', what)).lstrip('_').lower()

	@classmethod
	def classify(cls, what):
		'''Returns the corresponding class name for a table name (example: blog_posts => BlogPost, people => Person)'''

		return cls.camelize(cls.singularize(what))

	@classmethod
	def tableize(cls, what):
		'''Returns the corresponding table name for a class name (example: Person => people, BlogPost => blog_posts)'''

		return cls.underscore(cls.pluralize(what))

	@classmethod
	def unaccent(cls, what):
		'''Replaces accented characters with standard latin ones (example: Köln => Koln)'''

		for key in cls._unaccent:
			what = what.replace(key, cls._unaccent[key])

		return what

	@classmethod
	def latinize(cls, what):
		'''Replaces UTF8 cyrillic with latin equivalents (example: 'манджа' => 'mandzha')'''

		for key in cls._latinize:
			what = what.replace(key, cls._latinize[key])

		return what

	@classmethod
	def urlize(cls, what, delimiter='_'):
		'''Returns the sentense passed as a URL slug (example: what's goin' on out there? => what_s_goin_on_out_there)'''

		return rsub(delimiter + '+', delimiter, rsub('[^0-9a-z]', delimiter, cls.underscore(cls.unaccent(cls.latinize(what))))).strip(delimiter)
