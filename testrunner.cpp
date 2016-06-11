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
		case 0: {
			testStart("ADD 1");
			cpu->Reset();
			cpu->GPR[1] = 10;
			cpu->GPR[2] = -15;
		
			uint32_t blob_1[] = {0x00201820, 0x00222020, 0x00412820, 0x00423020, 0x082b6fb8};
			loadBlob(0x80000000, 5, blob_1);
			break;
		}
		
		case 1: {
			testExpectEqual(cpu->GPR[1], 10);
			testExpectEqual(cpu->GPR[2], -15);
			testExpectEqual(cpu->GPR[3], 10);
			testExpectEqual(cpu->GPR[4], -5);
			testExpectEqual(cpu->GPR[5], -5);
			testExpectEqual(cpu->GPR[6], -30);
			testEnd();
		
			testStart("Arithmetic/branching test");
			cpu->Reset();
			cpu->GPR[2] = 57005;
			cpu->GPR[3] = 0;
			cpu->GPR[5] = 1;
			cpu->PokeMem8(5, 123);
		
			uint32_t blob_2[] = {0x00451023, 0x24630001, 0x1c40fffd, 0x00000000, 0x082b6fb8};
			loadBlob(0x80000000, 5, blob_2);
			break;
		}
		
		case 3: {
			testExpectEqual(cpu->GPR[2], 0);
			testExpectEqual(cpu->GPR[3], 57005);
			testExpectEqual(cpu->GPR[5], 1);
			testExpectEqual(cpu->PeekMem8(5), 123);
			testEnd();
			break;
		}
	}

	if(state == 3) {
		if(failedAny)
			exit(1);
		exit(0);
	}
}
