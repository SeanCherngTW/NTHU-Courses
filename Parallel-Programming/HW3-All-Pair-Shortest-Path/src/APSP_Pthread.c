#include <time.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>

int *graph;
int n = 0;
int rc;
int num_threads = 0;
struct data
{
    pthread_t thread;
    int thread_ID;
};
typedef struct data tdata_t;
pthread_barrier_t barr;

void read_file(char *);
void split(char **, char *, const char *);
void write_file(char *);
void *floyd_warshall_parallel(void *);

void read_file(char *filename)
{
    const char *del = " ";
    const int LINE_LENGTH = 64;
    char line[64];
    char *arr[3];
    int i, j;

    FILE *input_file = fopen(filename, "r");
    if (!input_file)
    {
        puts("Error occurs while opening the input file");
        exit(-1);
    }

    fgets(line, LINE_LENGTH, input_file);
    split(arr, line, del);
    n = atoi(arr[0]); // Number of vertex

    graph = (int *)malloc(n * n * sizeof(int));

    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            graph[i * n + j] = (i == j) ? 0 : 999;

    while (fgets(line, LINE_LENGTH, input_file))
    {
        split(arr, line, del);
        int x = atoi(arr[0]);
        int y = atoi(arr[1]);
        int value = atoi(arr[2]);

        // Since the input graph is an undirect graph
        graph[x * n + y] = value;
        graph[y * n + x] = value;
    }
    fclose(input_file);
}

void split(char **arr, char *str, const char *del)
{
    char *s = strtok(str, del);
    while (s != NULL)
    {
        *arr++ = s;
        s = strtok(NULL, del);
    }
}

void *floyd_warshall_parallel(void *threadid)
{
    clock_t cal1, cal2, sync1, sync2;
    double caltime = 0, synctime = 0;
    cal1 = clock();
    int tid = *(int *)threadid;
    int i_lower = n * tid / num_threads;
    int i_upper = n * (tid + 1) / num_threads;
    int i, j, k;
    for (k = 0; k < n; k++)
    {
        for (i = i_lower; i < i_upper; i++)
            for (j = 0; j < n; j++)
                graph[i * n + j] =
                    ((graph[i * n + k] + graph[k * n + j]) < graph[i * n + j]) ? graph[i * n + k] + graph[k * n + j] : graph[i * n + j];

        sync1 = clock();
        pthread_barrier_wait(&barr);
        sync2 = clock();
        synctime += (sync2 - sync1) / (double)(CLOCKS_PER_SEC);
    }
    cal2 = clock();
    caltime = (cal2 - cal1) / (double)(CLOCKS_PER_SEC);
    // printf("Thread #%d, caltime = %lf, synctime = %lf\n", tid, caltime / num_threads, synctime / num_threads);
    pthread_exit(NULL);
}

char *int_to_string(int num, char *str)
{
    if (str == NULL)
        return NULL;

    sprintf(str, "%d", num);
    return str;
}

void write_file(char *filename)
{
    FILE *output_file = fopen(filename, "w");
    if (!output_file)
    {
        puts("Error occurs while opening the output file");
        exit(-1);
    }

    int i, j;
    char tmp[16];

    for (i = 0; i < n; i++)
    {
        for (j = 0; j < n; j++)
        {
            fputs(int_to_string(graph[i * n + j], tmp), output_file);
            fputs(" ", output_file);
        }
        fputs("\n", output_file);
    }
    fclose(output_file);
}

int main(int argc, char *argv[])
{
    // clock_t total1, total2;
    // total1 = clock();
    if (argc != 4)
    {
        puts("Command: ./apsp_pthread <INPUT_FILE> <OUTPUT_FILE> <num of threads>");
        exit(-1);
    }

    /* Read File */
    clock_t io1, io2;
    io1 = clock();
    read_file(argv[1]);
    io2 = clock();
    // printf("read_file() = %lf\n", (io2 - io1) / (double)(CLOCKS_PER_SEC));
    /* Read File */

    num_threads = atoi(argv[3]);
    num_threads = (num_threads > n) ? n : num_threads;
    tdata_t thread_data[num_threads];
    pthread_barrier_init(&barr, NULL, (unsigned)num_threads);

    int t;
    for (t = 0; t < num_threads; t++)
    {
        tdata_t tdata;
        tdata.thread_ID = t;
        thread_data[t] = tdata;
        rc = pthread_create(&thread_data[t].thread, NULL, &floyd_warshall_parallel, (void *)&thread_data[t].thread_ID);
        if(rc != 0)
        {
            printf("pthread_create error: %d\n", rc);
            exit(-1);
        }
    }

    for (t = 0; t < num_threads; t++)
        pthread_join(thread_data[t].thread, NULL);

    /* Write File */
    io1 = clock();
    write_file(argv[2]);
    io2 = clock();
    // printf("write_file() = %lf\n", (io2 - io1) / (double)(CLOCKS_PER_SEC));
    /* Write File */

    // total2 = clock();
    // printf("Total Time = %lf\n", (total2 - total1) / (double)(CLOCKS_PER_SEC));

    pthread_exit(NULL);

    return 0;
}