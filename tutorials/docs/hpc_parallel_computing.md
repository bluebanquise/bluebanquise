# Parallel computing

This practical session objective is to make user aware of his environment and how to use some parallel computing standard.

<div class="comment-tile">
    <div class="comment-tile-image">
        <img src="../images/global/Ash.png" alt="Image Description" width="96" height="96">
    </div>
    <div class="comment-tile-text">
        <p>Note that this training is light, and objective is to provide a quick introduction. To go deeper, I stronlgy recommand to check the https://chryswoods.com/main/courses.html INCREDIBLE website \o/ !!</p>
    </div>
</div>

## Environment

Connect via ssh to your remote system. Note that you can add -vvv flags to the ssh connection to get some details about the ssh connection mechanism, and dialog between client and server.

Once on the Linux system, first get the number of cores available and CPU details, using command: `cat /proc/cpuinfo`

The result shows you multiple things:

First, the number of processor entries reflect the number of cores available.
For example:

```
:~$ cat /proc/cpuinfo | grep '^processor'
processor       : 0
processor       : 1
processor       : 2
processor       : 3
```

Shows that there are 4 cores on this system.
Another interesting value is the physical id. The following command allows you to know how much CPU socket your server is equipped with:

```
:~$ cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l
1
```

You can also get SIMD available instructions on this CPU by having a look at the flags key output:

```
:~$ cat /proc/cpuinfo | grep flags
```

Well known SIMD instructions are AVX, FMA, SSE, MMX, etc.

The command `lscpu` also allows you to get details, and check if HyperThreading is active or not (Threads per core).

It is important to know available CPU cores resources (and how these are distributed physically) and available SIMD at disposal, to get maximum performances of current system.

Note that using the following commands, you can get details on other hardware:

* `lspci` (if installed) shows PCI devices, and so GPU and Infiniband cards.
* `free -h` shows available memory
* `df -h` shows available disk

## OpenMP

OpenMP is natively embedded in GCC. Install GCC and all needed tools:

```
sudo apt-get update && sudo apt-get install gcc make build-essential -y
```

Then create a new file called my_openmp_code.c with the following content:

```C
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <omp.h>
#include <unistd.h>

int main(int argc, char** argv)
{
    int n = 10;
    #pragma omp parallel shared(n) default(shared)
    {
        printf("Hello from thread: %d\n", omp_get_thread_num());

        # pragma omp for
            for (int i = 0; i < n; i++ )
            {
                printf("Iteration %d\n", i);
                sleep(2);
            }
    }
    return 0;
}
```

Understand the concept: here, program will iterate 10 times, and wait 2s at each iteration.
You can see we made the for loop parallel. Objective is to distribute load of this loop over multiple threads. The sleep instruction replaces a long calculation.

And compile it with gcc using the -fopenmp flag:

```
gcc my_openmp_code.c -fopenmp
```

You will get an executable `a.out`.

Ask system to only use 1 thread, and launch the executable with a time to know how much time program execution took:

```
:~$ export OMP_NUM_THREADS=1
:~$ time ./a.out
Hello from process: 0
Iteration 0
Iteration 1
Iteration 2
Iteration 3
Iteration 4
Iteration 5
Iteration 6
Iteration 7
Iteration 8
Iteration 9

real    0m20.002s
user    0m0.002s
sys     0m0.000s
```

You can see it took 20s, as expected (2s per iteration, for 10 iterations).

Now lets request 4 threads:

```
:~$ export OMP_NUM_THREADS=4
:~$ time ./a.out
Hello from process: 0
Iteration 0
Hello from process: 1
Iteration 3
Hello from process: 2
Iteration 6
Hello from process: 3
Iteration 8
Iteration 1
Iteration 4
Iteration 7
Iteration 9
Iteration 2
Iteration 5

real    0m6.002s
user    0m0.012s
sys     0m0.000s
```

You can see that total time was reduced to 6s. This is logical: 4 + 4 + 2, so during last part of execution, 2 threads where idle while 2 threads were executing the sleep.

