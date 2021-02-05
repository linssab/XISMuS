
__declspec(dllexport) float average(int arr[], int dim);
__declspec(dllexport) float matrix_to_array(float *image, int rows, int cols);
__declspec(dllexport) float** array_to_matrix(float arr[], int rows, int cols);
__declspec(dllexport) void apply_scaling(float arr1[], float arr2[], int mode, int shape);
__declspec(dllexport) void threshold(float arr1[],  int mode, int thresh, int shape);

