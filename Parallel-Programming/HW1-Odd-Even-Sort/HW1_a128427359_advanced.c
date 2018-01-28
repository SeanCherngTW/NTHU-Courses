#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define another(x)  ((x + 1) % 2)
#define swap(i, j)  float t = i; i = j; j = t;
#define tag1    0
#define tag2    1
#define bool        char
#define true        1
#define false       0
#define is_odd(x)   ((x) & 1)
#define is_even(x)  (!is_odd(x))

double iotime=0, commtime=0;
int size, rank, num, p_element, p_num;
float *p_nums;
bool sorted = false; 
void initialize_mpi(int, char**);
void read_file_mpi(char*, float*, int*);
int  communicate(int, float*, float*, int);
void switch_right(int, float*);
void switch_left(int, float*);
void save_file_mpi(char*, float*);
void quick_sort(float*, int, int);
void left_insertion_sort(float* ,int);
void right_insertion_sort(float*, int);
void insertion_sort(float*, int);

int main(int argc, char** argv)
{        
    clock_t t1, t2, io1, io2, c1, c2;
    initialize_mpi(argc, argv);
    t1 = clock();
    p_nums = (float *)malloc(p_num * sizeof(float));
    
    io1 = clock();
    read_file_mpi(argv[2], p_nums, &p_element);
    io2 = clock();
    iotime += io2-io1;
    
    int p_first_index = p_num * rank;
    int p_last_index  = p_first_index + p_num - 1;
    
    quick_sort(p_nums, 0, p_element-1);
    MPI_Barrier(MPI_COMM_WORLD); 
    while(!sorted)
    {
        sorted = true;
         
        /* even phase */
        c1 = clock();
        if (is_even(rank) && is_even(p_last_index))
            switch_right(rank + 1, &p_nums[p_element - 1]);
        if (is_odd(rank) && is_odd(p_first_index)) 
            switch_left(rank - 1, &p_nums[0]);
        MPI_Barrier(MPI_COMM_WORLD);
        c2 = clock();
        commtime += c2-c1; 

        /* odd phase */
        c1 = clock();
        if (is_odd(p_last_index)) 
            switch_right(rank + 1, &p_nums[p_element - 1]);
        if (is_even(p_first_index)) 
            switch_left(rank - 1, &p_nums[0]);
        MPI_Barrier(MPI_COMM_WORLD);
        c2 = clock();
        commtime += c2-c1;
        //odd_even_sort(p_nums, 1, p_element);
        insertion_sort(p_nums, p_element);
        bool tmp = sorted;
        MPI_Allreduce(&tmp, &sorted, 1, MPI_CHAR, MPI_BAND, MPI_COMM_WORLD); 
    }
    io1 = clock();
    save_file_mpi(argv[3], p_nums);
    io2 = clock();
    iotime += io2-io1;
    free(p_nums);
    t2 = clock();
    printf("Total time: %lf\n",(t2-t1)/(double)(CLOCKS_PER_SEC));
    printf("Comm  time: %lf\n", commtime/(double)(CLOCKS_PER_SEC));
    printf("I/O   time: %lf\n", iotime/(double)(CLOCKS_PER_SEC));
    MPI_Finalize();
}         
         
void initialize_mpi(int argc, char** argv)
{
    /* rc: MPI_Init result */
    int rc = MPI_Init(&argc, &argv);
    if(rc != MPI_SUCCESS)
    {
        printf("Error starting MPI"); 
        MPI_Abort(MPI_COMM_WORLD, rc);
    }
    /* size: Number of processors */
    /* rank: The ID of this processor */
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
   
    /* argv[1]: length of input list */
    sscanf(argv[1], "%d", &num);
    
    /* p_num: space for elements in each processor */
    p_num = (num + size - 1) / size;
}