Etc.

OpenMP is a simple and convenient way to parallelize C/C++ and Fortran codes.
A lot of tunings are available to ensure a proper scaling. For example, when dealing with a large amount of small time consuming tasks per loop, adjusting scheduler strategy with a static chunk size greater than 1 can significantly reduce execution time.

## MPI

MPI main objective is to distribute memory and exchange between nodes to achieve large calculations.
MPI can also be used locally to communicate between local processes.

Unlike OpenMP, MPI need additional libraries and runtime to build and execute.

Install first required dependencies:

```
sudo apt update && sudo apt-get install libopenmpi-dev openmpi-bin openmpi-common gcc gnuplot
```

Then, create a new file called my_mpi_code.c with the following content:

```C
#include <stddef.h>
#include <mpi.h>

int main(int argc, char** argv)
{
    MPI_Init(NULL, NULL); // Init MPI (init MPI_COMM_WORLD communicator, set rank to each process, etc)

    int nb_mpi_processes;
    MPI_Comm_size(MPI_COMM_WORLD, &nb_mpi_processes); // Ask the number of MPI processes running

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank); // Ask the rank of the current process

    char hostname[256];
    int hostname_len;
    MPI_Get_processor_name(hostname, &hostname_len); // Ask the name of the host the process is running on

    printf("Hello world I am process %d on %d processes. I am running on %s\n",rank, nb_mpi_processes, hostname);

    MPI_Finalize(); // Close MPI

    return 0;
}
```

And this time, build it with openmpi wrapper:

```
mpicc my_mpi_code.c -o my_mpi_code
```

And execute it with the mpirun runtime:

```
mpirun -n 2 --host localhost,localhost my_mpi_code
```

You should see that 2 isolated processes were created. Both were able to show their rank id, while being aware of the total number of process.
You can also see that they do not share the same memory, as their values of `hostname` variable for example are natively different.

Now, in a next example, we are going to calculate a very simple 1D blur to expose basic real case usage.

Here is a simple example:

```C
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <mpi.h>

int main(int argc, char** argv)
{
    MPI_Init(NULL, NULL);
    int nb_mpi_processes;
    MPI_Comm_size(MPI_COMM_WORLD, &nb_mpi_processes);
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if(nb_mpi_processes != 2) { printf("This program is design to be run with 2 processes only"); return 0;}

    int Nx1=20;
    int Nx1l = Nx1/2;
    double * Field = malloc(Nx1l * sizeof(double));
    double * Field_buff = malloc(Nx1l * sizeof(double));
    int i;

    for(i = 0; i < Nx1l; ++i)
            Field[i] = 0.0;

    if(rank==0) {Field[Nx1l-3] = 10.0; Field[Nx1l-2]=10.0;}

    char fileName[2048];
    sprintf(fileName, "IN.%d.dat", rank);

    FILE *file = NULL;
    file = fopen(fileName, "w");
    for(i = 1; i < Nx1l-1; ++i)
            fprintf(file, "%d %lf\n", i + (rank * Nx1l) - 2 * rank, Field[i]);
    fclose(file);

    int niter=8;
    int n;
    int tag = 7777;
    for(n = 1; n <= niter; ++n)
    {
            if(rank==0)
            {
                    MPI_Sendrecv ( &Field[Nx1l-2] , 1 , MPI_DOUBLE , 1 , tag , &Field[Nx1l-1] , 1 , MPI_DOUBLE , 1 , tag , MPI_COMM_WORLD , MPI_STATUS_IGNORE);
            }
            if(rank==1)
            {
                    MPI_Sendrecv ( &Field[1] , 1 , MPI_DOUBLE , 0 , tag, &Field[0] , 1 , MPI_DOUBLE , 0 , tag , MPI_COMM_WORLD , MPI_STATUS_IGNORE);
            }

            for(i = 1; i < Nx1l-1; ++i)
                    Field_buff[i] = ( Field[i-1] + Field[i] + Field[i+1] ) / 3.0;

            for(i = 1; i < Nx1l-1; ++i)
                    Field[i] =  Field_buff[i];
    }

    sprintf(fileName, "OUT.%d.dat", rank);
    file = fopen(fileName, "w");
    for(i = 1; i < Nx1l-1; ++i)
            fprintf(file, "%d %lf\n", i + (rank * Nx1l) - 2 * rank, Field[i]);
    fclose(file);

    MPI_Finalize();

    return 0;
}
```

