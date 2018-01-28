#define PNG_NO_SETJMP

#include <assert.h>
#include <png.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

void write_png(const char* filename, const int width, const int height, const int* buffer) 
{
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
    /* argument parsing */
    assert(argc == 9);
    int num_threads = strtol(argv[1], 0, 10);
    double left = strtod(argv[2], 0);
    double right = strtod(argv[3], 0);
    double lower = strtod(argv[4], 0);
    double upper = strtod(argv[5], 0);
    int width = strtol(argv[6], 0, 10);
    int height = strtol(argv[7], 0, 10);
    const char* filename = argv[8];

    double pic_height_range = upper - lower;

    /* allocate memory for image */
    int* image = (int*)malloc(width * height * sizeof(int));
    assert(image);
    
    #pragma omp parallel num_threads(num_threads) shared(image)
    {
        int t_size = omp_get_num_threads();
        int t_rank = omp_get_thread_num();
        int t_height_lower = height * t_rank / t_size;
        int t_height_upper = height * (t_rank + 1) / t_size;
        int t_height_range = t_height_upper - t_height_lower;
        double t_lower = lower + pic_height_range * t_rank / t_size;
        double t_upper = lower + pic_height_range * (t_rank + 1) / t_size;
        // printf("Thread#%d/%d, t_lower=%.2lf, t_upper=%.2lf, t_h_lower=%d, t_h_upper=%d\n", t_rank, t_size, t_lower, t_upper, t_height_lower, t_height_upper);

        /* mandelbrot set */
        for (int j = t_height_lower; j < t_height_upper; ++j) 
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
                image[j * width + i] = repeats;
            } // end inner for
        } // end outer for
    } // end parallel

    // for(int k = 0; k < 100; k++)
      //  printf("image[%d] = %d\n", k, image[k]);

    /* draw and cleanup */
    write_png(filename, width, height, image);
    free(image);
}
