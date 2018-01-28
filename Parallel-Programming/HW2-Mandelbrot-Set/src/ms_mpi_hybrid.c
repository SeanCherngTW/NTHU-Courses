#define PNG_NO_SETJMP

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <mpi.h>
#include <png.h>
#include <omp.h>

void write_png(const char* filename, const int width, const int height, const int* buffer) {
    FILE* fp = fopen(filename, "wb");
    assert(fp);
    png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    assert(png_ptr);
    png_infop info_ptr = png_create_info_struct(png_ptr);
    assert(info_ptr);
    png_init_io(png_ptr, fp);
    png_set_IHDR(png_ptr, info_ptr, width, height, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
    png_write_info(png_ptr, info_ptr);
    size_t row_size = 3 * width * sizeof(png_byte);
    png_bytep row = (png_bytep)malloc(row_size);
    for (int y = 0; y < height; ++y) 
    {
        memset(row, 0, row_size);
        for (int x = 0; x < width; ++x) 
        {
            int p = buffer[(height - 1 - y) * width + x];
            if(p < 0 || p > 100000)
            { 
                printf("p = %d\n",p);
                continue;
            }
            row[x * 3] = ((p & 0xf) << 4);
        }
        png_write_row(png_ptr, row);
    }
    free(row);
    png_write_end(png_ptr, NULL);
    png_destroy_write_struct(&png_ptr, &info_ptr);
    fclose(fp);
}

int main(int argc, char** argv) 
{
	int p_rank, rc, p_size;
	rc = MPI_Init(&argc, &argv);
	if(rc != MPI_SUCCESS)
        {
		printf("Error starting MPI");
		MPI_Abort(MPI_COMM_WORLD, rc);
	}
        double total_start = MPI_Wtime();
       
        /* Get Parameters */
        assert(argc == 9);
        int num_threads = strtol(argv[1], 0, 10);
        double left = strtod(argv[2], 0);
        double right = strtod(argv[3], 0);
        double lower = strtod(argv[4], 0);
        double upper = strtod(argv[5], 0);
        int width = strtol(argv[6], 0, 10);
        int height = strtol(argv[7], 0, 10);
        const char* filename = argv[8];

	MPI_Comm_size(MPI_COMM_WORLD, &p_size);
	MPI_Comm_rank(MPI_COMM_WORLD, &p_rank);

        /* Properties for all processes */
        int p_height_max = (height + p_size - 1) / p_size;
        int p_height_lower = height * p_rank / p_size;
        int p_height_upper = height * (p_rank + 1) / p_size;
        int p_height_range = p_height_upper - p_height_lower;
        double p_lower = lower + p_height_range * p_rank / p_size;
        double p_upper = lower + p_height_range * (p_rank + 1) / p_size;

        int* image = (int*)malloc(width * p_height_range * sizeof(int));
        int p_width = width / p_size;      
        int total_count = height * width / p_size;
        assert(image);
        int p_count = width * ((height * (p_rank + 1) / p_size) - (height * p_rank / p_size)); 
        int count = p_rank * p_count;
        printf("Proc #%d, count = %d\n", p_rank, count);
                    
        printf("Proc #%d, p_lower = %d, p_upper = %d\n", p_rank, p_height_lower, p_height_upper); 
        /* mandelbrot set */ 
        #pragma omp parallel num_threads(num_threads) shared(image)
        {
           // int count = width * ((height * (p_rank + 1) / p_size) - (height * p_rank / p_size)); 
            int t_rank = omp_get_thread_num();
        #pragma omp for schedule(dynamic)
        for (int j = p_height_lower; j < p_height_upper; ++j) 
        {
            double y0 = j * ((upper - lower) / height) + lower;
            
            for (int i = 0; i < width; ++i)
            {
                double x0 = i * ((right - left) / width) + left;

                int repeats = 0;
                double x = 0;
                double y = 0;
                double length_squared = 0;
                while (repeats < 100000 && length_squared < 4) 
                {
                    double temp = x * x - y * y + x0;
                    y = 2 * x * y + y0;
                    x = temp;
                    length_squared = x * x + y * y;
                    ++repeats;
                }
                image[j * width + i - count] = repeats;
                printf("Proc #%d Thread #%d, image[%d] = %d\n", p_rank, t_rank, j*width+i, image[j*width+i]);
                //count++;
             }
        }  // end outer for
        // printf("This is Proc #%d Thread #%d FINISHED for\n", p_rank, t_rank);
        }
        printf("This is Proc #%d FINISHED!!!!!!!!!!!!\n ", p_rank);
        //for(int i = 0; i < 100; i++){
        //   printf("image[%d] = %d\n", i, image[i]);
       // }

       // MPI_Barrier(MPI_COMM_WORLD);
        
        /* For MPI_Gatherv() */
        int* image_gather;
        int *counts = (int*)malloc(p_size * sizeof(int));
        int *offsets = (int*)malloc(p_size * sizeof(int));
        int totalCount = width * height;
        int n = totalCount / p_size;

        for (int i = 0; i < p_size; i++)
            counts[i] = width * ((height * (i + 1) / p_size) - (height * i / p_size));
        
        int sum = 0;
        for (int i = 0; i < p_size; i++) 
        {
            offsets[i] = sum;
            sum += counts[i];
        }  
         
        /* Debug */
        if (p_rank == 0) 
            for (int i = 0; i < p_size; i++)
            {
                printf("counts[%d] = %d\n", i, counts[i]);
                printf("offsets[%d] = %d\n", i, offsets[i]);
            }

        if (p_rank == 0)
            image_gather = (int*)malloc(width * height * sizeof(int));
        
        double comm_start = MPI_Wtime();
        MPI_Gatherv(image, counts[p_rank], MPI_INT, image_gather, counts, offsets, MPI_INT, 0, MPI_COMM_WORLD);
        // printf("Proc #%d (root) is sent\n", p_rank);
        
        MPI_Barrier(MPI_COMM_WORLD);

        double comm_time = MPI_Wtime() - comm_start;
        if (p_rank == 0)
        {
            for (int i = 0; i < 100; i++)
                printf("images[%d] = %d\n", i, image_gather[i]);
            double io_start = MPI_Wtime();
            write_png(filename, width, height, image_gather);
            double io_time = MPI_Wtime() - io_start;
            //printf("I/O  Time = %lf\n", io_time); 
            //printf("Comm Time = %lf\n", comm_time);
            free(image_gather);
            double total_time = MPI_Wtime() - total_start;
            printf("I/O  Time = %lf\n", io_time);
            printf("Comm Time = %lf\n", comm_time);
            printf("CPU  Time = %lf\n", total_time - comm_time - io_time);
        }
        free(image);
        MPI_Finalize();
}
