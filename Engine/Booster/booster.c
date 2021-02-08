// booster.c
// C functions to build the dynamic libraries for python
// @author: Sergio Lins
// @email: sergio.lins@roma3.infn.it
// Version: 2.0.0 Feb - 2021

#include <stdio.h>
#include <stdlib.h>

#include "booster.h"

int N = 2250000;

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

int pos(int x, int y, int cols){
	return cols*x+y;
}

float get_pixel(float* arr,
		int x,
		int y,
		int rows,
		int cols){
	if (x==0){
		if (y==0){		//upper-left
			return (
					2*arr[pos(x,y,cols)] + 
					arr[pos(x+1,y,cols)] + 
					arr[pos(x,y+1,cols)] +
					arr[pos(x+1,y+1,cols)])/5;

		} else if (y==cols-1){	//upper-right
			return(
					2*arr[pos(x,y,cols)] + 
					arr[pos(x+1,y,cols)] + 
					arr[pos(x,y-1,cols)] +
					arr[pos(x+1,y-1,cols)])/5;

		} else {		//left-border
			return(
					2*arr[pos(x,y,cols)] +
					arr[pos(x+1,y,cols)] +
					arr[pos(x,y-1,cols)] +
					arr[pos(x,y+1,cols)] +
					arr[pos(x+1,y-1,cols)] +
					arr[pos(x+1,y+1,cols)])/7;
		}
	} else if (x==rows-1){
		if (y==0){		//bottom-left
			return(
					2*arr[pos(x,y,cols)] + 
					arr[pos(x-1,y,cols)] + 
					arr[pos(x,y+1,cols)] +
					arr[pos(x-1,y+1,cols)])/5;

		} else if (y==cols-1){	//bottom-right
			return(
					2*arr[pos(x,y,cols)] + 
					arr[pos(x-1,y,cols)] + 
					arr[pos(x,y-1,cols)] +
					arr[pos(x-1,y-1,cols)])/5;

		} else {		//right-border
			return(
					2*arr[pos(x,y,cols)] +
					arr[pos(x-1,y,cols)] +
					arr[pos(x,y-1,cols)] +
					arr[pos(x,y+1,cols)] +
					arr[pos(x-1,y-1,cols)] +
					arr[pos(x-1,y+1,cols)])/7;
		}
	} else if (y==0) {
		return( 	//upper-border
				2*arr[pos(x,y,cols)] +
				arr[pos(x-1,y,cols)] +
				arr[pos(x+1,y,cols)] +
				arr[pos(x,y+1,cols)] +
				arr[pos(x-1,y+1,cols)] +
				arr[pos(x+1,y+1,cols)])/7;		

	} else if (y==cols-1) {
		return( 	//bottom-border
				2*arr[pos(x,y,cols)] +
				arr[pos(x-1,y,cols)] +
				arr[pos(x+1,y,cols)] +
				arr[pos(x,y-1,cols)] +
				arr[pos(x-1,y-1,cols)] +
				arr[pos(x+1,y-1,cols)])/7;		
	} else {
		return(		//any other pixel
				2*arr[pos(x,y,cols)] +
				arr[pos(x-1,y,cols)] +
				arr[pos(x+1,y,cols)] +
				arr[pos(x,y-1,cols)] +
				arr[pos(x,y+1,cols)] +
				arr[pos(x-1,y-1,cols)] +
				arr[pos(x-1,y+1,cols)] +
				arr[pos(x+1,y-1,cols)] +
				arr[pos(x+1,y+1,cols)])/10;
	}
}

void apply_smooth(float *arr,
		int iter,
		int rows,
		int cols){

	int i;
	int idx = 0;
	for (i=0;i<iter+1;i++){
		//printf("\nIter = %d",i);
		for (int x=0;x<rows;x++){
			for (int y=0;y<cols;y++){
				arr[idx] = get_pixel(arr,x,y,rows,cols);
				//printf("\nIndex %d = %f",idx,arr[idx]);
				idx++;
			}
		}
		idx = 0;
	}
}

void print_arr(float *arr, int dim){
	for (int i=0;i<dim;i++){
		printf("\n%f",arr[i]);
	}
}


int main(){
	float arr[20] = {1,1,1,1,1,
			1,1,2,2,1,
			2,2,2,2,2,
			1,1,1,1,1};
	float arr2[20] = {2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2};
	printf("\nBefore");
	print_arr(arr,20);

	//apply_scaling(arr2, arr,1,20);
	//threshold(arr,1,10,20);
	
	float a;
	a = arr[pos(2,3,5)];
	
	apply_smooth(arr, 1, 4, 5);

	printf("\nAfter.");
	print_arr(arr,20);

	printf("\n pixel 2,3 (14) is %f",a);
	return 0;
}
