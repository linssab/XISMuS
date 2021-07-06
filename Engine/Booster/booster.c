// booster.c
// C functions to build the dynamic libraries for python
// @author: Sergio Lins
// @email: sergio.lins@roma3.infn.it
// Version: 2.0.0 Feb - 2021

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "booster.h"

int N = 2250000;
#define ARRAYSIZE(a) (sizeof(a) / sizeof(a[0]))

void print_arr(float *arr, int dim){
	for (int i=0;i<dim;i++){
		printf("\n%f",arr[i]);
	}
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

void apply_brightness(float *image,
		int rows,
		int cols,
		float value,
		int direction,
		int mode,
		int bound){

	/* 
	 * value = scaling factor
	 * direction 0 = upwards or left
	 * direction 1 = downwards or right
	 * mode 0 = vertical scan
	 * mode 1 = horizontal scan
	 * bound = row or column delimiting the filter
	 */ 

	int size = rows * cols;
	for(int i=0; i < rows; i++){
		for(int j=0; j < cols; j++){
			if(mode == 0){
				if(direction == 0 && i <= bound){image[ pos(i, j, cols) ] *= value;}
				else{if(direction == 1 && i >= bound){image[ pos(i, j, cols) ] *= value;}}
			}else{
				if(mode == 1){
					if(direction == 0 && j <= bound){image[ pos(i, j, cols) ] *= value;}
					else{if(direction == 1 && j >= bound){image[ pos(i, j, cols) ] *= value;}}
				}
			}
		}
	}
}

void apply_scaling(float *scale_matrix,
		float *image,
		int mode,
		int size){
	int i;
	int j;
	for (i=0;i<size;i++){
		if (mode == 1){
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
		for (int x=0;x<rows;x++){
			for (int y=0;y<cols;y++){
				arr[idx] = get_pixel(arr,x,y,rows,cols);
				idx++;
			}
		}
		idx = 0;
	}
}

void strippeaks(float *arr,
		int len,
		int cycles,
		int width){

	float m;
	int high;
	int low;
	
	for (int k=0;k<cycles;k++){
		if (k>=cycles-8){width = width/1.4142135623730950;}
		for (int l=0;l<len;l++){
			if (l-width<0){ low=0; }
			else { low=l-width; }
			if (l+width>=len){ high=len-1; }
			else { high= l+width; }

			m = (arr[low] + arr[high])*0.5;

			if (m<1){ m=1; }
			if (arr[l]>m){ arr[l]=m; }
		}
	}
}

float *snipbg(float *arr,
		int len,
		int cycles,
		int width,
		int sg_window,
		int sg_order){

	for (int i=0;i<len;i++){
		arr[i] = sqrt(arr[i]);		
	}
	
	//savgol_filter(sqr, len, sg_window, sg_order);

	for (int i=0;i<len;i++){
		if (arr[i]<0){
			arr[i] = 0;
		}
	}

	strippeaks(arr, len, cycles, width);

	for (int i=0;i<len;i++){
		arr[i] = pow(arr[i],2);
	}
	return arr;
}

float batch_snipbg(float **matrix,
		int dim_x,
		int dim_y,
		int nchan,
		int progress,
		struct PARAM bg_params){
	for(int i=0;i<(dim_x*dim_x);i++){
		progress++;
		matrix[i] = snipbg(
				matrix[i],
				nchan,
				bg_params.cycles,
				bg_params.window,
				bg_params.sav_window,
				bg_params.sav_order);
	}
	return **matrix; 
}

struct pair{
  float min;
  float max;
};

struct pair getMinMax(float arr[], int n){
  struct pair minmax;
  int i;

  if (n == 1)
  {
     minmax.max = arr[0];
     minmax.min = arr[0];
     return minmax;
  }

  if (arr[0] > arr[1])
  {
      minmax.max = arr[0];
      minmax.min = arr[1];
  }
  else
  {
      minmax.max = arr[1];
      minmax.min = arr[0];
  }

  for (i = 2; i<n; i++)
  {
    if (arr[i] >  minmax.max)
      minmax.max = arr[i];

    else if (arr[i] <  minmax.min)
      minmax.min = arr[i];
  }

  return minmax;
}

int main(){
	float arr[20] = {1,1,1,1,1,
			1,1,2,2,1,
			2,2,2,2,2,
			1,1,1,1,1};
	float arr2[20] = {2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2};
	float arr3[20] = {1,1,2,8,56,234,75,23,3,2,2,2,55,125,230,87,12,2,2};

	int dimx = 4;
	int dimy = 4;
	int NCHAN = 100;
	float **data;
	float *out;

	float test[16][10];
	
	float iter = 0;
	for (int x=0;x<dimx*dimy;x++){
		for (int y=0;y<10;y++){
			test[x][y] = iter;
			iter ++;
			//printf("\n%f",test[x][y]);
		}
	}

	//printf("\nBefore");
	//print_arr(arr3,20);

	//apply_scaling(arr2, arr,1,20);
	//threshold(arr,1,10,20);
	
	//apply_smooth(arr, 1, 4, 5);
	//out = snipbg(arr3,20,24,7,7,3);

	//printf("\nAfter.");
	//print_arr(out,20);

	struct PARAM params;
	params.cycles = 24;
	params.window = 5;
	params.sav_window = 5;
	params.sav_order = 3;

	//print_arr(test[0],10);
	//batch_snipbg(test,4,4,10,0,params);
	//print_arr(test[0],10);
	printf("\nDONE!");

	return 0;
}
