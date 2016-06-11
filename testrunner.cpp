void runtests() {
	testStart("Arithmetic/branching test");
	cpu->Reset();
	cpu->GPR[2] = 57005;
	cpu->GPR[3] = 0;
	cpu->GPR[5] = 1;
	cpu->PokeMem8(5, 123);

	runBlob(0x80000000, 5, {0x00451023, 0x24630001, 0x1c40fffd, 0x00000000, 0x0bab6fb8});

	testAssert(cpu->GPR[2] == 0);
	testAssert(cpu->GPR[3] == 57005);
	testAssert(cpu->GPR[5] == 1);
	testAssert(cpu->PeekMem8(5) == 123);
	testEnd();

}