test:
	nosetests -dsv --with-yanc --with-coverage --cover-package tokenizer,index

testx:
	nosetests -dsvx --with-yanc --with-coverage --cover-package tokenizer,index

clean:
	find -regex '.*\.pyc' -exec rm {} \;
	find -regex '.*~' -exec rm {} \;
	rm -rf reg-settings.py

.PHONY:	test testx clean
