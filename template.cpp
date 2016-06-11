#include "psx.h"

bool failed, failedAny = false;
int testState = 0;

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
#define testExpectEqual(lval, rval) if(lval != rval) { printf(#lval " == %i, expected " #rval "\n", lval); failed = true; }

uint32_t loadBlob(uint32_t addr, int len, uint32_t *blob) {
	for(int i = 0; i < len; ++i)
		cpu->PokeMem32(addr + i * 4, blob[i]);
	return addr;
}

uint32_t cpuTest() {
	uint32_t pc;
	switch(testState++) {
		$TESTS$
	}

	if(testState == $LASTSTATE$) {
		if(failedAny)
			exit(1);
		exit(0);
	}
	return pc;
}