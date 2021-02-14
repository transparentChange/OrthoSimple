.PHONY: run

run:
	@cd orthosimple/recognizer; \
	raco make init_recognize.rkt; \
	mv compiled/init_recognize_rkt.zo .; \
	cd ..; \
	racket recognizer/init_recognize_rkt.zo & python3 __init__.py &
