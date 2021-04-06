#include <stdlib.h>
#include <stdio.h>
#include <shlobj.h>
#include <shlwapi.h>
#include <objbase.h>

int main(int argc, char *argv[]){
	printf("Starting patcher...");
	char *patch_exe;
	char *xismus_exe;
	patch_exe = argv[1];
	printf("\n");
	for (int i=1; i<argc; i++){
		printf("\nPATH:\n%s",argv[i]);
	}
	printf("\n%s",patch_exe);
	//if (system(patch_exe) == 0){
	if (ShellExecute(NULL, "runas", patch_exe, 0, 0, SW_SHOWNORMAL) == 0){
		printf("\nDone patching");
		if (remove(patch_exe) != 0){
			printf("\nCould not delete patch.exe");
		} else {
			printf("\nRemoved patch.exe");
			exit(1);
		}
	}
	exit(0);
}