Before going further, try to understand what this program does:

1. We create a basic array of data, that could be temperature, pressure, whatever. The whole field is set to 0.0 real value, except near the middle where there is a sharp value raise to 10.0.
2. We apply iteratively a filter on this field, that will simply "smooth" the filed (blur).
3. After few iterations, the signal is smoothed.
4. For each iteration, both process exchange borders, so signal can spread between both process as a unified field (the 10.0 value defined in rank 0 field will slowly spread on rank 1 field).

Note that this is an **example code**, with many issues.

Build and execute this simple program now:

```
mpicc mpi_blurd_1d.c -o mpi_blurd_1d
mpirun --allow-run-as-root -n 2 --host localhost,localhost mpi_blurd_1d
```

Once run, you should see 4 files, 2 for input field, and 2 for output field.
You can `cat` files in the terminal to display their content (X and Y values).

Lets plot these field to see what happen.

Start gnuplot, and inside gnuplot, ask for an ASCII display (in terminal) to visualize fields.

```
gnuplot
gnuplot> set terminal dumb
gnuplot> set yrange [-1:11]
gnuplot> plot "IN.0.dat"
gnuplot> replot "IN.1.dat"
gnuplot> replot "OUT.0.dat"
gnuplot> replot "OUT.1.dat"
gnuplot> replot
```

You should get the following output:

```
     +---------------------------------------------------------------------+
     |        +        +       +        +        +        +       +        |
  10 |-+                            A   A               "IN.0.dat"    A  +-|
     |                                                  "IN.1.dat"    B    |
     |                                                 "OUT.0.dat"    C    |
   8 |-+                                               "OUT.1.dat"    D  +-|
     |                                                                     |
     |                                                                     |
   6 |-+                                                                 +-|
     |                                                                     |
     |                                                                     |
     |                                                                     |
   4 |-+                                                                 +-|
     |                              C   C                                  |
     |                         C            D                              |
   2 |-+                   C                     D                       +-|
     |                 C                             D                     |
     |            C                                       D                |
   0 |-+ C    C   A    A   A   A            B    B   B    B   D   D    D +-|
     |        +        +       +        +        +        +       +        |
     +---------------------------------------------------------------------+
     0        2        4       6        8        10       12      14       16
```

We can see that initial field has been smoothed, and that the 2 fields were computed as a unique field.

In this current example, calculations were fast. But in real world science, fields would be 3D fields, with millions of data per node, and so distributing calculations over multiple process would be key to perform the final calculation.

## Bash multi processing

You can also distribute subscripts over multiple process. This is especially useful when dealing with data processing.

In bash, when you need to isolate a portion of the script, have it inside parenthesis. Then, uses the & character at the end of parenthesis, to instruct that this portion of script should be executed in a separated process.
Since its asynchronous, you can then in the exact next line grab the PID of new process that was just created and store it into a variable (here P1 and P2).
Then, the wait instruction can be used to wait for one or multiple PID to end before continuing execution.

Example:

```bash
#!/bin/bash
date
(
echo I am process $BASHPID, son of $$ and I sleep 5 s
sleep 5
) &
P1=$!
(
echo I am process $BASHPID, son of $$ and I sleep 2 s
sleep 2
) &
P2=$!

wait $P1 $P2
date
echo all done
```

Which gives:

```
Thu Mar 23 20:55:15 EDT 2023
I am process 40675, son of 40673 and I sleep 5 s
I am process 40676, son of 40673 and I sleep 2 s
Thu Mar 23 20:55:20 EDT 2023
all done
```

