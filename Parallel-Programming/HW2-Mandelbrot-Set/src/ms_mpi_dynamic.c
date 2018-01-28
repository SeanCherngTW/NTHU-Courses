#define PNG_NO_SETJMP
#define DATA_TAG 1
#define RESULT_TAG 2
#define SOURCE_TAG 3
#define TERMINATE_TAG 4
#define ROOT 0

#include <stddef.h>
#include <assert.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <mpi.h>
#include <png.h>

struct data
{
    int row;
    int* row_image;
};

double start_time = 0;
double comm_time = 0;

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
                //printf("p = %d\n",p);
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

      //  MPI_Datatype IMG_DATA;
      //  struct data tmp[2];
      //  MPI_Aint extent = &tmp[1] - &tmp[0];
      //  MPI_Type_create_resized(MPI_2INT, 0, extent, &IMG_DATA);
      //  MPI_Type_commit(&IMG_DATA);
 
        //struct data struct_data;
       // struct_data.row_image = (int*)malloc(width * sizeof(int));
      /*  int var_count = 1;
        MPI_Datatype array_of_types[var_count];
        array_of_types[0] = MPI_INT;
        array_of_types[1] = MPI_INT;
        int array_of_blocklengths[var_count];
        array_of_blocklengths[0] = 1;
        array_of_blocklengths[1] = width;

        MPI_Aint array_of_displacements[var_count];
        MPI_Aint address1, address2, address3;
        MPI_Get_address(&struct_data, &address1);
        MPI_Get_address(&struct_data.row, &address2);
        MPI_Get_address(&struct_data.row_image[0], &address3);
        
        array_of_displacements[0] = address2 - address1;
        array_of_displacements[1] = address3 - address2;
        
        MPI_Datatype IMG_DATA;
        MPI_Type_create_struct(var_count, array_of_blocklengths, array_of_displacements, array_of_types, &IMG_DATA);
        MPI_Type_commit(&IMG_DATA); */
        
	MPI_Comm_size(MPI_COMM_WORLD, &p_size);
	MPI_Comm_rank(MPI_COMM_WORLD, &p_rank);

        int* image_gather;
        //int* image = (int*)malloc(width * sizeof(int));
        //assert(image); 
        /* START MPI WORK POOL */
        if(p_rank == 0)
        {
            comm_time = 0;
            MPI_Status status;
            int p_active = 0;
            int p_row = 0;
            int total_row = height;
            int slave_rank = 0;
            int row_offset = 0;
            int start_row = 0;
            int end_row = 0;
            int* p_result = (int*)malloc(width * sizeof(int));
            image_gather = (int*)malloc(width * height * sizeof(int));
        //    struct data recv_struct_data;
        //    recv_struct_data.row_image = (int*)malloc(width * sizeof(int));
            printf("(Proc ROOT) Ready to Send\n");
            for(int k = 1; k < p_size; k++)
            {
                //printf("(Proc ROOT) In for\n");
                start_time = MPI_Wtime();
                MPI_Send(&p_row, 1, MPI_INT, k, DATA_TAG, MPI_COMM_WORLD);
                comm_time += MPI_Wtime() - start_time;
                p_active++;
                p_row++;
                //printf("(Proc ROOT) p_active = %d, p_row = %d\n", p_active, p_row);
            }

            do
            {
                ///MPI_Recv(&recv_struct_data, 1, IMG_DATA, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);
                //MPI_Recv(recv_struct_data.row_image, width, MPI_INT, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);
                // MPI_Recv(&image_gather, width, MPI_INT, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);
                
                start_time = MPI_Wtime();
                MPI_Recv(p_result, width, MPI_INT, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);
                MPI_Recv(&start_row, 1, MPI_INT, status.MPI_SOURCE, 6, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                comm_time += MPI_Wtime() - start_time;                

                int j = 0;
                //start_row = recv_struct_data.row * width;
                //printf("(Proc ROOT) start_row = %d\n", start_row);
                start_row = start_row * width;
                end_row = start_row + width;
                for(int i = start_row; i < end_row; i++)
                {
                   // printf("(Proc ROOT) p_result[%d] = %d\n", i, p_result[j]);
                    image_gather[i] = p_result[j];
                    j++;
                }

                // MPI_Recv(p_result, width, MPI_INT, MPI_ANY_SOURCE, RESULT_TAG, MPI_COMM_WORLD, &status);
                p_active--;
                if(p_row < total_row)
                {
                    start_time = MPI_Wtime();
                    MPI_Send(&p_row, 1, MPI_INT, status.MPI_SOURCE, DATA_TAG, MPI_COMM_WORLD);
                    comm_time += MPI_Wtime() - start_time;
                    p_active++;
                    p_row++;
                }
                else
                { 
                    start_time = MPI_Wtime();
                    MPI_Send(&p_row, 1, MPI_INT, status.MPI_SOURCE, TERMINATE_TAG, MPI_COMM_WORLD);
                    comm_time += MPI_Wtime() - start_time;
                    printf("(Proc ROOT) TERMINATE_TAG is sent to %d, p_active = %d\n", status.MPI_SOURCE, p_active);
                }
               /* int j = 0;
                start_row = recv_struct_data.row;
                end_row = recv_struct_data.row + width;
                for(int i = start_row; i < end_row; i++)
                {
                    printf("image_gather[%d] = %d\n", i, recv_struct_data.row_image[j]);
                    image_gather[i] = recv_struct_data.row_image[j];
                    j++;
                }*/
                /* TO-DO: Allocate p_result to image*/
            }while(p_active > 0);
        }  /* end if */
        else
        {
            MPI_Status status;
            int p_row = 0;
            int* image = (int*)malloc(width * sizeof(int));
            struct data struct_data;
            struct_data.row_image = (int*)malloc(width * sizeof(int));
      
            printf("(Proc #%d) Ready to Receive\n", p_rank);
            MPI_Recv(&p_row, 1, MPI_INT, ROOT, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            
            printf("(Proc #%d Received)\n", p_rank);
            while(status.MPI_TAG == DATA_TAG)
            {
                /* Mandelbort Set */
                int count = 0;
                double y0 = p_row * ((upper - lower) / height) + lower;
            
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
                    }  /* end while */
                    image[count] = repeats;
                    //printf("(Proc #%d) image[%d] = %d\n", p_rank, count, image[count]);
                    count++;
                }  /* end for */   
                struct_data.row = p_row;
                for (int i = 0; i < width; i++)
                    struct_data.row_image[i] = image[i];
                //printf("(Proc #%d) struct_data.row = %d\n", p_rank, struct_data.row);
                //for(int i = 0; i < 10; i++)
                //    printf("(Proc #%d) struct_data.row_image[%d] = %d\n", p_rank, i, struct_data.row_image[i]);
                // /// MPI_Send(&struct_data, 1, IMG_DATA, ROOT, RESULT_TAG, MPI_COMM_WORLD);
                //MPI_Send(struct_data.row_image, width, MPI_INT, ROOT, RESULT_TAG, MPI_COMM_WORLD);
                MPI_Send(image, width, MPI_INT, ROOT, RESULT_TAG, MPI_COMM_WORLD);
                MPI_Send(&p_row, 1, MPI_INT, ROOT, 6, MPI_COMM_WORLD);
                MPI_Recv(&p_row, 1, MPI_INT, ROOT, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            }  /* end while */   
        }  /* end else */
        printf("(Proc #%d) End MPI Dynamic Work Pool\n", p_rank);
        /* END MPI DYNAMIC WORK POOL */

        MPI_Barrier(MPI_COMM_WORLD);
        
        //double comm_time = MPI_Wtime() - comm_start;
        if (p_rank == 0)
        {
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
        //free(image);
        MPI_Finalize();
}
