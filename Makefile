test:
	nosetests -dsv --with-yanc --with-coverage --cover-package tokenizer,index

testx:
	nosetests -dsvx --with-yanc --with-coverage --cover-package tokenizer,index

.PHONY:	test testx