void read_file_mpi(char* input_file, float* p_nums, int* p_element)
{
    MPI_File fh;
    MPI_Status status;
    /* Open file "input_file" in READ-ONLY and assign to fh */
    MPI_File_open(MPI_COMM_WORLD, input_file, MPI_MODE_RDONLY, MPI_INFO_NULL, &fh);
    /* Allocate elements to processors */
    MPI_File_set_view(fh, sizeof(float) * p_num * rank, MPI_FLOAT, MPI_FLOAT, "native", MPI_INFO_NULL);
    MPI_File_read_all(fh, p_nums, p_num, MPI_FLOAT, &status);

    /* p_element: number of elements in each processor */
    MPI_Get_count(&status, MPI_FLOAT, p_element);
    MPI_File_close(&fh);
}

void save_file_mpi(char* output_file, float* p_nums)
{
    MPI_File fh;
    MPI_Status status;
    /* Open file "input_file" in READ-ONLY and assign to fh */
    MPI_File_open(MPI_COMM_WORLD, output_file, MPI_MODE_WRONLY | MPI_MODE_CREATE, MPI_INFO_NULL, &fh);
    /* Allocate elements to processors */
    MPI_File_set_view(fh, sizeof(float) * p_num * rank, MPI_FLOAT, MPI_FLOAT, "native", MPI_INFO_NULL);
    MPI_File_write_all(fh, p_nums, p_element, MPI_FLOAT, &status);
    MPI_File_close(&fh);
}


void switch_right(int proc, float* target)
{
    float buffer;
    if (communicate(proc, target, &buffer, tag1)) 
        return;
    
    if (*target > buffer) 
    { 
        *target = buffer; 
        sorted = false; 
    }
}

void switch_left(int proc, float* target)
{
    float buffer;
    if (communicate(proc, target, &buffer, tag2)) 
        return;
    
    if (buffer > *target) 
    { 
        *target = buffer; 
        sorted = false; 
    }
}


void right_insertion_sort(float* a, int n)
{
    int target_index;
    int last_index = n-1;
    float target_item = a[last_index];
    printf("right RANK: %d, LEN: %d\n",rank, n);
    for(int i = last_index - 1; i > 0; i--)
      if(a[last_index] > a[i])
      {
        target_index = i + 1;
        break;
      }
  
    for(int i = last_index; i > target_index; i--)
        a[i] = a[i-1];
  
    a[target_index] = target_item;
}


void left_insertion_sort(float* a, int n)
{
    int target_index;
    int first_index = 0;
    float target_item = a[first_index];
    printf("left RANK: %d, LEN: %d\n", rank, n);
    for(int i = first_index - 1; i < n; i++)
      if(a[first_index] < a[i])
      {
        target_index = i - 1;
        break;
      }
  
    for(int i = 0; i < target_index; i++)
        a[i] = a[i+1];
  
    a[target_index] = target_item;
}

void quick_sort(float* a, int left, int right) { 
    if(left < right) 
    { 
        float s = a[(left+right)/2]; 
        int i = left - 1; 
        int j = right + 1; 

        while(1) { 
            while(a[++i] < s);
            while(a[--j] > s);
            if(i >= j) 
                break; 
            swap(a[i], a[j]); 
        } 

        quick_sort(a, left, i-1);
        quick_sort(a, j+1, right);
    } 
} 


void insertion_sort(float* a, int n)
{
   int i, j;
   float key;
   for (i = 1; i < n; i++)
   {
       key = a[i];
       j = i - 1;
 
       while (j >= 0 && a[j] > key)
       {
           a[j+1] = a[j];
           j = j - 1;
       }
       a[j+1] = key;
   }
}



/* Communitcation between 2 processors */
int communicate(int proc, float* target, float* buffer, int tag)
{
    if (rank >= size || proc >= size || proc < 0) 
        return -1;
    
    MPI_Status status;
    MPI_Request req;
    /* Send the last element of this rank to the next rank */
    MPI_Isend(target, 1, MPI_FLOAT, proc, tag, MPI_COMM_WORLD, &req);
    /* Receive the first element of the next rank */
    MPI_Irecv(buffer, 1, MPI_FLOAT, proc, another(tag), MPI_COMM_WORLD, &req);
    MPI_Wait(&req, &status);   
    
    return 0;
}
