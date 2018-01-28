#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int *graph, *indx, *edge;
int n = 0, e = 0;
int rank, size;
// double synctime = 0, commtime = 0;

void initialize_mpi(int, char **);
void read_file(char *);
void init_vertex();
void split(char **, char *, const char *);
void write_file(char *, int *);

void initialize_mpi(int argc, char **argv)
{
    int rc = MPI_Init(&argc, &argv);
    if (rc != MPI_SUCCESS)
    {
        printf("Error starting MPI");
        MPI_Abort(MPI_COMM_WORLD, rc);
    }
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
}

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
    e = atoi(arr[1]); // Number of Edge

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

void init_vertex()
{
    int i, j, ind, edg;

    indx = (int *)malloc(n * sizeof(int));
    edge = (int *)malloc(2 * e * sizeof(int));

    for (i = 0, ind = 0, edg = 0; i < n; i++)
    {
        for (j = 0; j < n; j++)
        {
            if (i != j && graph[i * n + j] != 999)
            {
                ind++;
                edge[edg++] = j;
            }
        }
        indx[i] = ind;
    }

    // if (rank == 0)
    // {
    //     printf("indx: \n");
    //     for (i = 0; i < n; i++)
    //         printf("%d ", indx[i]);
    //     printf("\n");

    //     printf("edge: \n");
    //     for (i = 0; i < 2 * e; i++)
    //         printf("%d ", edge[i]);
    //     printf("\n");
    // }
}

char *int_to_string(int num, char *str)
{
    if (str == NULL)
        return NULL;

    sprintf(str, "%d", num);
    return str;
}

void write_file(char *filename, int *result_graph)
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
            fputs(int_to_string(result_graph[i * n + j], tmp), output_file);
            fputs(" ", output_file);
        }
        fputs("\n", output_file);
    }
    fclose(output_file);
}

int main(int argc, char *argv[])
{
    // double total1, total2;

    if (argc != 4)
    {
        puts("Command: ./filename <INPUT_FILE> <OUTPUT_FILE> <num of threads/processes>");
        exit(-1);
    }

    /* Read File */
    // double io1, io2;
    // io1 = MPI_Wtime();
    read_file(argv[1]);
    // io2 = MPI_Wtime();
    // printf("read_file() = %lf\n", io2 - io1);
    /* Read File */

    init_vertex();

    MPI_Comm Comm_graph;
    initialize_mpi(argc, argv);
    // total1 = MPI_Wtime();
    MPI_Graph_create(MPI_COMM_WORLD, n, indx, edge, 1, &Comm_graph);
    MPI_Comm_rank(Comm_graph, &rank);

    int relax = 1;
    int num_neighbors;
    int i, j;

    // double comm1 = MPI_Wtime();
    MPI_Graph_neighbors_count(Comm_graph, rank, &num_neighbors);
    // double comm2 = MPI_Wtime();
    // commtime += comm2 - comm1;

    int *send_buf, *recv_buf, *neighbors;

    send_buf = (int *)malloc(n * sizeof(int));
    recv_buf = (int *)malloc(n * num_neighbors * sizeof(int));
    neighbors = (int *)malloc(num_neighbors * sizeof(int));

    // double comm3 = MPI_Wtime();
    MPI_Graph_neighbors(Comm_graph, rank, num_neighbors, neighbors);
    // double comm4 = MPI_Wtime();
    // commtime += comm4 - comm3;

    for (i = 0; i < n; i++)
        send_buf[i] = graph[rank * n + i];

    // double computation1 = MPI_Wtime();
    while (relax)
    {
        relax = 0;

        // double sync1 = MPI_Wtime();
        MPI_Neighbor_allgather(send_buf, n, MPI_INT, recv_buf, n, MPI_INT, Comm_graph);
        // double sync2 = MPI_Wtime();
        // synctime += (sync2 - sync1);

        for (i = 0; i < num_neighbors; i++)
        {
            int v = neighbors[i];
            for (j = 0; j < n; j++)
            {
                if (j != rank)
                {
                    if (send_buf[j] > send_buf[v] + recv_buf[i * n + j])
                    {
                        send_buf[j] = send_buf[v] + recv_buf[i * n + j];
                        relax = 1;
                    }
                }
            }
        }
        int tmp = relax;

        // double sync3 = MPI_Wtime();
        MPI_Allreduce(&tmp, &relax, 1, MPI_INT, MPI_BOR, Comm_graph);
        // double sync4 = MPI_Wtime();
        // synctime += (sync4 - sync3);
    }
    // double computation2 = MPI_Wtime();

    int *final_graph;
    if (rank == 0)
        final_graph = (int *)malloc(n * n * sizeof(int));

    // double comm5 = MPI_Wtime();
    MPI_Gather(send_buf, n, MPI_INT, final_graph, n, MPI_INT, 0, Comm_graph);
    // double comm6 = MPI_Wtime();
    // commtime += comm6 - comm5;

    // if (rank == 0)
    // {
    //     printf("------------------------------\n");
    //     printf("computation time = %lf\n", (computation2 - computation1 - synctime) * n);
    //     printf("sync time = %lf\n", synctime * n);
    //     printf("comm time = %lf\n", commtime * n);
    //     printf("------------------------------\n");
    // }
    free(send_buf);
    free(recv_buf);
    free(neighbors);
    free(graph);
    free(indx);
    free(edge);

    // total2 = MPI_Wtime();

    if (rank == 0)
    {
        /* Write File */
        // double io1, io2;
        // io1 = MPI_Wtime();
        write_file(argv[2], final_graph);
        // io2 = MPI_Wtime();
        // printf("write_file() = %lf\n", (io2 - io1));
        free(final_graph);
        /* Write File */
        // printf("Total time = %lf\n", (total2 - total1) * n);
    }

    MPI_Finalize();
    return 0;
}