Note that when dealing with a lot of small tasks, you can use a loop and arrays to submit process like jobs and store their pid into the array to manage them.

## Python Multiprocessing

Install python3 on local system:

`
sudo apt install python3 python3-pip
`

Once installed, create a serial program as a reference, with basic sleep function:

```python
#!/usr/bin/env python3
import time

def heavycalculations(n):
  time.sleep(n)
  return 1

if __name__ == "__main__":

    nsize = 10
    numbers = list(range(0, nsize, 1))
    print(len(numbers))
    result = list(range(0, nsize, 1))
    for n in range(0, nsize):
        numbers[n] = 2

    result = map(heavycalculations, numbers)

    print(sum(list(result)))
```

Here, function is called 10 times, with 2s sleep per call. So we expect 20s of execution.

Execute the python code with a time command to get total execution time:

```
$ time python3 sleep_serial.py
10
10

real    0m20.037s
user    0m0.018s
sys     0m0.000s
$
```

Now, lets make this code parallel with python multiprocessing :

```python
#!/usr/bin/env python3
import time
import multiprocessing as mp

def heavycalculations(n):
  time.sleep(n)
  return 1

if __name__ == "__main__":

    pool = mp.Pool(mp.cpu_count())

    nsize = 10
    numbers = list(range(0, nsize, 1))
    print(len(numbers))
    result = list(range(0, nsize, 1))
    for n in range(0, nsize):
        numbers[n] = 2

    result = pool.map(heavycalculations, numbers)

    print(sum(list(result)))
    # print(list(zip(numbers, result)))
    pool.close()
```

Now, if we execute this new code, on a 4 cores system:

```
$ time python3 sleep_serial.py
10
10

real    0m6.058s
user    0m0.047s
sys     0m0.018s
$
```

Time was reduced to 6s, which is expected.

Lets create a real world example now, to understand that scaling is not always as perfect.

Create a serial code that computes the number of prime numbers in a range:

```python
#!/usr/bin/env python3

def is_prime(num):

  if num == 1:
      return 0
  elif num > 1:
      # check for factors
      for i in range(2,num):
          if (num % i) == 0:
              return 1
  else:
      return 0
  return 0

if __name__ == "__main__":

    nsize = 100000
    numbers = list(range(1, nsize, 1))
    result = list(range(1, nsize, 1))

    result = map(is_prime, numbers)
#    for n in range(0, nsize - 1):
#        result[n] = is_prime(numbers[n])

    print("Number of primes found: " + str(sum(result)))
```

When executed, the time rises to around 24s on a single core:

```
$ time python3 prime_serial.py
Number of primes found: 90406

real    0m24.263s
user    0m24.245s
sys     0m0.012s
```

Lets create now a multiprocessing version of the same code:

```python
#!/usr/bin/env python3
import multiprocessing as mp

def is_prime(num):

  if num == 1:
      return 0
  elif num > 1:
      # check for factors
      for i in range(2,num):
          if (num % i) == 0:
              return 1
  else:
      return 0
  return 0

if __name__ == "__main__":

    pool = mp.Pool(mp.cpu_count())

    nsize = 100000
    numbers = list(range(1, nsize, 1))
    result = list(range(1, nsize, 1))

    result = pool.map(is_prime, numbers, chunksize=10000)
#    for n in range(0, nsize - 1):
#        result[n] = is_prime(numbers[n])

    print("Number of primes found: " + str(sum(result)))
    pool.close()
```

And execute it:

```
$ time python3 prime_mp.py
Number of primes found: 90406

real    0m13.460s
user    0m44.522s
sys     0m0.036s
```

Time was reduced to 13s with 4 cores, so not the perfect scaling we have seen before with synthetic sleeps tests. This code would need some optimizations.
Notice the user time, which has increased from 24s to 44s, due to the usage of multiple cores in parallel.

## Dask

Dask allows to spread load over multiple cores on multiple hosts, using a network to exchange data.
Of course, the better the network, the better performances. User should ensure to use the available interconnect if one if available.

Install first dask and needed dependencies:

