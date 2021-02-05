#include <stdio.h>
#include <stdlib.h>

#include "booster.h"

int N = 2250000;

float matrix_to_array(float *image, int rows, int cols){

	int index = 0;

	float *flattened = malloc(N * sizeof(float));

	for (int y=0; y < rows; y++){
		for (int x=0; x < cols; x++){
			flattened[index] = image[y,x];
			index++;
		}
	}
	return *flattened;
}

float** array_to_matrix(float flattened[], int rows, int cols){

	int index = 0;
	
	float **image = malloc(N * sizeof(float));

	for (int y=0; y < rows; y++){
		for (int x=0; x < cols; x++){
			image[y][x] = flattened[index];
			index++;
		}
	}
	return image;
}

float average(int arr[], int dim){
	int i;
	int sum = 0;
	float avg;
	for (i=0;i < dim ; i++){
		sum += arr[i];
	}
	avg = sum/dim;
	return avg;
}

void apply_scaling(float *scale_matrix,
		float *image,
		int mode,
		int size){
	int i;
	int j;
	for (i=0;i<size;i++){
		if (mode == 1 && scale_matrix[i] != 0){
			image[i] = image[i] * scale_matrix[i];
		} else if (mode == -1 && scale_matrix[i] !=0){ 
			image[i] = image[i] / scale_matrix[i];
		}
	}
}


void threshold(float *image,
		int mode,
		int thresh,
		int size){
	
	//mode 0 cuts lower values
	//mode 1 cuts higher values

	int i;
	if (mode==0){
		for (i=0;i<size;i++){
			if (image[i]<thresh){
				image[i] = 0.0;
			}
		}
	} else if (mode==1){
		for (i=0;i<size;i++){
			if (image[i]>thresh){
				image[i] = 0.0;
			}	
		}
	}
}

int main(){
	float arr[20] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20};
	float arr2[20] = {2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2};
	printf("\nBefore");
	for (int i=0;i<20;i++){
		printf("\n%f",arr[i]);
	}
	//apply_scaling(arr2, arr,1,20);
	threshold(arr,1,10,20);
	printf("\nAfter");
	for (int i=0;i<20;i++){
		printf("\n%f",arr[i]);
	}
	//float** avg = array_to_matrix(arr,4,5);
	return 0;
}
