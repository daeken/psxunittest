void runtests() {
	testStart("Arithmetic/branching test");
	cpu->Reset();
	cpu->GPR[2] = 57005;
	cpu->GPR[3] = 0;
	cpu->GPR[5] = 1;
	cpu->PokeMem8(5, 123);

	runBlob(20, {0x23, 0x10, 0x45, 0x00, 0x01, 0x00, 0x63, 0x24, 0xfd, 0xff, 0x40, 0x1c, 0x00, 0x00, 0x00, 0x00, 0xb8, 0x6f, 0x2b, 0x08});

	testAssert(cpu->GPR[2] == 0);
	testAssert(cpu->GPR[3] == 57005);
	testAssert(cpu->GPR[5] == 1);
	testAssert(cpu->PeekMem8(5) == 123);
	testEnd();

}