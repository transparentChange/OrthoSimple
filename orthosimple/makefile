.PHONY: run

run:
	@cd orthosimple; \
	raco make init_recognize.rkt; \
	mv compiled/init_recognize_rkt.zo .; \
	racket init_recognize_rkt.zo & python3 __init__.py
