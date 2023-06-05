### 3.4. Computational resources management

The **job scheduler** is the conductor of computational resources of the cluster.

A **job** is a small script, that contains instructions on how to execute the calculation program, and that also contains information for to the job scheduler (required job duration, how much resources are needed, etc.).
When a user ask the job scheduler to execute a **job**, which is call **submitting a job**, the job enter **jobs queue**.
The job scheduler is then in charge of finding free computational resources depending of the needs of the job, then launching the job and monitoring it during its execution. Note that the job scheduler is in charge of managing all jobs to ensure maximum usage of computational resources, which is why sometime, the job scheduler will put some jobs on hold for a long time in a queue, to wait for free resources.
In return, after user has submitted a job, the job scheduler will provide user a **job ID** to allow following job state in the jobs queue and during its execution.