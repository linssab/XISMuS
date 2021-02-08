// booster.h
// DLL linkage and header
// @author: Sergio Lins
// @email: sergio.lins@roma3.infn.it
// Version: 2.0.0 Feb - 2021

__declspec(dllexport) float average(int arr[], int dim);
__declspec(dllexport) void apply_scaling(float arr1[], float arr2[], int mode, int shape);
__declspec(dllexport) void apply_smooth(float arr[], int iter, int rows, int cols);
__declspec(dllexport) void threshold(float arr[],  int mode, int thresh, int shape);