```
pip3 install "dask[complete]"
```

Then, lets create first a simple sleep code:

```python
import dask
from dask.distributed import Client, LocalCluster
import time
import os

def costly_simulation(list_param):
    print("Hello I am " + str(os.getpid()) + " and I am son of " + str(os.getppid()))
    time.sleep(4)
    return list_param * 2

if __name__ == "__main__":

    client = Client('localhost:8786')

    input_array = [1] * 10

    futures = []
    for parameters in input_array:
        future = client.submit(costly_simulation, parameters, pure=False)
        futures.append(future)

    results = client.gather(futures)
    print(results[:])
```

This very simple example will run a synthetic costly simulation (simulated by a 4s sleep).
Note that we added the `pure=False` parameter. Dask is smart enough to detect that entry values are the same, and so will run the task only once here (we could use random numbers too to prevent that behavior).

Lets create the dask cluster. We will need 3 ssh terminals: 1 for launching the python code, 1 to run the dask scheduler, and 1 to run the dask worker.

Open a first terminal on the cluster, using port redirection on 8787 port (`-L 8787:localhost:8787`).
Then, in this terminal, launch dask-scheduler:

```
dask-scheduler
```

And let it run in this terminal. Note that from now, in your local web browser, you can get the dask cluster web interface at http://localhost:8787 .

Now, in a second terminal, ssh on the cluster without any port redirection, and start a worker.
We will ask for now a 1 process 1 thread worker:

```
dask-worker --nworkers 1 --nthreads 1 localhost:8786
```

Note that now, in the dask-scheduler terminal, you can see in the logs that the worker registered to the scheduler. Also, in the web interface, you can now see the worker.

In a third terminal, launch the example program now:

```
time python3 dask_sleep.py
```

And note the total time: 40s.

Increase now the number of process and threads on the worker. Kill the worker in its shell with 2 Ctrl+C, and relaunch it with the following parameters:

```
dask-worker --nworkers 4 --nthreads 2 localhost:8786
```

So now, we will have 4 process of 2 threads each.

Restart the program, and get the new execution time. Also have a look in the dashboard. You can observe here that 8 tasks were run in a first pass, and then 2 were run alone in a second pass (8 + 2 = 10). Time was also significantly reduced.

You can also see during simulation resources usage in the dashboard. It is interesting to see how dask optimize tasks too. Lets now make the time random, and increase the number of tasks.

```python
import dask
from dask.distributed import Client, LocalCluster
import time
import os
import random

def costly_simulation(list_param):
    time.sleep(random.random())
    return list_param * 2

if __name__ == "__main__":

    client = Client('localhost:8786')

    input_array = [1] * 200

    futures = []
    for parameters in input_array:
        future = client.submit(costly_simulation, parameters, pure=False)
        futures.append(future)

    results = client.gather(futures)
    print(results[:])
```

Run now this job, and watch execution inside the dashboard. You can see on different tabs how dask schedule tasks and worker crunches them. Don't hesitate to relaunch the tasks multiple time to see how it run inside the dashboard.

Lets use now the dask arrays, which are numpy arrays, but that live into the daskc luster (so distributed memory and calculations !!).

Use the following example:

```python
import dask
from dask.distributed import Client

import dask.array as da

if __name__ == "__main__":

    x = da.random.random((10000, 10000), chunks=(1000, 1000))

    client = Client('localhost:8786')

    y = x + x.T
    z = y[::2, 5000:].mean(axis=1)
    print(z.compute())
```

You can note that once the array as been created, we can use numpy syntax on it as usual, which is very useful. However, we used the power of the full cluster to achieve the calculation.

Launch this program, and at the same time, monitor the output inside the dask scheduler dashboard, in status tab. You can see the whole calculation occurring.

More documentation is available at https://examples.dask.org/array.html .

Dask is a powerful tool, that has the capacity to run both locally and distributed, allowing codes to be run on any platforms.

## Do it yourself

Take some time now to manipulate all these parallel languages. Design a test case, and develop it in the language of your choice.
