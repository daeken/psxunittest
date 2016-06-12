#include <stdio.h>

#define DAEKEN_PC 0x0EADBEE0

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
#define testExpectEqual(lval, rval) if((uint32_t)lval != (uint32_t)rval) { printf(#lval " == %i, expected " #rval "\n", lval); failed = true; }

uint32_t loadBlob(struct r3051 *cpu, uint32_t addr, int len, uint32_t *blob) {
	int i;
	for(i = 0; i < len; ++i)
		mem_writel(cpu, blob[i], addr + i * 4);
	return addr;
}

#define GetGPR(gpr) cpu->R[gpr]
#define SetGPR(gpr, val) cpu->R[gpr] = val

uint32_t cpuTest(struct r3051 *cpu) {
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
