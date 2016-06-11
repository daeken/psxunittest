bool failed, failedAny = false;
int state = 0;

void testStart(const char *name) {
	printf("Test: %s\n", name);
	failed = false;
}

void testEnd() {
	if(failed) {
		printf("Test failed\n");
		failedAny = true;
	} else {
		printf("Test passed\n");
	}
}
#define testExpectEqual(lval, rval) if(lval != rval) { printf(#lval " == %i, expected " #rval, lval); failed = true; }

void runtests() {
	switch(state++) {
		$TESTS$
	}

	if(state == $LASTSTATE$) {
		if(failedAny)
			exit(1);
		exit(0);
	}
}